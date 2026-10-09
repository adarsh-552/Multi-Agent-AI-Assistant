"""Parsers for the backend's templated text outputs.

They only read what the model actually returned. Anything that can't be parsed
comes back as None/empty, and the UI then falls back to the raw text.
"""

import re

ATS_SUBS = [
    ("STRUCTURE SCORE", "Structure and organization", 20),
    ("SKILLS SCORE", "Skills clarity", 20),
    ("EXPERIENCE AND PROJECTS SCORE", "Experience and projects", 20),
    ("ACHIEVEMENTS SCORE", "Achievements and results", 15),
    ("CONTACT INFORMATION SCORE", "Contact information", 10),
    ("ATS CONTENT SCORE", "ATS-friendly content", 15),
]

ATS_HEADERS = ["OVERALL SCORE", "WHY THIS SCORE", "TOP IMPROVEMENTS"] + [h for h, _, _ in ATS_SUBS]

MATCH_HEADERS = [
    "JOB MATCH SCORE", "MATCHING SKILLS", "MISSING / RECOMMENDED SKILLS", "MATCHING EXPERIENCE",
    "EXPERIENCE GAPS", "ROLE SUITABILITY", "RESUME IMPROVEMENTS",
]

ADVISOR_HEADERS = [
    "DECISION", "MATCH LEVEL", "WHY", "MATCHING SKILLS", "MISSING IMPORTANT SKILLS",
    "TRANSFERABLE SKILLS", "CONCERNS", "RECOMMENDATION",
]


def _normalize(line):
    line = re.sub(r"[*#`_>]", "", line).strip()
    return re.sub(r"^\d+[.)]\s*", "", line)


def split_sections(text, headers):
    """Split text into {HEADER: body} using the template's own headers."""
    ordered = sorted(headers, key=len, reverse=True)
    sections, current, buffer = {}, None, []

    def flush():
        if current is not None:
            sections[current] = "\n".join(buffer).strip()

    for raw in (text or "").splitlines():
        line = _normalize(raw)
        upper = line.upper()
        hit = None
        for header in ordered:
            if upper.startswith(header):
                rest = upper[len(header):].strip()
                if rest == "" or rest.startswith(":"):
                    hit = header
                    break
        if hit:
            flush()
            current, buffer = hit, []
            remainder = line[len(hit):].lstrip().lstrip(":").strip()
            if remainder:
                buffer.append(remainder)
        elif current is not None:
            buffer.append(raw)
    flush()
    return sections


def parse_score(text, default_max=100):
    """Return (value, max) from text like '78/100', '85%' or '15 / 20'."""
    if not text:
        return None
    body = text.strip()
    if re.search(r"_{2,}\s*/", body):  # an unfilled template placeholder
        return None
    match = re.search(r"(\d{1,3}(?:\.\d+)?)\s*(?:/\s*(\d{1,3}))?\s*(%)?", body)
    if not match:
        return None
    value = float(match.group(1))
    if match.group(2):
        maximum = float(match.group(2))
    elif match.group(3):
        maximum = 100.0
    else:
        maximum = float(default_max)
    if maximum <= 0 or value < 0 or value > maximum:
        return None
    return value, maximum


def to_items(text):
    """Turn a bullet or paragraph block into a clean list of strings."""
    items = []
    for line in (text or "").splitlines():
        cleaned = re.sub(r"^\s*(?:[-*\u2022\u2013]+|\d+[.)])\s*", "", line).strip()
        cleaned = cleaned.strip("*_ ").strip()
        if cleaned and cleaned.lower() not in ("none", "n/a", "-"):
            items.append(cleaned)
    return items


def parse_ats(text):
    sections = split_sections(text, ATS_HEADERS)
    overall = parse_score(sections.get("OVERALL SCORE"), 100)
    subs = []
    for header, label, maximum in ATS_SUBS:
        parsed = parse_score(sections.get(header), maximum)
        if parsed:
            subs.append({"label": label, "value": parsed[0], "max": parsed[1]})
    return {
        "score": overall[0] if overall else None,
        "max": overall[1] if overall else 100,
        "subs": subs,
        "why": to_items(sections.get("WHY THIS SCORE")),
        "improvements": to_items(sections.get("TOP IMPROVEMENTS")),
    }


def parse_match(text):
    sections = split_sections(text, MATCH_HEADERS)
    score = parse_score(sections.get("JOB MATCH SCORE"), 100)
    return {
        "score": score[0] if score else None,
        "max": score[1] if score else 100,
        "matching_skills": to_items(sections.get("MATCHING SKILLS")),
        "missing_skills": to_items(sections.get("MISSING / RECOMMENDED SKILLS")),
        "matching_experience": to_items(sections.get("MATCHING EXPERIENCE")),
        "experience_gaps": to_items(sections.get("EXPERIENCE GAPS")),
        "suitability": sections.get("ROLE SUITABILITY", "").strip(),
        "improvements": to_items(sections.get("RESUME IMPROVEMENTS")),
    }


def parse_advisor(text):
    sections = split_sections(text, ADVISOR_HEADERS)
    decision_text = (sections.get("DECISION") or "").upper()
    decision = None
    if "NOT RECOMMENDED" in decision_text:
        decision = "NOT RECOMMENDED"
    elif "MAYBE" in decision_text:
        decision = "MAYBE"
    elif "APPLY" in decision_text:
        decision = "APPLY"
    level_text = (sections.get("MATCH LEVEL") or "").lower()
    level = next((w.capitalize() for w in ("high", "medium", "low") if w in level_text), None)
    return {
        "decision": decision,
        "level": level,
        "why": to_items(sections.get("WHY")),
        "matching_skills": to_items(sections.get("MATCHING SKILLS")),
        "missing_skills": to_items(sections.get("MISSING IMPORTANT SKILLS")),
        "transferable": to_items(sections.get("TRANSFERABLE SKILLS")),
        "concerns": to_items(sections.get("CONCERNS")),
        "recommendation": (sections.get("RECOMMENDATION") or "").strip(),
    }
