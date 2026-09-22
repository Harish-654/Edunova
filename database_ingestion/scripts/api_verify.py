"""End-to-end API smoke test.

Registers a throwaway student, builds a full profile, computes matches and
exercises the catalog / scholarship / ingestion endpoints. Requires the API
running on a base URL (default http://localhost:8001/api/v1).

Usage:
    ../.venv/bin/python scripts/api_verify.py [BASE_URL]
"""

import sys
import time

import httpx

try:
    BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001/api/v1"
except IndexError:
    BASE = "http://localhost:8001/api/v1"

FAILED = 0
student_id = None
top_exam_id = None


def check(name: str, cond: bool, extra: str = "") -> None:
    global FAILED
    if cond:
        print(f"  PASS  {name}")
    else:
        FAILED += 1
        print(f"  FAIL  {name}  {extra}")
        if extra:
            pass
    return cond


def main() -> None:
    global student_id, top_exam_id
    client = httpx.Client(base_url=BASE, timeout=60)

    r = client.get("/health")
    check("health", r.status_code == 200)

    # --- create a unique student so the test is re-runnable ---
    r = client.post(
        "/auth/register",
        json={
            "full_name": "Priya Sharma",
            "email": f"priya.{int(time.time())}@example.com",
            "password": "secret123",
            "age": 18,
            "category": "General",
            "state_of_residence": "Maharashtra",
            "annual_family_income": 600000,
        },
    )
    ok = r.status_code == 201 and r.json().get("access_token")
    if check("register", ok, r.text[:200]):
        student_id = r.json()["user"]["student_id"]
        print(f"      registered student {student_id}")

    # --- profile ---
    r = client.put(
        f"/students/{student_id}/marks",
        json={
            "qualifying_degree": "12th",
            "overall_percentage": 88.5,
            "graduation_year": 2026,
        },
    )
    check("update marks", r.status_code == 200, r.text[:200])

    r = client.put(
        f"/students/{student_id}/preferences",
        json={
            "preferred_fields": ["Engineering", "Robotics"],
            "preferred_locations": ["Pune"],
            "career_interest_statement": (
                "I studied physics chemistry maths and want to join a B.Tech "
                "in robotics and AI engineering after class 12."
            ),
        },
    )
    check("update preferences", r.status_code == 200, r.text[:200])

    # --- catalog ---
    r = client.get("/exams")
    ok = r.status_code == 200 and r.json().get("count", 0) >= 10
    if check("exam catalog", ok, r.text[:200]):
        data = r.json()["data"]
        levels = sorted({e["exam_level"] for e in data if e.get("exam_level")})
        print(f"      catalog count={len(data)} levels={levels}")

    # --- match engine ---
    r = client.post(f"/match/student/{student_id}/compute")
    ok = r.status_code == 200 and len(r.json()["results"]) >= 10
    if check("match compute", ok, r.text[:200]):
        results = r.json()["results"]
        eligible = [x for x in results if x["deterministic_eligible"]]
        top = results[0]
        top_exam_id = top["exam"]["exam_id"]
        print(
            f"      eligible={len(eligible)}/{len(results)} top='{top['exam']['exam_name'][:40]}' "
            f"composite={top['composite_score']}"
        )
        assert top_exam_id

    r = client.get(f"/match/student/{student_id}/recommendations")
    check("recommendations read", r.status_code == 200, r.text[:200])

    # --- scholarships for the top match ---
    r = client.get(f"/scholarships/exam/{top_exam_id}")
    ok = r.status_code == 200 and isinstance(r.json(), list)
    if check("scholarships for top exam", ok, r.text[:200]):
        print(f"      scholarships for top exam: {len(r.json())}")

    # --- ingestion audit trail ---
    r = client.get("/ingestion/anomalies")
    check("ingestion anomalies", r.status_code == 200, r.text[:200])

    print()
    print("ALL CHECKS PASSED" if not FAILED else f"{FAILED} CHECKS FAILED")
    sys.exit(0 if not FAILED else 1)


if __name__ == "__main__":
    main()