CREATE TABLE students (
    student_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    age INT,
    category VARCHAR(50),
    state_of_residence VARCHAR(100),
    annual_family_income NUMERIC(12, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE student_preferences (
    preference_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(student_id) ON DELETE CASCADE,
    preferred_fields TEXT[],
    preferred_locations TEXT[],
    career_interest_statement TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE student_marks (
    mark_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(student_id) ON DELETE CASCADE,
    qualifying_degree VARCHAR(100) NOT NULL,
    overall_percentage NUMERIC(5, 2) NOT NULL,
    graduation_year INT NOT NULL
);

CREATE TABLE exams (
    exam_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_code VARCHAR(50) UNIQUE NOT NULL,
    exam_name VARCHAR(255) NOT NULL,
    description TEXT,
    official_url VARCHAR(500),
    conducting_body VARCHAR(255),
    exam_level VARCHAR(20),
    application_fee VARCHAR(100),
    embedding_vector vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE exam_schedules (
    schedule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_id UUID REFERENCES exams(exam_id) ON DELETE CASCADE,
    application_start_date DATE,
    application_end_date DATE,
    exam_date DATE,
    academic_year INT NOT NULL
);

CREATE TABLE eligibility_rules (
    rule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_id UUID REFERENCES exams(exam_id) ON DELETE CASCADE,
    max_age INT,
    min_qualifying_percentage NUMERIC(5, 2),
    required_degree VARCHAR(100),
    max_family_income NUMERIC(12, 2)
);

CREATE TABLE recommendation_cache (
    cache_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(student_id) ON DELETE CASCADE,
    exam_id UUID REFERENCES exams(exam_id) ON DELETE CASCADE,
    deterministic_eligible BOOLEAN NOT NULL,
    semantic_match_score NUMERIC(5, 4),
    composite_score NUMERIC(5, 2),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, exam_id)
);

CREATE TABLE scraping_sources (
    source_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_name VARCHAR(255) NOT NULL,
    target_url VARCHAR(500) NOT NULL,
    cron_expression VARCHAR(50) DEFAULT '0 0 * * *',
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE raw_staging_payloads (
    payload_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID REFERENCES scraping_sources(source_id) ON DELETE CASCADE,
    raw_html_or_json TEXT NOT NULL,
    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_processed BOOLEAN DEFAULT FALSE
);

CREATE TABLE ingestion_anomaly_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payload_id UUID REFERENCES raw_staging_payloads(payload_id) ON DELETE CASCADE,
    error_code VARCHAR(100) NOT NULL,
    missing_fields TEXT[],
    logged_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE scholarships (
    scholarship_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    provider_name VARCHAR(255),
    max_amount NUMERIC(12, 2),
    max_income_limit NUMERIC(12, 2)
);

CREATE TABLE scholarship_exam_mappings (
    mapping_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scholarship_id UUID REFERENCES scholarships(scholarship_id) ON DELETE CASCADE,
    exam_id UUID REFERENCES exams(exam_id) ON DELETE CASCADE
);

CREATE TABLE questionnaire_responses (
    response_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(student_id) ON DELETE CASCADE,
    answers JSONB NOT NULL,
    derived_statement TEXT,
    derived_fields TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rec_cache_student ON recommendation_cache (student_id);
CREATE INDEX idx_exam_schedules_exam ON exam_schedules (exam_id);
