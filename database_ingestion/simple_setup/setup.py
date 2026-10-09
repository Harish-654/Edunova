# Simple cross-platform database setup for Edunova
# Works on Windows, macOS, and Linux
# Just run: python setup.py

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Database config
DB_PORT = "5433"
DB_USER = "edunova_user"
DB_PASS = "edunova_pass"
DB_NAME = "edunova_db"

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / ".data" / "db"
SCHEMA_SQL = PROJECT_ROOT / "schema.sql"
LOG_FILE = DATA_DIR / "pg.log"

def find_tool(name):
    """Find a PostgreSQL tool in PATH."""
    tool = shutil.which(name)
    if not tool:
        # Windows adds .exe
        tool = shutil.which(name + ".exe")
    return tool

def run_cmd(cmd, check=True, capture=False):
    """Run a command."""
    print(f"  Running: {' '.join(str(c) for c in cmd)}")
    try:
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if check and result.returncode != 0:
                print(f"ERROR: {result.stderr}")
                sys.exit(1)
            return result
        else:
            result = subprocess.run(cmd)
            if check and result.returncode != 0:
                sys.exit(1)
            return result
    except Exception as e:
        if check:
            print(f"ERROR running command: {e}")
            sys.exit(1)
        return None

def main():
    print("Setting up Edunova database...")
    print()
    
    # Check for required tools
    initdb = find_tool("initdb")
    pg_ctl = find_tool("pg_ctl")
    psql = find_tool("psql")
    
    if not all([initdb, pg_ctl, psql]):
        print("ERROR: PostgreSQL tools not found in PATH.")
        print()
        print("Make sure PostgreSQL is installed and added to PATH:")
        print("  Linux: sudo apt install postgresql")
        print("  macOS: brew install postgresql")
        print("  Windows: Install from postgresql.org (check 'Add to PATH')")
        sys.exit(1)
    
    print(f"Found: initdb, pg_ctl, psql")
    
    # Create cluster if it doesn't exist
    if not DATA_DIR.exists():
        print(f"\nCreating database cluster at {DATA_DIR}")
        DATA_DIR.parent.mkdir(parents=True, exist_ok=True)
        run_cmd([initdb, "-D", DATA_DIR, "-A", "trust", "-U", "postgres", "--no-locale", "--encoding", "UTF8"])
        print("Cluster created.")
    else:
        print(f"\nCluster already exists at {DATA_DIR}")
    
    # Start cluster if not running
    status = run_cmd([pg_ctl, "-D", DATA_DIR, "status"], check=False, capture=True)
    if status.returncode != 0:
        print("\nStarting database on port", DB_PORT)
        run_cmd([pg_ctl, "-D", DATA_DIR, "-l", LOG_FILE, "-o", f"-p {DB_PORT}", "-w", "start"])
        print("Database started.")
    else:
        print("\nDatabase is already running.")
    
    # Create user and database
    print("\nCreating user and database...")
    run_cmd([
        psql, "-h", "localhost", "-p", DB_PORT, "-U", "postgres", "-d", "postgres",
        "-c", f"DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='{DB_USER}') THEN CREATE ROLE {DB_USER} LOGIN PASSWORD '{DB_PASS}'; END IF; END $$;"
    ])
    
    # Check if DB exists
    result = run_cmd([
        psql, "-h", "localhost", "-p", DB_PORT, "-U", "postgres", "-d", "postgres",
        "-tAc", f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}'"
    ], capture=True)
    
    if "1" not in result.stdout:
        run_cmd([
            psql, "-h", "localhost", "-p", DB_PORT, "-U", "postgres", "-d", "postgres",
            "-c", f"CREATE DATABASE {DB_NAME} OWNER {DB_USER}"
        ])
        print("Database created.")
    else:
        print("Database already exists.")
    
    # Try to enable pgvector
    print("\nSetting up pgvector...")
    vec_result = run_cmd([
        psql, "-h", "localhost", "-p", DB_PORT, "-U", "postgres", "-d", DB_NAME,
        "-c", "CREATE EXTENSION IF NOT EXISTS vector;"
    ], check=False)
    if vec_result.returncode == 0:
        print("pgvector enabled.")
    else:
        print("Note: pgvector not installed system-wide (optional)")
    
    # Load schema
    if SCHEMA_SQL.exists():
        print("\nLoading schema...")
        run_cmd([
            psql, "-h", "localhost", "-p", DB_PORT, "-U", DB_USER, "-d", DB_NAME,
            "-f", SCHEMA_SQL
        ])
        print("Schema loaded.")
    else:
        print(f"\nWARNING: Schema not found at {SCHEMA_SQL}")
    
    # Done
    print()
    print("=" * 40)
    print("SUCCESS! Database is ready.")
    print("=" * 40)
    print()
    print("Connection:")
    print(f"  psql -h localhost -p {DB_PORT} -U {DB_USER} -d {DB_NAME}")
    print(f"  Password: {DB_PASS}")
    print()

if __name__ == "__main__":
    main()