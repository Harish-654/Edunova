export interface Student {
  student_id: string;
  full_name: string;
  email: string;
  role: string;
  age?: number | null;
  category?: string | null;
  state_of_residence?: string | null;
  annual_family_income?: number | null;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  student: Student;
}

export interface QuestionOption {
  value: string;
  label: string;
  fields?: string[];
}

export interface Question {
  id: string;
  prompt: string;
  type: string;
  options?: QuestionOption[];
}

export interface QuestionnaireResult {
  derived_statement: string;
  derived_fields: string[];
  career_interest_statement: string;
  profile_updated: boolean;
}

export interface Exam {
  exam_id: string;
  exam_code: string;
  exam_name: string;
  description?: string | null;
  official_url?: string | null;
  conducting_body?: string | null;
  exam_level?: string | null;
  application_fee?: string | null;
}

export interface Schedule {
  schedule_id: string;
  application_start_date?: string | null;
  application_end_date?: string | null;
  exam_date?: string | null;
  academic_year: number;
}

export interface Eligibility {
  max_age?: number | null;
  min_qualifying_percentage?: number | null;
  required_degree?: string | null;
  max_family_income?: number | null;
}

export interface ExamDetail extends Exam {
  schedules: Schedule[];
  eligibility?: Eligibility | null;
}

export interface Scholarship {
  scholarship_id: string;
  title: string;
  provider_name?: string | null;
  max_amount?: number | null;
  max_income_limit?: number | null;
}

export interface Recommendation {
  exam_id: string;
  exam_code: string;
  exam_name: string;
  exam_level?: string | null;
  conducting_body?: string | null;
  eligible: boolean;
  semantic_score: number;
  composite_score: number;
  matched_fields: string[];
  reasons: string[];
}

export interface Source {
  source_id: string;
  target_name: string;
  target_url: string;
  cron_expression?: string | null;
  is_active: boolean;
}

export interface Payload {
  payload_id: string;
  source_id: string;
  fetched_at: string;
  is_processed: boolean;
}

export interface Anomaly {
  log_id: string;
  payload_id: string;
  error_code: string;
  missing_fields?: string[] | null;
  logged_at: string;
}

export interface CrawlResult {
  source_id: string;
  target_name: string;
  fetched: boolean;
  missing_fields: string[];
  error?: string | null;
}

export interface Overview {
  students: number;
  exams: number;
  scholarships: number;
  sources: number;
  payloads: number;
  anomalies: number;
}
