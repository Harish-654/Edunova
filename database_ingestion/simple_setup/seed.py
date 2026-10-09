#!/usr/bin/env python3
"""Simple database seeding - easy to understand and explain."""

import psycopg2
from datetime import date

DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'edunova_db',
    'user': 'edunova_user',
    'password': 'edunova_pass'
}

# Sample exams - just the key info
EXAMS = [
    {
        'code': 'JEE-MAIN',
        'name': 'Joint Entrance Examination (Main)',
        'description': 'Engineering entrance for B.E./B.Tech programs',
        'url': 'https://jeemain.nta.nic.in',
        'body': 'National Testing Agency',
        'level': 'UG',
        'fee': 'Rs. 250/-',
        'app_start': '2026-02-01',
        'app_end': '2026-03-02',
        'exam_date': '2026-04-05',
        'year': 2026,
        'required_degree': '12th',
    },
    {
        'code': 'NEET-UG',
        'name': 'NEET UG',
        'description': 'Medical entrance for MBBS/BDS',
        'url': 'https://neet.nta.nic.in',
        'body': 'National Testing Agency',
        'level': 'UG',
        'fee': 'Rs. 1700/-',
        'app_start': '2026-02-08',
        'app_end': '2026-03-08',
        'exam_date': '2026-06-21',
        'year': 2026,
        'required_degree': '12th',
    },
    {
        'code': 'CUET-UG',
        'name': 'CUET UG',
        'description': 'Common entrance for central universities',
        'url': 'https://cuet.nta.nic.in',
        'body': 'National Testing Agency',
        'level': 'UG',
        'fee': 'Rs. 400/-',
        'app_start': '2026-01-03',
        'app_end': '2026-02-15',
        'exam_date': '2026-05-11',
        'year': 2026,
        'required_degree': '12th',
    },
    {
        'code': 'CAT-2026',
        'name': 'Common Admission Test',
        'description': 'MBA entrance for IIMs',
        'url': 'https://iimcat.ac.in',
        'body': 'Indian Institutes of Management',
        'level': 'PG',
        'fee': 'Rs. 2200/-',
        'app_start': '2026-08-01',
        'app_end': '2026-09-15',
        'exam_date': '2026-11-29',
        'year': 2026,
        'required_degree': 'bachelor',
    },
    {
        'code': 'GATE-2026',
        'name': 'GATE',
        'description': 'Postgraduate engineering entrance',
        'url': 'https://gate2026.iisc.ac.in',
        'body': 'IISc Bangalore & IITs',
        'level': 'PG',
        'fee': 'Rs. 1800/-',
        'app_start': '2025-08-25',
        'app_end': '2025-10-03',
        'exam_date': '2026-01-31',
        'year': 2026,
        'required_degree': 'bachelor',
    },
]

def main():
    print("Connecting to database...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("Adding sample exams...")
        for exam in EXAMS:
            # Check if exam exists
            cur.execute("SELECT exam_id FROM exams WHERE exam_code = %s", (exam['code'],))
            if cur.fetchone():
                print(f"  {exam['code']} already exists, skipping")
                continue
            
            # Insert exam
            cur.execute("""
                INSERT INTO exams (exam_code, exam_name, description, official_url, conducting_body, exam_level, application_fee)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING exam_id
            """, (exam['code'], exam['name'], exam['description'], exam['url'], exam['body'], exam['level'], exam['fee']))
            exam_id = cur.fetchone()[0]
            
            # Insert schedule
            cur.execute("""
                INSERT INTO exam_schedules (exam_id, application_start_date, application_end_date, exam_date, academic_year)
                VALUES (%s, %s, %s, %s, %s)
            """, (exam_id, exam['app_start'], exam['app_end'], exam['exam_date'], exam['year']))
            
            # Insert eligibility
            cur.execute("""
                INSERT INTO eligibility_rules (exam_id, required_degree)
                VALUES (%s, %s)
            """, (exam_id, exam['required_degree']))
            
            print(f"  Added {exam['code']}")
        
        conn.commit()
        print("\nDone! Sample data added successfully.")
        
        # Show count
        cur.execute("SELECT count(*) FROM exams")
        print(f"Total exams in database: {cur.fetchone()[0]}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"ERROR: {e}")
        print("\nMake sure database is set up first: run setup.sh in simple_setup/")

if __name__ == '__main__':
    main()