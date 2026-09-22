#!/usr/bin/env python3
"""Cross-platform PostgreSQL setup & management for EduNova.

Owns a project-local cluster in `.data/db` on port 5433 (never touches a
system postgres) and installs pgvector into it. Runs on Linux, macOS and
Windows with only the standard library; PostgreSQL binaries are located
automatically.

Commands:
    setup            full bootstrap (idempotent); --reset drops schema first
    start / stop     start / stop the cluster
    status           is the cluster running?
    psql [args...]   open a psql shell as edunova_user (extra args passed)
    reset            drop the 12 app tables and re-apply schema.sql
"""

from __future__ import annotations

import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / ".data" / "db"
PGVEC_DIR = ROOT / ".data" / "pgvector"
PGVEC_SQL = ROOT / "scripts" / "pgvector" / "vector--0.8.6.sql"
SCHEMA_SQL = ROOT / "schema.sql"
LOG_FILE = DATA_DIR / "pg.log"

PORT = "5433"
DB_USER = "edunova_user"
DB_PASS = "edunova_pass"
DB_NAME = "edunova_db"

PGVEC_VERSION = "0.8.6"
PGVEC_TARBALL = f"https://github.com/pgvector/pgvector/archive/refs/tags/v{PGVEC_VERSION}.tar.gz"
WIN_PGVEC_ZIP = (
    "https://github.com/andreiramani/pgvector_pgsql_windows/releases/download/"
    f"{PGVEC_VERSION}_{{major}}/vector.v{PGVEC_VERSION}-pg{{major}}.zip"
)
WIN_PG_DIRS = [rf"C:\Program Files\PostgreSQL\{m}" for m in range(18, 12, -1)]

IS_WINDOWS = platform.system() == "Windows"
PGSQL_EXT = ".dll" if IS_WINDOWS else ".so"


def say(msg: str) -> None:
    print(f"[edunova] {msg}")


def die(msg: str) -> None:
    print(f"[edunova] ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


# ------------------------------------------------------------------ tooling
def _windows_pg_bin() -> Path | None:
    """First existing ...\\PostgreSQL\\<ver>\\bin on a Windows box."""
    if not IS_WINDOWS:
        return None
    for d in WIN_PG_DIRS:
        if (Path(d) / "bin" / "psql.exe").exists():
            return Path(d) / "bin"
    return None


def find_pg_bin() -> Path:
    if not IS_WINDOWS:
        for name in ("pg_config", "initdb", "pg_ctl", "psql"):
            found = shutil.which(name)
            if found:
                return Path(found).parent
        die(
            "Could not find PostgreSQL binaries (pg_config, initdb, pg_ctl, psql).\n"
            "  Linux/macOS:  apt install postgresql   |   brew install postgresql@18\n"
            "  Windows:      install via https://www.enterprisedb.com/downloads/postgres-postgresql-downloads "
            "and make sure it is reachable on PATH."
        )
    wpath = _windows_pg_bin()
    if wpath:
        return wpath
    die(
        "Could not find a PostgreSQL install in C:\\Program Files\\PostgreSQL\\.\n"
        "Install PostgreSQL via the EDB installer, then re-run this script."
    )


def pg_major(bin_dir: Path) -> str:
    out = subprocess.run(
        [str(bin_dir / "pg_config"), "--version"],
        capture_output=True, text=True,
    ).stdout
    m = re.search(r"PostgreSQL (\d+)", out)
    if not m:
        die(f"Unexpected output from pg_config --version: {out!r}")
    return m.group(1)


def ensure_tools(bin_dir: Path) -> None:
    for name in ("initdb", "pg_ctl", "psql"):
        if not (bin_dir / (name + ".exe" if IS_WINDOWS else name)).exists():
            die(f"Required tool '{name}' not found in {bin_dir}")
    if IS_WINDOWS and not (bin_dir / ("pg_config.exe" if IS_WINDOWS else "pg_config")).exists():
        # pg_config is required for building; ignore if missing until build needed
        pass


def run(*args: str, **kw) -> subprocess.CompletedProcess:
    """Run a subprocess with the PG bin dir prepended to PATH."""
    env = dict(os.environ)
    env["PATH"] = str(_PG_BIN) + os.pathsep + env.get("PATH", "")
    kw.setdefault("text", True)
    return subprocess.run([str(a) for a in args], env=env, **kw)


def psql(db: str, user: str, *sql: str, **kw) -> subprocess.CompletedProcess:
    if len(sql) == 1 and "\n" not in sql[0] and " " not in sql[0]:
        pass  # allow a single bare statement like "<stdin>" via -c
    cmd = [_p("psql"), "-h", "localhost", "-p", PORT, "-U", user, "-d", db, "-X"]
    cmd += ["-v", "ON_ERROR_STOP=1"]
    cmd += ["-c", sql[0]] if len(sql) == 1 else ["-c", "".join(sql)]
    return subprocess.run(cmd, **kw)


def _p(name: str) -> Path:  # executable in the PG bin dir
    return _PG_BIN / (name + (".exe" if IS_WINDOWS else ""))


_PG_BIN = find_pg_bin()
ensure_tools(_PG_BIN)
_PG_MAJOR = pg_major(_PG_BIN)


# ------------------------------------------------------------------ cluster
def cluster_version() -> str | None:
    f = DATA_DIR / "PG_VERSION"
    return f.read_text().strip() if f.exists() else None


def cluster_running() -> bool:
    r = run(_p("pg_ctl"), "-D", DATA_DIR, "status", capture_output=True)
    return r.returncode == 0


def init_cluster() -> None:
    say("Initializing cluster at .data/db ...")
    DATA_DIR.parent.mkdir(parents=True, exist_ok=True)
    r = run(
        _p("initdb"), "-D", DATA_DIR, "-A", "trust", "-U", "postgres",
        "--no-locale", "--encoding", "UTF8",
    )
    if r.returncode != 0:
        die(f"initdb failed:\n{r.stderr}")


def start_cluster() -> None:
    if cluster_running():
        say("Cluster already running.")
        return
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    opts = f"-p {PORT}"
    if not IS_WINDOWS:
        opts += " -c unix_socket_directories=/tmp"
    say(f"Starting cluster on port {PORT} ...")
    r = run(_p("pg_ctl"), "-D", DATA_DIR, "-l", LOG_FILE, "-o", opts, "-w", "start")
    if r.returncode != 0:
        die(f"pg_ctl start failed:\n{r.stderr}")


def stop_cluster() -> None:
    if not cluster_running():
        say("Cluster is not running.")
        return
    run(_p("pg_ctl"), "-D", DATA_DIR, "-m", "fast", "-w", "stop")


def setup_roles_db() -> None:
    say("Ensuring roles + database ...")
    r = psql("postgres", "postgres", rf"""
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'postgres') THEN
    CREATE ROLE postgres LOGIN SUPERUSER;
  END IF;
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '{DB_USER}') THEN
    CREATE ROLE {DB_USER} LOGIN PASSWORD '{DB_PASS}';
  END IF;
END
$$;
""")
    if r.returncode != 0:
        die(f"role creation failed: {r.stderr}")
    exists = run(
        _p("psql"), "-h", "localhost", "-p", PORT, "-U", "postgres", "-d", "postgres",
        "-tAc", f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}'",
        capture_output=True,
    )
    if "1" not in exists.stdout:
        r = run(
            _p("psql"), "-h", "localhost", "-p", PORT, "-U", "postgres", "-d", "postgres",
            "-c", f"CREATE DATABASE {DB_NAME} OWNER {DB_USER}",
        )
        if r.returncode != 0:
            die(f"database creation failed: {r.stderr}")


# ------------------------------------------------------------------ pgvector
def _sql_one(col: str) -> str | None:
    r = run(_p("psql"), "-h", "localhost", "-p", PORT, "-U", DB_USER, "-d", DB_NAME,
            "-tAc", col, capture_output=True)
    return r.stdout.strip() if r.returncode == 0 else None


def vector_type_installed() -> bool:
    return _sql_one("SELECT 1 FROM pg_type WHERE typname='vector'") == "1"


def install_vector_via_extension() -> bool:
    r = run(_p("psql"), "-h", "localhost", "-p", PORT, "-U", "postgres", "-d", DB_NAME,
            "-v", "ON_ERROR_STOP=1", "-c", "CREATE EXTENSION IF NOT EXISTS vector")
    return r.returncode == 0


def download(url: str, dest: Path) -> None:
    say(f"  downloading {url}")
    tmp = dest.with_suffix(dest.suffix + ".part")
    try:
        with urllib.request.urlopen(url, timeout=180) as resp, open(tmp, "wb") as fh:
            shutil.copyfileobj(resp, fh)
    except Exception as e:
        die(f"download failed ({url}): {e}")
    tmp.replace(dest)


def build_pgvector_posix(lib_dest: Path, major: str) -> None:
    say("No pgvector found. Building v0.8.6 from source (one time)...")
    for tool in ("make", "cc"):
        if not shutil.which(tool):
            die(
                f"Missing build tool '{tool}'. Install it, or put a pgvector "
                "install reachable by `CREATE EXTENSION vector`, e.g.\n"
                "  Debian/Ubuntu: apt install build-essential postgresql-server-dev-" + major +
                "\n  macOS:        brew install gcc make  (then brew install pgvector)"
            )
    with tempfile.TemporaryDirectory() as tmp:
        src_dir = Path(tmp) / "pgvector"
        tgz = Path(tmp) / "pgvector.tgz"
        download(PGVEC_TARBALL, tgz)
        with tarfile.open(tgz) as t:
            t.extractall(tmp)
        # github tarball root is 'pgvector-<ref>'
        extracted = next(p for p in Path(tmp).iterdir() if p.is_dir() and p.name.startswith("pgvector"))
        log = (DATA_DIR / "pgvector-build.log")

        r = run("make", "-s", "-C", extracted, "PG_CONFIG", str(_p("pg_config")), capture_output=True)
        if r.returncode != 0:
            log.write_text(r.stdout + "\n" + r.stderr)
            die(f"make failed (log: {log}). Usually missing PG dev headers or a C compiler:\n{r.stderr[-800:]}")
        shutil.copy(extracted / "src" / "vector.so", lib_dest)
    say(f"  built -> {lib_dest}")


def acquire_pgvector_dll(lib_dest: Path, major: str) -> None:
    say("No pgvector found. Downloading prebuilt Windows DLL (one time)...")
    url = WIN_PGVEC_ZIP.format(major=major)
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / "vector.zip"
        download(url, zip_path)
        with zipfile.ZipFile(zip_path) as z:
            member = next(n for n in z.namelist() if n.replace("\\", "/").endswith("lib/vector.dll"))
            dst_bytes = z.read(member)
        lib_dest.write_bytes(dst_bytes)
    say(f"  downloaded -> {lib_dest}")


def ensure_pgvector() -> None:
    say("Ensuring pgvector ...")
    if vector_type_installed():
        say("  vector type already present.")
        return
    say("  attempting CREATE EXTENSION vector ...")
    if install_vector_via_extension():
        say("  extension installed from system pgvector.")
        return

    lib_dest = PGVEC_DIR / ("vector" + PGSQL_EXT)
    if not lib_dest.exists():
        if IS_WINDOWS:
            acquire_pgvector_dll(lib_dest, _PG_MAJOR)
        else:
            build_pgvector_posix(lib_dest, _PG_MAJOR)

    say("  installing vector functions into the cluster ...")
    base_path = str(lib_dest.with_suffix(""))
    if IS_WINDOWS:
        base_path = base_path.replace("\\", "/")
    PGVEC_DIR.mkdir(parents=True, exist_ok=True)
    install_sql = PGVEC_DIR / "vector_install.sql"
    install_sql.write_text(PGVEC_SQL.read_text().replace("MODULE_PATHNAME", base_path))
    r = run(_p("psql"), "-h", "localhost", "-p", PORT, "-U", "postgres", "-d", DB_NAME,
            "-q", "-v", "ON_ERROR_STOP=1", "-f", install_sql)
    if r.returncode != 0:
        die(f"vector install failed:\n{r.stderr[-800:]}")
    if not vector_type_installed():
        die("vector type still missing after install.")


# ------------------------------------------------------------------ schema
APP_TABLES = [
    "scholarship_exam_mappings", "scholarships", "ingestion_anomaly_logs",
    "raw_staging_payloads", "scraping_sources", "recommendation_cache",
    "eligibility_rules", "exam_schedules", "exams", "student_marks",
    "student_preferences", "students",
]


def table_exists(table: str) -> bool:
    return _sql_one(
        f"SELECT 1 FROM pg_tables WHERE schemaname='public' AND tablename='{table}'"
    ) == "1"


def apply_schema(reset: bool = False) -> None:
    if reset:
        say("--reset: dropping app tables ...")
        drops = " ".join(f"DROP TABLE IF EXISTS public.{t} CASCADE;" for t in APP_TABLES)
        r = run(_p("psql"), "-h", "localhost", "-p", PORT, "-U", DB_USER, "-d", DB_NAME,
                "-v", "ON_ERROR_STOP=1", "-q", "-c", drops)
        if r.returncode != 0:
            die(f"reset failed: {r.stderr}")
    if table_exists("exams"):
        say("Schema already applied (exams exists) — skipping.")
        return
    say("Applying schema.sql ...")
    r = run(_p("psql"), "-h", "localhost", "-p", PORT, "-U", DB_USER, "-d", DB_NAME,
            "-q", "-v", "ON_ERROR_STOP=1", "-f", SCHEMA_SQL)
    if r.returncode != 0:
        die(f"schema apply failed:\n{r.stderr[-800:]}")


# ------------------------------------------------------------------ CLI
def cmd_psql(extra: list[str]) -> None:
    subprocess.run([str(_p("psql")), "-h", "localhost", "-p", PORT, "-U", DB_USER,
                    "-d", DB_NAME, *extra])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", nargs="?", default="setup",
                    help="setup|start|stop|status|psql|reset")
    ap.add_argument("--reset", action="store_true", help="(with setup) drop & re-apply schema")
    ap.add_argument("extra", nargs=argparse.REMAINDER, help="psql extra args")
    args = ap.parse_args()

    say(f"PostgreSQL tools: PG {_PG_MAJOR} ({_PG_BIN})")

    if args.command == "setup":
        if cluster_version() is None:
            init_cluster()
        else:
            say(f"Cluster exists (.data/db, PG {cluster_version()})")
        start_cluster()
        setup_roles_db()
        ensure_pgvector()
        apply_schema(reset=args.reset)
        say(f"Done. Connect: psql -h localhost -p {PORT} -U {DB_USER} -d {DB_NAME}")
        say("Next: cp backend/.env.example backend/.env  &&  pip install -r backend/requirements.txt")
        say("Then seed data:  python backend/scripts/populate.py")
    elif args.command == "start":
        if cluster_version() is None:
            init_cluster()
        start_cluster()
    elif args.command == "stop":
        stop_cluster()
    elif args.command == "status":
        running = cluster_running()
        print(f"Cluster at {DATA_DIR}: {'RUNNING' if running else 'STOPPED'}")
        if running:
            print(f"Connect: psql -h localhost -p {PORT} -U {DB_USER} -d {DB_NAME}")
    elif args.command == "psql":
        cmd_psql(args.extra)
    elif args.command == "reset":
        if cluster_version() is None:
            die("No cluster yet. Run: db.py setup")
        start_cluster()
        apply_schema(reset=True)
        say("Schema reset complete (data wiped).")
    else:
        die(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()