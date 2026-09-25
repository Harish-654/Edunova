from dataclasses import dataclass, field

from app.models.entities import EligibilityRule, Student, StudentMark


@dataclass
class EligibilityBreakdown:
    age: bool | None = None
    percentage: bool | None = None
    degree: bool | None = None
    income: bool | None = None
    detail: list[str] = field(default_factory=list)

    @property
    def eligible(self) -> bool:
        return all(
            check is not False
            for check in (self.age, self.percentage, self.degree, self.income)
        )


DEGREE_ALIASES = {
    "12th": [
        "12th",
        "class 12",
        "class xii",
        "10+2",
        "10+2 or equivalent",
        "senior secondary",
        "intermediate",
        "pre-university",
        "higher secondary",
    ],
    "bachelor": [
        "bachelor",
        "b.tech",
        "btech",
        "be",
        "b.e.",
        "b.sc",
        "bsc",
        "b com",
        "ba",
        "undergraduate",
        "bachelor's",
        "degree",
    ],
    "master": [
        "master",
        "m.tech",
        "mtech",
        "m.sc",
        "msc",
        "m.com",
        "ma",
        "mba",
        "postgraduate",
        "post-graduate",
        "pg",
        "master's",
    ],
}


def _degree_matches(required: str | None, obtained: str | None) -> bool:
    if not required:
        return True
    if not obtained:
        return False

    required_norm = required.strip().lower()
    obtained_norm = obtained.strip().lower()
    allowed = DEGREE_ALIASES.get(required_norm, [required_norm])
    return any(token in obtained_norm for token in allowed)


def evaluate_eligibility(
    student: Student, marks: StudentMark | None, rule: EligibilityRule
) -> EligibilityBreakdown:
    breakdown = EligibilityBreakdown()

    if rule.max_age is not None:
        breakdown.age = student.age <= rule.max_age
        breakdown.detail.append(
            f"Age {student.age} <= {rule.max_age}"
            if breakdown.age
            else f"Age {student.age} > max {rule.max_age}"
        )

    if rule.min_qualifying_percentage is not None:
        score = marks.overall_percentage if marks else None
        breakdown.percentage = (
            score is not None
            and float(score) >= float(rule.min_qualifying_percentage)
        )
        breakdown.detail.append(
            f"Marks {score or 'N/A'} >= {rule.min_qualifying_percentage}"
        )

    if rule.required_degree:
        obtained_degree = marks.qualifying_degree if marks else None
        breakdown.degree = _degree_matches(rule.required_degree, obtained_degree)
        breakdown.detail.append(
            f"Degree '{obtained_degree or 'N/A'}' vs required "
            f"'{rule.required_degree}'"
        )

    if rule.max_family_income is not None:
        income = student.annual_family_income
        breakdown.income = (
            income is not None and float(income) <= float(rule.max_family_income)
        )
        breakdown.detail.append(
            f"Income {income or 'N/A'} <= {rule.max_family_income}"
        )

    return breakdown