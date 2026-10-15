import re

from bs4 import BeautifulSoup

DATE_PATTERN = re.compile(r"\b(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})\b")


def html_to_text(html: str) -> str:
    return BeautifulSoup(html, "html.parser").get_text(" ", strip=True)


def find_dates(text: str) -> list[str]:
    dates: list[str] = []
    for day, month, year in DATE_PATTERN.findall(text):
        if len(year) == 2:
            year = "20" + year
        dates.append(f"{year}-{int(month):02d}-{int(day):02d}")
    return dates


def parse_page(html: str) -> tuple[dict, list[str]]:
    text = html_to_text(html)
    dates = find_dates(text)
    fields: dict = {}
    if dates:
        fields["dates"] = dates
    if re.search(r"application|registration|apply", text, re.IGNORECASE):
        fields["has_application_text"] = True
    missing: list[str] = []
    if not dates:
        missing.append("dates")
    if "has_application_text" not in fields:
        missing.append("application_text")
    return fields, missing
