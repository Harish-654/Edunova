DEGREE_RANK = {"10th": 0, "12th": 1, "bachelor": 2, "master": 3, "research": 4}

DEGREE_ALIASES = {
    "10th": "10th",
    "class 10": "10th",
    "matric": "10th",
    "secondary": "10th",
    "12th": "12th",
    "class 12": "12th",
    "10+2": "12th",
    "higher secondary": "12th",
    "intermediate": "12th",
    "senior secondary": "12th",
    "bachelor": "bachelor",
    "bachelors": "bachelor",
    "bachelor's": "bachelor",
    "graduation": "bachelor",
    "graduate": "bachelor",
    "b.tech": "bachelor",
    "btech": "bachelor",
    "b.e": "bachelor",
    "bsc": "bachelor",
    "b.sc": "bachelor",
    "ba": "bachelor",
    "b.com": "bachelor",
    "undergraduate": "bachelor",
    "master": "master",
    "masters": "master",
    "master's": "master",
    "postgraduate": "master",
    "m.tech": "master",
    "mtech": "master",
    "msc": "master",
    "m.sc": "master",
    "mba": "master",
    "ma": "master",
    "research": "research",
    "phd": "research",
    "ph.d": "research",
    "doctorate": "research",
}


def normalize_degree(value: str | None) -> str | None:
    if not value:
        return None
    return DEGREE_ALIASES.get(value.strip().lower(), value.strip().lower())


def check_eligibility(
    rule,
    *,
    age: int | None,
    percentage: float | None,
    degree: str | None,
    family_income: float | None,
) -> list[str]:
    reasons: list[str] = []
    if rule is None:
        return reasons

    if rule.max_age is not None and age is not None and age > rule.max_age:
        reasons.append(f"Maximum age allowed is {rule.max_age} years.")
    if (
        rule.min_qualifying_percentage is not None
        and percentage is not None
        and percentage < float(rule.min_qualifying_percentage)
    ):
        reasons.append(
            f"Requires at least {float(rule.min_qualifying_percentage):g}% marks."
        )
    if rule.required_degree and degree:
        required = normalize_degree(rule.required_degree)
        have = normalize_degree(degree)
        if (
            required in DEGREE_RANK
            and have in DEGREE_RANK
            and DEGREE_RANK[have] < DEGREE_RANK[required]
        ):
            reasons.append(f"Requires a {rule.required_degree} degree.")
    if (
        rule.max_family_income is not None
        and family_income is not None
        and family_income > float(rule.max_family_income)
    ):
        reasons.append(f"Family income limit is Rs. {float(rule.max_family_income):,.0f}.")
    return reasons
