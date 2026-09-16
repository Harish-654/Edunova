"""Verified ingestion engine: parser & cleaner.

Turns raw scraped text / curated records into normalized, standardized
exam entities (dates in ISO format, numeric fee, bounded eligibility fields).

If mandatory fields are missing or malformed the record is flagged with
`error_code` + `missing_fields` and ingestion halts for that item
(returned as an `IngestionIssue` instead of mutating the database).
"""

import re
from dataclasses import dataclass, field
from datetime import date, datetime

from bs4 import BeautifulSoup

MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "oct": 10,
    "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}

DATE_PATTERNS = [
    (re.compile(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})"), "%d %m %Y"),  # 8 February 2026
    (re.compile(r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})"), "%d %m %Y"),  # 08/02/2026
    (re.compile(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})"), "%Y %m %d"),  # 2026-02-08
]

REQUIRED_FIELDS = ["exam_code", "exam_name"]


@dataclass
class ParsedSchedule:
    application_start_date: date | None = None
    application_end_date: date | None = None
    exam_date: date | None = None
    academic_year: int | None = None


@dataclass
class ParsedEligibility:
    max_age: int | None = None
    min_qualifying_percentage: float | None = None
    required_degree: str | None = None
    max_family_income: float | None = None


@dataclass
class ParsedExam:
    exam_code: str = ""
    exam_name: str = ""
    description: str = ""
    official_url: str = ""
    conducting_body: str = ""
    exam_level: str = ""
    application_fee: float | None = None
    schedule: ParsedSchedule = field(default_factory=ParsedSchedule)
    eligibility: ParsedEligibility = field(default_factory=ParsedEligibility)


@dataclass
class IngestionIssue:
    error_code: str
    missing_fields: list[str] = field(default_factory=list)
    detail: str = ""


class IngestionHalted(Exception):
    def __init__(self, error_code: str, missing_fields: list[str], detail: str = ""):
        self.error_code = error_code
        self.missing_fields = missing_fields
        self.detail = detail
        super().__init__(detail or error_code)


# ---------- cleaning primitives ----------

def html_to_text(raw_html: str) -> str:
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    return re.sub(r"\s+", " ", soup.get_text(" ", strip=True))


def normalize_date(value: str | None) -> date | None:
    if not value:
        return None
    value = value.strip().replace("st", "").replace("nd", "").replace("rd", "").replace("th", "")
    value = re.sub(r"\s+", " ", value)
    for pattern, fmt in DATE_PATTERNS:
        match = pattern.search(value)
        if not match:
            continue
        parts = list(match.groups())
        if fmt == "%d %m %Y" and parts[1].lower() in MONTHS:
            parts[1] = str(MONTHS[parts[1].lower()])
        try:
            return datetime.strptime(" ".join(parts), fmt).date()
        except ValueError:
            continue
    return None


def normalize_year(value: str | int | None) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    match = re.search(r"(20\d{2})", text)
    return int(match.group(1)) if match else None


def parse_fee(value: str | float | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value)
    text = re.sub(r"[^\d.]", "", text.split("/")[0])
    return float(text) if text else None


def parse_age_limit(value: str | int | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    match = re.search(r"(\d{2})\s*(?:years|yrs|yr|years of age)?", str(value), re.I)
    return int(match.group(1)) if match else None


def parse_percentage(value: str | float | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"(\d{1,3}(?:\.\d+)?)\s*%?", str(value))
    return float(match.group(1)) if match else None


def parse_income(value: str | float | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if match:
        amount = float(match.group(1))
        if "lakh" in text.lower() or "lac" in text.lower():
            amount *= 100_000
        elif "cror" in text.lower():
            amount *= 10_000_000
        return amount
    return None


# ---------- core parsing ----------

def parse_exam_record(raw: dict) -> ParsedExam:
    """Validate + normalize a raw exam dict into a ParsedExam (or raise)."""
    missing = [f for f in REQUIRED_FIELDS if not str(raw.get(f) or "").strip()]
    if missing:
        raise IngestionHalted("MISSING_MANDATORY_FIELD", missing)

    schedule_raw = raw.get("schedule", {}) or {}
    eligibility_raw = raw.get("eligibility", {}) or {}

    exam = ParsedExam(
        exam_code=str(raw["exam_code"]).strip().upper(),
        exam_name=str(raw["exam_name"]).strip(),
        description=str(raw.get("description") or "").strip(),
        official_url=str(raw.get("official_url") or "").strip(),
        conducting_body=str(raw.get("conducting_body") or "").strip(),
        exam_level=(str(raw.get("exam_level") or "").strip().upper()),
        application_fee=parse_fee(raw.get("application_fee")),
        schedule=ParsedSchedule(
            application_start_date=normalize_date(
                schedule_raw.get("application_start_date")
            ),
            application_end_date=normalize_date(schedule_raw.get("application_end_date")),
            exam_date=normalize_date(schedule_raw.get("exam_date")),
            academic_year=normalize_year(
                schedule_raw.get("academic_year") or raw.get("academic_year")
            ),
        ),
        eligibility=ParsedEligibility(
            max_age=parse_age_limit(eligibility_raw.get("max_age")),
            min_qualifying_percentage=parse_percentage(
                eligibility_raw.get("min_qualifying_percentage")
            ),
            required_degree=(
                str(eligibility_raw["required_degree"]).strip()
                if eligibility_raw.get("required_degree")
                else None
            ),
            max_family_income=parse_income(eligibility_raw.get("max_family_income")),
        ),
    )

    # Soft anomaly: year missing/invalid blocks scheduling only.
    if not exam.schedule.academic_year:
        raise IngestionHalted("MISSING_MANDATORY_FIELD", ["academic_year"])

    return exam