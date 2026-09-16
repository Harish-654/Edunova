-- EduNova schema (PostgreSQL)
-- NOTE: pgvector is pre-installed in this project-owned cluster
-- (type vector shipped via .data/pgvector/vector_install.sql).
-- CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Student Profiles & Demographics
CREATE TABLE students (
    student_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    age INT NOT NULL,
    category VARCHAR(50), -- E.g., General, OBC, SC, ST
    state_of_residence VARCHAR(100),
    annual_family_income NUMERIC(12, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Student Preferences
CREATE TABLE student_preferences (
    preference_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(student_id) ON DELETE CASCADE,
    preferred_fields TEXT[], -- E.g., ARRAY['Engineering', 'Robotics']
    preferred_locations TEXT[],
    career_interest_statement TEXT, -- Raw interest string used for vector generation
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Student Academic Records
CREATE TABLE student_marks (
    mark_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(student_id) ON DELETE CASCADE,
    qualifying_degree VARCHAR(100) NOT NULL, -- E.g., '12th', 'B.Tech'
    overall_percentage NUMERIC(5, 2) NOT NULL,
    graduation_year INT NOT NULL
);

-- 4. Exams Catalog (Enables pgvector extension for AI Matching)
CREATE TABLE exams (
    exam_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_code VARCHAR(50) UNIQUE NOT NULL,
    exam_name VARCHAR(255) NOT NULL,
    description TEXT,
    official_url VARCHAR(500),
    embedding_vector vector(1536), -- Vector representation for semantic matching
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Exam Schedules & Deadlines
CREATE TABLE exam_schedules (
    schedule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_id UUID REFERENCES exams(exam_id) ON DELETE CASCADE,
    application_start_date DATE,
    application_end_date DATE,
    exam_date DATE,
    academic_year INT NOT NULL
);

-- 6. Hard Eligibility Rules (Binary Filter Bounds)
CREATE TABLE eligibility_rules (
    rule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_id UUID REFERENCES exams(exam_id) ON DELETE CASCADE,
    max_age INT,
    min_qualifying_percentage NUMERIC(5, 2),
    required_degree VARCHAR(100),
    max_family_income NUMERIC(12, 2)
);

-- 7. Pre-computed Recommendation Cache
CREATE TABLE recommendation_cache (
    cache_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(student_id) ON DELETE CASCADE,
    exam_id UUID REFERENCES exams(exam_id) ON DELETE CASCADE,
    deterministic_eligible BOOLEAN NOT NULL, -- True if passed hard binary checks
    semantic_match_score NUMERIC(5, 4),      -- Cosine similarity output (0.0 to 1.0)
    composite_score NUMERIC(5, 2),           -- Final weighted percentage match
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, exam_id)
);

-- 8. Web Scraper Sources & Schedule Rules
CREATE TABLE scraping_sources (
    source_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_name VARCHAR(255) NOT NULL,
    target_url VARCHAR(500) NOT NULL,
    cron_expression VARCHAR(50) DEFAULT '0 0 * * *', -- Scrape frequency
    is_active BOOLEAN DEFAULT TRUE
);

-- 9. Raw Scraped Payload Staging Area
CREATE TABLE raw_staging_payloads (
    payload_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID REFERENCES scraping_sources(source_id) ON DELETE CASCADE,
    raw_html_or_json TEXT NOT NULL,
    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_processed BOOLEAN DEFAULT FALSE
);

-- 10. Data Anomaly & Audit Logs
CREATE TABLE ingestion_anomaly_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payload_id UUID REFERENCES raw_staging_payloads(payload_id) ON DELETE CASCADE,
    error_code VARCHAR(100) NOT NULL,
    missing_fields TEXT[],
    logged_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 11. Scholarships & Financial Aid
CREATE TABLE scholarships (
    scholarship_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    provider_name VARCHAR(255),
    max_amount NUMERIC(12, 2),
    max_income_limit NUMERIC(12, 2)
);

-- 12. Exam-to-Scholarship Junction Table
CREATE TABLE scholarship_exam_mappings (
    mapping_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scholarship_id UUID REFERENCES scholarships(scholarship_id) ON DELETE CASCADE,
    exam_id UUID REFERENCES exams(exam_id) ON DELETE CASCADE
);