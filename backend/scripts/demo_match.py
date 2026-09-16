"""Demo: show the EduNova match engine discriminating by career interest.

Registers four students with deliberately different career goals, computes
recommendations for each, and prints a tidy table of top matches so the
semantic matcher's behavior is easy to see. Requires the API running on
BASE_URL.
"""

import sys
import time

import httpx

try:
    BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001/api/v1"
except IndexError:
    BASE = "http://localhost:8001/api/v1"

PROFILES = [
    {
        "tag": "Medical aspirant",
        "email_slug": "med",
        "age": 18,
        "degree": "12th",
        "marks": 92.0,
        "income": 400000,
        "fields": ["Medicine"],
        "statement": ("I finished class 12 with biology and chemistry and "
                      "want to become a doctor. My dream is a government "
                      "medical seat in an MBBS program."),
    },
    {
        "tag": "Engineering UG",
        "email_slug": "eng",
        "age": 18,
        "degree": "12th",
        "marks": 88.5,
        "income": 600000,
        "fields": ["Engineering", "Robotics"],
        "statement": ("I studied physics, chemistry and maths in class 12 and "
                      "want to join a B.Tech in robotics and AI engineering."),
    },
    {
        "tag": "Hospitality UG",
        "email_slug": "hotel",
        "age": 18,
        "degree": "12th",
        "marks": 81.0,
        "income": 550000,
        "fields": ["Hospitality"],
        "statement": ("I love hotels, travel and meeting people. I want to "
                      "study hotel administration and catering."),
    },
    {
        "tag": "PG research",
        "email_slug": "research",
        "age": 23,
        "degree": "Master",
        "marks": 76.0,
        "income": 450000,
        "fields": ["Research"],
        "statement": ("I completed my masters and want a research career, "
                      "becoming a professor. I need a research fellowship."),
    },
]


def main() -> None:
    client = httpx.Client(base_url=BASE, timeout=60)
    created = []

    for prof in PROFILES:
        email = f"{prof['email_slug']}.{int(time.time())}@demo.com"
        r = client.post(
            "/auth/register",
            json={
                "full_name": prof["tag"],
                "email": email,
                "password": "secret123",
                "age": prof["age"],
                "category": "General",
                "state_of_residence": "Maharashtra",
                "annual_family_income": prof["income"],
            },
        )
        if r.status_code not in (200, 201):
            print(f"  !! register failed for {prof['tag']}: {r.status_code} {r.text}")
            continue
        sid = r.json()["user"]["student_id"]
        created.append(sid)

        client.put(
            f"/students/{sid}/marks",
            json={
                "qualifying_degree": prof["degree"],
                "overall_percentage": prof["marks"],
                "graduation_year": 2026,
            },
        )
        client.put(
            f"/students/{sid}/preferences",
            json={
                "preferred_fields": prof["fields"],
                "preferred_locations": ["Pune"],
                "career_interest_statement": prof["statement"],
            },
        )
        r = client.post(f"/match/student/{sid}/compute")
        if r.status_code != 200:
            print(f"  !! compute failed for {prof['tag']}: {r.text}")
            continue

        results = r.json()["results"]
        eligible = [x for x in results if x["deterministic_eligible"]]
        top3 = sorted(eligible, key=lambda x: x["composite_score"], reverse=True)[:3]

        print("=" * 78)
        print(f"  {prof['tag']}  (degree={prof['degree']}, %={prof['marks']}, income={prof['income']})")
        print(f"  interest: {prof['statement']}")
        print(f"  -> {len(eligible)}/{len(results)} exams eligible")
        print(f"  {'EXAM':<48}{'SEMANTIC':>10}{'COMPOSITE':>11}")
        if not top3:
            print("  (no eligible exams)")
        for x in top3:
            name = x["exam"]["exam_name"][:46]
            print(f"  {name:<48}{x['semantic_match_score']:>10.3f}{x['composite_score']:>11.2f}")

    print("=" * 78)
    print("Demo done; created demo students were kept in the DB (emails end in @demo.com).")


if __name__ == "__main__":
    main()