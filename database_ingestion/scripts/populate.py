#!/usr/bin/env python3
"""Seed the EduNova database with curated 2026 examination and scholarship data.

Self-contained: it talks to PostgreSQL directly with asyncpg and does not import
the backend application, so the database module can be set up on its own.
"""

import asyncio
import hashlib
import math
import re
from datetime import date

import asyncpg

DB = {
    "host": "localhost",
    "port": 5433,
    "database": "edunova_db",
    "user": "edunova_user",
    "password": "edunova_pass",
}

EMBEDDING_DIM = 1536

NTA_SOURCES = [
    ("NTA - JEE Main", "https://jeemain.nta.nic.in", "0 0 1 * *"),
    ("NTA - NEET UG", "https://neet.nta.nic.in", "0 0 1 * *"),
    ("NTA - CUET UG", "https://cuet.nta.nic.in", "0 0 1 * *"),
    ("NTA - UGC NET", "https://ugcnet.nta.nic.in", "0 0 1 * *"),
    ("NTA - CSIR NET", "https://csirnet.nta.nic.in", "0 0 1 * *"),
    ("NTA - CMAT", "https://cmat.nta.nic.in", "0 0 1 * *"),
    ("NTA - NCHM JEE", "https://exams.nta.ac.in/NCHM", "0 0 1 * *"),
    ("IISc - GATE 2026", "https://gate2026.iisc.ac.in", "0 0 1 * *"),
    ("IIM - CAT", "https://iimcat.ac.in", "0 0 1 * *"),
]

RAW_EXAMS = [
    {
        "exam_code": "JEE-MAIN",
        "exam_name": "Joint Entrance Examination (Main) 2026",
        "description": (
            "National-level engineering entrance exam for admission to B.E. / B.Tech "
            "(Paper 1), B.Arch (Paper 2A) and B.Planning (Paper 2B) programmes. "
            "Conducted twice a year (January and April sessions) in computer-based "
            "mode. Candidates must have passed or be appearing in Class 12 with "
            "Physics and Mathematics plus one of Chemistry, Biology or Technical "
            "Vocational subject. No minimum qualifying percentage and no age limit."
        ),
        "official_url": "https://jeemain.nta.nic.in",
        "conducting_body": "National Testing Agency",
        "exam_level": "UG",
        "application_fee": "Rs. 250/- for General/EWS/OBC, Rs. 130/- for SC/ST/PwD",
        "application_start_date": "2026-02-01",
        "application_end_date": "2026-03-02",
        "exam_date": "2026-04-05",
        "academic_year": 2026,
        "required_degree": "12th",
    },
    {
        "exam_code": "NEET-UG",
        "exam_name": "National Eligibility cum Entrance Test (UG) 2026",
        "description": (
            "Single national-level entrance test for admission to MBBS, BDS, BAMS, "
            "BUMS, BSMS, BHMS and B.Sc. Nursing courses across India. Pen-and-paper "
            "mode with 180 questions from Physics, Chemistry and Biology in 180 "
            "minutes. Qualifying exam: Class 12 with Physics, Chemistry, "
            "Biology/Biotechnology and English. Minimum age 17 years; no upper age "
            "limit."
        ),
        "official_url": "https://neet.nta.nic.in",
        "conducting_body": "National Testing Agency",
        "exam_level": "UG",
        "application_fee": "Rs. 1700/- (General), Rs. 1600/- (EWS/OBC-NCL), Rs. 1000/- (SC/ST/PwD)",
        "application_start_date": "2026-02-08",
        "application_end_date": "2026-03-08",
        "exam_date": "2026-06-21",
        "academic_year": 2026,
        "required_degree": "12th",
    },
    {
        "exam_code": "CUET-UG",
        "exam_name": "Common University Entrance Test (UG) 2026",
        "description": (
            "Single-window computer-based test for admission to undergraduate "
            "programmes in Central Universities and more than 250 participating "
            "institutions. No age limit. Candidate must have passed or be appearing "
            "in Class 12 (10+2) or equivalent from a recognised board in 2026."
        ),
        "official_url": "https://cuet.nta.nic.in",
        "conducting_body": "National Testing Agency",
        "exam_level": "UG",
        "application_fee": "Rs. 400/- (General), Rs. 350/- (OBC/EWS), Rs. 325/- (SC/ST/PwD)",
        "application_start_date": "2026-01-03",
        "application_end_date": "2026-02-15",
        "exam_date": "2026-05-11",
        "academic_year": 2026,
        "required_degree": "12th",
    },
    {
        "exam_code": "NCHM-JEE",
        "exam_name": "NCHM Joint Entrance Examination 2026",
        "description": (
            "National-level hotel management entrance exam for the 3-year B.Sc. "
            "(Hospitality and Hotel Administration) programme at Institutes of Hotel "
            "Management. Candidate must have passed or be appearing in 10+2 with "
            "English as a subject. No age restriction and no minimum marks required."
        ),
        "official_url": "https://exams.nta.ac.in/NCHM",
        "conducting_body": "NTA on behalf of NCHMCT",
        "exam_level": "UG",
        "application_fee": "Rs. 1000/-",
        "application_start_date": "2025-12-26",
        "application_end_date": "2026-04-01",
        "exam_date": "2026-04-25",
        "academic_year": 2026,
        "required_degree": "12th",
    },
    {
        "exam_code": "NCET-2026",
        "exam_name": "National Common Entrance Test 2026",
        "description": (
            "Entrance test conducted by NTA for admission to B.Sc., B.Sc. (Hons.) "
            "and B.Ed. / Integrated Teacher Education programmes of national "
            "importance. Eligible candidates must have passed or be appearing in "
            "Class 10+2 with relevant subject combinations."
        ),
        "official_url": "https://ncet.nta.ac.in",
        "conducting_body": "National Testing Agency",
        "exam_level": "UG",
        "application_fee": "Rs. 800/- (General), Rs. 600/- (SC/ST/PwD)",
        "application_start_date": "2026-03-10",
        "application_end_date": "2026-04-10",
        "exam_date": "2026-06-15",
        "academic_year": 2026,
        "required_degree": "12th",
    },
    {
        "exam_code": "CMAT",
        "exam_name": "Common Management Admission Test 2026",
        "description": (
            "National-level entrance exam for admission to management programmes "
            "(MBA/MMS) in AICTE-affiliated institutions. Candidate must hold a "
            "Bachelor's degree in any discipline; final-year students may also apply. "
            "No age restriction."
        ),
        "official_url": "https://cmat.nta.nic.in",
        "conducting_body": "National Testing Agency",
        "exam_level": "PG",
        "application_fee": "Rs. 2500/-",
        "application_start_date": "2025-10-17",
        "application_end_date": "2025-11-17",
        "exam_date": "2026-01-25",
        "academic_year": 2026,
        "required_degree": "bachelor",
    },
    {
        "exam_code": "CAT-2026",
        "exam_name": "Common Admission Test 2026",
        "description": (
            "National-level entrance exam for admission to MBA/PGP programmes at the "
            "21 IIMs and more than 1000 B-schools. Candidate must hold a Bachelor's "
            "degree with minimum 50% aggregate (45% for SC/ST/PwD); final-year "
            "undergraduates may apply. No age limit."
        ),
        "official_url": "https://iimcat.ac.in",
        "conducting_body": "Indian Institutes of Management",
        "exam_level": "PG",
        "application_fee": "Rs. 2200/- (General), Rs. 1100/- (SC/ST/PwD)",
        "application_start_date": "2026-08-01",
        "application_end_date": "2026-09-15",
        "exam_date": "2026-11-29",
        "academic_year": 2026,
        "required_degree": "bachelor",
        "min_qualifying_percentage": "50%",
    },
    {
        "exam_code": "GATE-2026",
        "exam_name": "Graduate Aptitude Test in Engineering 2026",
        "description": (
            "Jointly conducted entrance exam for admission to M.Tech / MS / PhD "
            "programmes at IITs, NITs and IISc, and for eligibility in PSU "
            "recruitment. Open to candidates holding or completing Bachelor's degrees "
            "in Engineering, Technology, Science or Architecture. No age limit."
        ),
        "official_url": "https://gate2026.iisc.ac.in",
        "conducting_body": "IISc Bangalore and IITs",
        "exam_level": "PG",
        "application_fee": "Rs. 1800/- (General/OBC), Rs. 900/- (SC/ST/PwD/Female)",
        "application_start_date": "2025-08-25",
        "application_end_date": "2025-10-03",
        "exam_date": "2026-01-31",
        "academic_year": 2026,
        "required_degree": "bachelor",
    },
    {
        "exam_code": "UGC-NET",
        "exam_name": "UGC-NET June 2026",
        "description": (
            "National eligibility test conducted by NTA for Junior Research "
            "Fellowship and Assistant Professor eligibility across 85 subjects. "
            "Qualifying qualification: Master's degree with minimum 55% marks and "
            "50% for reserved categories. JRF age limit is 30 years with category "
            "relaxations; no age limit for Assistant Professor."
        ),
        "official_url": "https://ugcnet.nta.nic.in",
        "conducting_body": "National Testing Agency (on behalf of UGC)",
        "exam_level": "RESEARCH",
        "application_fee": "Rs. 1150/- (General), Rs. 600/- (OBC/EWS/PwD), Rs. 325/- (SC/ST)",
        "application_start_date": "2026-04-29",
        "application_end_date": "2026-05-20",
        "exam_date": "2026-06-22",
        "academic_year": 2026,
        "required_degree": "master",
        "min_qualifying_percentage": "55%",
        "max_age": "30 years",
    },
    {
        "exam_code": "CSIR-NET",
        "exam_name": "Joint CSIR-UGC NET June 2026",
        "description": (
            "National eligibility test for Junior Research Fellowship and "
            "Lectureship in Science subjects including Life, Physical, Chemical, "
            "Mathematical, Earth and Engineering Sciences. Qualifying: Master's "
            "degree with 55% marks or 50% for reserved categories. JRF age limit 30 "
            "years with relaxations."
        ),
        "official_url": "https://csirnet.nta.nic.in",
        "conducting_body": "NTA on behalf of CSIR",
        "exam_level": "RESEARCH",
        "application_fee": "Rs. 1150/-",
        "application_start_date": "2026-05-27",
        "application_end_date": "2026-06-19",
        "exam_date": "2026-07-10",
        "academic_year": 2026,
        "required_degree": "master",
        "min_qualifying_percentage": "55%",
        "max_age": "30 years",
    },
]

SCHOLARSHIPS = [
    {
        "title": "Central Sector Scheme of Scholarships (College and University)",
        "provider_name": "Ministry of Education",
        "max_amount": 20000,
        "max_income_limit": 450000,
        "exam_codes": ["JEE-MAIN", "NEET-UG", "CUET-UG", "CAT-2026", "CMAT", "NCHM-JEE"],
    },
    {
        "title": "AICTE Pragati Scholarship for Girls (Technical Education)",
        "provider_name": "AICTE",
        "max_amount": 50000,
        "max_income_limit": 800000,
        "exam_codes": ["JEE-MAIN", "CUET-UG", "GATE-2026"],
    },
    {
        "title": "AICTE Saksham Scholarship for Differently-Abled",
        "provider_name": "AICTE",
        "max_amount": 50000,
        "max_income_limit": 800000,
        "exam_codes": ["JEE-MAIN", "GATE-2026", "CUET-UG"],
    },
    {
        "title": "National Post Matric Scholarship for SC Students",
        "provider_name": "Ministry of Social Justice and Empowerment",
        "max_amount": 100000,
        "max_income_limit": 250000,
        "exam_codes": ["JEE-MAIN", "NEET-UG", "CUET-UG", "NCHM-JEE", "CMAT"],
    },
    {
        "title": "Nationwide Education Scholarship Test (NEST)",
        "provider_name": "NEST Trust",
        "max_amount": 200000,
        "max_income_limit": None,
        "exam_codes": ["JEE-MAIN", "NEET-UG", "CUET-UG"],
    },
    {
        "title": "UGC NET JRF Fellowship",
        "provider_name": "University Grants Commission",
        "max_amount": 37000,
        "max_income_limit": None,
        "exam_codes": ["UGC-NET", "CSIR-NET"],
    },
    {
        "title": "AICTE-NSP Post Matric Merit Scholarship (Minority / ST / OBC)",
        "provider_name": "AICTE / NSP",
        "max_amount": 100000,
        "max_income_limit": 350000,
        "exam_codes": ["CAT-2026", "CMAT", "GATE-2026"],
    },
]


def embed(text):
    vector = [0.0] * EMBEDDING_DIM
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        digest = int(hashlib.blake2b(token.encode(), digest_size=8).hexdigest(), 16)
        vector[digest % EMBEDDING_DIM] += 1.0 if (digest >> 63) & 1 else -1.0
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0.0:
        return vector
    return [value / norm for value in vector]


def vector_literal(text):
    return "[" + ",".join(f"{value:.6f}" for value in embed(text)) + "]"


def first_number(value):
    if value is None:
        return None
    match = re.search(r"\d+(\.\d+)?", str(value))
    return match.group() if match else None


def first_int(value):
    number = first_number(value)
    return int(float(number)) if number is not None else None


def as_date(value):
    return date.fromisoformat(value) if value else None


async def seed_sources(conn):
    added = 0
    for name, url, cron in NTA_SOURCES:
        exists = await conn.fetchval(
            "SELECT 1 FROM scraping_sources WHERE target_url = $1", url
        )
        if not exists:
            await conn.execute(
                "INSERT INTO scraping_sources (target_name, target_url, cron_expression) "
                "VALUES ($1, $2, $3)",
                name,
                url,
                cron,
            )
            added += 1
    print(f"[sources] {added} new scraping sources added.")


async def seed_exams(conn):
    added = 0
    for raw in RAW_EXAMS:
        exists = await conn.fetchval(
            "SELECT 1 FROM exams WHERE exam_code = $1", raw["exam_code"]
        )
        if exists:
            continue
        exam_id = await conn.fetchval(
            "INSERT INTO exams (exam_code, exam_name, description, official_url, "
            "conducting_body, exam_level, application_fee) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING exam_id",
            raw["exam_code"],
            raw["exam_name"],
            raw["description"],
            raw["official_url"],
            raw["conducting_body"],
            raw["exam_level"],
            raw["application_fee"],
        )
        await conn.execute(
            "INSERT INTO exam_schedules (exam_id, application_start_date, "
            "application_end_date, exam_date, academic_year) VALUES ($1, $2, $3, $4, $5)",
            exam_id,
            as_date(raw["application_start_date"]),
            as_date(raw["application_end_date"]),
            as_date(raw["exam_date"]),
            raw["academic_year"],
        )
        await conn.execute(
            "INSERT INTO eligibility_rules (exam_id, max_age, min_qualifying_percentage, "
            "required_degree, max_family_income) VALUES ($1, $2, $3, $4, $5)",
            exam_id,
            first_int(raw.get("max_age")),
            float(first_number(raw.get("min_qualifying_percentage")))
            if raw.get("min_qualifying_percentage")
            else None,
            raw.get("required_degree"),
            raw.get("max_family_income"),
        )
        added += 1
    print(f"[exams] {added} new exams added (existing skipped).")


async def seed_scholarships(conn):
    mapped = 0
    for item in SCHOLARSHIPS:
        scholarship_id = await conn.fetchval(
            "SELECT scholarship_id FROM scholarships WHERE title = $1", item["title"]
        )
        if not scholarship_id:
            scholarship_id = await conn.fetchval(
                "INSERT INTO scholarships (title, provider_name, max_amount, max_income_limit) "
                "VALUES ($1, $2, $3, $4) RETURNING scholarship_id",
                item["title"],
                item["provider_name"],
                item["max_amount"],
                item["max_income_limit"],
            )
        for code in item["exam_codes"]:
            exam_id = await conn.fetchval(
                "SELECT exam_id FROM exams WHERE exam_code = $1", code
            )
            if not exam_id:
                continue
            exists = await conn.fetchval(
                "SELECT 1 FROM scholarship_exam_mappings "
                "WHERE scholarship_id = $1 AND exam_id = $2",
                scholarship_id,
                exam_id,
            )
            if not exists:
                await conn.execute(
                    "INSERT INTO scholarship_exam_mappings (scholarship_id, exam_id) "
                    "VALUES ($1, $2)",
                    scholarship_id,
                    exam_id,
                )
                mapped += 1
    print(f"[scholarships] {len(SCHOLARSHIPS)} scholarships, {mapped} new exam mappings.")


async def generate_embeddings(conn):
    exams = await conn.fetch(
        "SELECT exam_id, exam_name, description, conducting_body, exam_level FROM exams"
    )
    for exam in exams:
        corpus = " ".join(
            part
            for part in (
                exam["exam_name"],
                exam["description"],
                exam["conducting_body"],
                exam["exam_level"],
            )
            if part
        )
        await conn.execute(
            "UPDATE exams SET embedding_vector = $1::text::vector WHERE exam_id = $2",
            vector_literal(corpus),
            exam["exam_id"],
        )
    print(f"[embed] embeddings generated for {len(exams)} exams.")


async def main():
    conn = await asyncpg.connect(**DB)
    try:
        await seed_sources(conn)
        await seed_exams(conn)
        await seed_scholarships(conn)
        await generate_embeddings(conn)
    finally:
        await conn.close()
    print("[done] population complete.")


if __name__ == "__main__":
    asyncio.run(main())
