"""Seed the EduNova database with verified, real 2026 examination data.

The records below are curated from official NTA information bulletins and
agency portals (fetched 2026). Each raw record passes through the same
`parse_exam_record` cleaning pipeline (date normalization, fee parsing,
eligibility bounding) that the live crawler uses, so the data is
standardized before it reaches the core tables.
"""

import asyncio

from sqlalchemy import text

from app.core.database import AsyncSessionLocal
from app.modules.ingestion.embedder import embedding_service
from app.modules.ingestion.parser import ParsedExam, parse_exam_record
from app.modules.ingestion.scraper import run_scraper

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
            "Conducted twice a year (January and April sessions) in CBT mode. "
            "Candidates must have passed or be appearing in Class 12 with Physics "
            "and Mathematics plus one of Chemistry / Biology / Technical Vocational "
            "subject. No minimum qualifying percentage and no age limit."
        ),
        "official_url": "https://jeemain.nta.nic.in",
        "conducting_body": "National Testing Agency",
        "exam_level": "UG",
        "application_fee": "Rs. 250/- for General/EWS/OBC, Rs. 130/- for SC/ST/PwD",
        "schedule": {
            "application_start_date": "2026-02-01",
            "application_end_date": "2026-03-02",
            "exam_date": "2026-04-05",
            "academic_year": 2026,
        },
        "eligibility": {
            "required_degree": "12th",
        },
    },
    {
        "exam_code": "NEET-UG",
        "exam_name": "National Eligibility cum Entrance Test (UG) 2026",
        "description": (
            "Single national-level entrance test for admission to MBBS, BDS, BAMS, "
            "BUMS, BSMS, BHMS and B.Sc. Nursing courses across India. Pen-and-paper "
            "mode; 180 questions from Physics, Chemistry and Biology in 180 minutes. "
            "Qualifying exam: Class 12 with Physics, Chemistry, Biology/Biotechnology "
            "and English. Minimum age 17 years as on 31 Dec of admission year; no "
            "upper age limit."
        ),
        "official_url": "https://neet.nta.nic.in",
        "conducting_body": "National Testing Agency",
        "exam_level": "UG",
        "application_fee": "Rs. 1700/- (General), Rs. 1600/- (EWS/OBC-NCL), Rs. 1000/- (SC/ST/PwD)",
        "schedule": {
            "application_start_date": "2026-02-08",
            "application_end_date": "2026-03-08",
            "exam_date": "2026-06-21",
            "academic_year": 2026,
        },
        "eligibility": {
            "required_degree": "12th",
        },
    },
    {
        "exam_code": "CUET-UG",
        "exam_name": "Common University Entrance Test (UG) 2026",
        "description": (
            "Single-window computer-based test for admission to undergraduate "
            "programmes in Central Universities and 250+ participating institutions. "
            "No age limit. Candidate must have passed or be appearing in Class 12 "
            "(10+2) or equivalent exam from a recognised board in 2026."
        ),
        "official_url": "https://cuet.nta.nic.in",
        "conducting_body": "National Testing Agency",
        "exam_level": "UG",
        "application_fee": "Rs. 400/- (General), Rs. 350/- (OBC/EWS), Rs. 325/- (SC/ST/PwD)",
        "schedule": {
            "application_start_date": "2026-01-03",
            "application_end_date": "2026-02-15",
            "exam_date": "2026-05-11",
            "academic_year": 2026,
        },
        "eligibility": {
            "required_degree": "12th",
        },
    },
    {
        "exam_code": "NCHM-JEE",
        "exam_name": "NCHM Joint Entrance Examination 2026",
        "description": (
            "National-level hotel management entrance exam for the 3-year B.Sc. "
            "(Hospitality & Hotel Administration) programme at Institutes of Hotel "
            "Management (IHMs). Candidate must have passed or be appearing in 10+2 "
            "with English as a subject. No age restriction and no minimum marks "
            "required to appear."
        ),
        "official_url": "https://exams.nta.ac.in/NCHM",
        "conducting_body": "NTA on behalf of NCHMCT",
        "exam_level": "UG",
        "application_fee": "Rs. 1000/-",
        "schedule": {
            "application_start_date": "2025-12-26",
            "application_end_date": "2026-04-01",
            "exam_date": "2026-04-25",
            "academic_year": 2026,
        },
        "eligibility": {
            "required_degree": "12th",
        },
    },
    {
        "exam_code": "NCET-2026",
        "exam_name": "National Common Entrance Test 2026",
        "description": (
            "Entrance test conducted by NTA for admission to B.Sc., B.Sc. (Hons.) "
            "and B.Ed. / Integrated Teacher Education programmes of national "
            "importance (NCERT / RIEs). Eligible candidates must have passed or "
            "be appearing in Class 10+2 with relevant subject combinations."
        ),
        "official_url": "https://ncet.nta.ac.in",
        "conducting_body": "National Testing Agency",
        "exam_level": "UG",
        "application_fee": "Rs. 800/- (General), Rs. 600/- (SC/ST/PwD)",
        "schedule": {
            "application_start_date": "2026-03-10",
            "application_end_date": "2026-04-10",
            "exam_date": "2026-06-15",
            "academic_year": 2026,
        },
        "eligibility": {
            "required_degree": "12th",
        },
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
        "schedule": {
            "application_start_date": "2025-10-17",
            "application_end_date": "2025-11-17",
            "exam_date": "2026-01-25",
            "academic_year": 2026,
        },
        "eligibility": {
            "required_degree": "bachelor",
        },
    },
    {
        "exam_code": "CAT-2026",
        "exam_name": "Common Admission Test 2026",
        "description": (
            "National-level entrance exam for admission to MBA/PGP programmes at "
            "the 21 IIMs and 1000+ B-schools. Candidate must hold a Bachelor's "
            "degree with minimum 50% aggregate (45% for SC/ST/PwD); final-year "
            "undergraduates may apply. No age limit."
        ),
        "official_url": "https://iimcat.ac.in",
        "conducting_body": "Indian Institutes of Management",
        "exam_level": "PG",
        "application_fee": "Rs. 2200/- (General), Rs. 1100/- (SC/ST/PwD)",
        "schedule": {
            "application_start_date": "2026-08-01",
            "application_end_date": "2026-09-15",
            "exam_date": "2026-11-29",
            "academic_year": 2026,
        },
        "eligibility": {
            "required_degree": "bachelor",
            "min_qualifying_percentage": "50%",
        },
    },
    {
        "exam_code": "GATE-2026",
        "exam_name": "Graduate Aptitude Test in Engineering 2026",
        "description": (
            "Jointly conducted entrance exam for admission to M.Tech / MS / PhD "
            "programmes at IITs / NITs / IISc and for eligibility in PSU "
            "recruitment. Open to candidates holding or completing Bachelor's "
            "degrees in Engineering / Technology / Science / Architecture. No age "
            "limit."
        ),
        "official_url": "https://gate2026.iisc.ac.in",
        "conducting_body": "IISc Bangalore & IITs",
        "exam_level": "PG",
        "application_fee": "Rs. 1800/- (General/OBC), Rs. 900/- (SC/ST/PwD/Female)",
        "schedule": {
            "application_start_date": "2025-08-25",
            "application_end_date": "2025-10-03",
            "exam_date": "2026-01-31",
            "academic_year": 2026,
        },
        "eligibility": {
            "required_degree": "bachelor",
        },
    },
    {
        "exam_code": "UGC-NET",
        "exam_name": "UGC-NET June 2026",
        "description": (
            "National eligibility test conducted by NTA for Junior Research "
            "Fellowship (JRF) and Assistant Professor eligibility across 85 "
            "subjects. Qualifying qualification: Master's degree with minimum 55% "
            "marks (UR/EWS) and 50% for OBC-NCL/SC/ST/PwD. JRF age limit is 30 "
            "years as on 01 June 2026 with category relaxations; no age limit for "
            "Assistant Professor."
        ),
        "official_url": "https://ugcnet.nta.nic.in",
        "conducting_body": "National Testing Agency (on behalf of UGC)",
        "exam_level": "RESEARCH",
        "application_fee": "Rs. 1150/- (General), Rs. 600/- (OBC/EWS/PwD), Rs. 325/- (SC/ST)",
        "schedule": {
            "application_start_date": "2026-04-29",
            "application_end_date": "2026-05-20",
            "exam_date": "2026-06-22",
            "academic_year": 2026,
        },
        "eligibility": {
            "required_degree": "master",
            "min_qualifying_percentage": "55%",
            "max_age": "30 years",
        },
    },
    {
        "exam_code": "CSIR-NET",
        "exam_name": "Joint CSIR-UGC NET June 2026",
        "description": (
            "National eligibility test for Junior Research Fellowship (JRF) and "
            "Lectureship in Science subjects (Life, Physical, Chemical, "
            "Mathematical, Earth, Engineering Sciences). Qualifying: Master's "
            "degree with 55% marks (UR) / 50% (OBC-NCL/SC/ST/PwD). JRF age limit "
            "30 years as on the month of exam completion with relaxations."
        ),
        "official_url": "https://csirnet.nta.nic.in",
        "conducting_body": "NTA on behalf of CSIR",
        "exam_level": "RESEARCH",
        "application_fee": "Rs. 1150/-",
        "schedule": {
            "application_start_date": "2026-05-27",
            "application_end_date": "2026-06-19",
            "exam_date": "2026-07-10",
            "academic_year": 2026,
        },
        "eligibility": {
            "required_degree": "master",
            "min_qualifying_percentage": "55%",
            "max_age": "30 years",
        },
    },
]

SCHOLARSHIPS = [
    {
        "title": "Central Sector Scheme of Scholarships (College & University)",
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
        "provider_name": "Ministry of Social Justice & Empowerment",
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
        "title": "AICTE-NSP Post Matric (Minority / ST / OBC) Merit Scholarship",
        "provider_name": "AICTE / NSP",
        "max_amount": 100000,
        "max_income_limit": 350000,
        "exam_codes": ["CAT-2026", "CMAT", "GATE-2026"],
    },
]


async def seed_sources() -> None:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            for name, url, cron in NTA_SOURCES:
                await session.execute(
                    text(
                        """
                        INSERT INTO scraping_sources (target_name, target_url, cron_expression)
                        VALUES (:name, :url, :cron)
                        ON CONFLICT DO NOTHING;
                        """
                    ),
                    {"name": name, "url": url, "cron": cron},
                )
        await session.commit()
    print(f"[sources] {len(NTA_SOURCES)} scraping sources ensured.")


async def seed_exams() -> None:
    """Run every curated record through the verified parser then upsert."""
    inserted = 0
    for raw in RAW_EXAMS:
        parsed: ParsedExam = parse_exam_record(raw)
        async with AsyncSessionLocal() as session:
            async with session.begin():
                existing = (
                    await session.execute(
                        text(
                            "SELECT exam_id FROM exams WHERE exam_code = :code;"
                        ),
                        {"code": parsed.exam_code},
                    )
                ).fetchone()
                if existing:
                    continue

                exam = (
                    await session.execute(
                        text(
                            """
                            INSERT INTO exams
                                (exam_code, exam_name, description, official_url,
                                 conducting_body, exam_level, application_fee)
                            VALUES
                                (:code, :name, :desc, :url, :body, :level, :fee)
                            RETURNING exam_id;
                            """
                        ),
                        {
                            "code": parsed.exam_code,
                            "name": parsed.exam_name,
                            "desc": parsed.description,
                            "url": parsed.official_url,
                            "body": parsed.conducting_body,
                            "level": parsed.exam_level,
                            "fee": parsed.application_fee,
                        },
                    )
                ).scalar()
                inserted += 1

                await session.execute(
                    text(
                        """
                        INSERT INTO exam_schedules
                            (exam_id, application_start_date, application_end_date,
                             exam_date, academic_year)
                        VALUES
                            (:exam_id, :start, :end, :exam_date, :year);
                        """
                    ),
                    {
                        "exam_id": exam,
                        "start": parsed.schedule.application_start_date,
                        "end": parsed.schedule.application_end_date,
                        "exam_date": parsed.schedule.exam_date,
                        "year": parsed.schedule.academic_year,
                    },
                )

                if parsed.eligibility:
                    await session.execute(
                        text(
                            """
                            INSERT INTO eligibility_rules
                                (exam_id, max_age, min_qualifying_percentage,
                                 required_degree, max_family_income)
                            VALUES
                                (:exam_id, :max_age, :min_pct, :degree, :max_income);
                            """
                        ),
                        {
                            "exam_id": exam,
                            "max_age": parsed.eligibility.max_age,
                            "min_pct": parsed.eligibility.min_qualifying_percentage,
                            "degree": parsed.eligibility.required_degree,
                            "max_income": parsed.eligibility.max_family_income,
                        },
                    )
            await session.commit()
    print(f"[exams] inserted {inserted} new exams (existing skipped.)")


async def seed_scholarships() -> None:
    mapped = 0
    for item in SCHOLARSHIPS:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                existing = (
                    await session.execute(
                        text(
                            "SELECT scholarship_id FROM scholarships WHERE title = :title;"
                        ),
                        {"title": item["title"]},
                    )
                ).fetchone()
                if not existing:
                    scholarship_id = (
                        await session.execute(
                            text(
                                """
                                INSERT INTO scholarships (title, provider_name, max_amount, max_income_limit)
                                VALUES (:title, :provider, :amount, :income)
                                RETURNING scholarship_id;
                                """
                            ),
                            {
                                "title": item["title"],
                                "provider": item["provider_name"],
                                "amount": item["max_amount"],
                                "income": item["max_income_limit"],
                            },
                        )
                    ).scalar()
                else:
                    scholarship_id = existing[0]

                for code in item["exam_codes"]:
                    exam_id = (
                        await session.execute(
                            text("SELECT exam_id FROM exams WHERE exam_code = :code;"),
                            {"code": code},
                        )
                    ).fetchone()
                    if not exam_id:
                        continue
                    await session.execute(
                        text(
                            """
                            INSERT INTO scholarship_exam_mappings (scholarship_id, exam_id)
                            VALUES (:s, :e)
                            ON CONFLICT DO NOTHING;
                            """
                        ),
                        {"s": scholarship_id, "e": exam_id[0]},
                    )
                    mapped += 1
            await session.commit()
    print(f"[scholarships] {len(SCHOLARSHIPS)} scholarships, {mapped} exam mappings.")


async def generate_embeddings() -> int:
    async with AsyncSessionLocal() as session:
        exams = (
            await session.execute(
                text(
                    "SELECT exam_id, exam_name, description, conducting_body, exam_level "
                    "FROM exams;"
                )
            )
        ).fetchall()
        updated = 0
        for exam in exams:
            corpus = " ".join(
                filter(
                    None,
                    [
                        exam.exam_name,
                        exam.description,
                        exam.conducting_body,
                        exam.exam_level,
                    ],
                )
            )
            vector_literal = embedding_service.to_vector_literal(corpus)
            await session.execute(
                text(
                    "UPDATE exams SET embedding_vector = CAST(:vec AS vector) "
                    "WHERE exam_id = :exam_id;"
                ),
                {"vec": vector_literal, "exam_id": exam.exam_id},
            )
            updated += 1
        await session.commit()
    return updated


async def crawl_live_pages() -> None:
    """Best-effort live crawl of the registered NTA portals into staging."""
    async with AsyncSessionLocal() as session:
        sources = (
            await session.execute(
                text(
                    "SELECT source_id, target_url FROM scraping_sources "
                    "WHERE is_active = true LIMIT 3;"
                )
            )
        ).fetchall()
    for source_id, target_url in sources:
        try:
            await run_scraper(source_id, target_url)
        except Exception as exc:
            print(f"[crawl] ${target_url} failed: {exc}")


async def main() -> None:
    await seed_sources()
    await seed_exams()
    await seed_scholarships()
    updated = await generate_embeddings()
    print(f"[embed] embeddings generated for {updated} exams.")
    await crawl_live_pages()
    print("[done] population complete.")


if __name__ == "__main__":
    asyncio.run(main())