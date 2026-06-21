from __future__ import annotations

import re


SECTION_ALIASES = {
    "personal": [
        "PERSÖNLICHE DATEN",
        "PERSOENLICHE DATEN",
        "PERSONAL DATA",
    ],
    "profile": [
        "PROFIL",
        "PROFILE",
    ],
    "skills": [
        "FÄHIGKEITEN",
        "FAEHIGKEITEN",
        "SKILLS",
        "PROGRAMMIERSPRACHEN",
        "PROGRAMMING LANGUAGES",
    ],
    "tools": [
        "TOOLS",
        "TECHNOLOGIEN",
        "TECHNOLOGIES",
    ],
    "work experience": [
        "BERUFSERFAHRUNG",
        "WORK EXPERIENCE",
        "EXPERIENCE",
    ],
    "education": [
        "AUSBILDUNG",
        "EDUCATION",
        "STUDIUM",
    ],
    "training": [
        "WEITERBILDUNG",
        "CERTIFICATIONS",
        "CERTIFICATES",
    ],
    "projects": [
        "PROJEKTE",
        "PROJECTS",
        "PROJECT",
    ],
    "languages": [
        "SPRACHEN",
        "LANGUAGES",
    ],
    "hobbies": [
        "HOBBYS",
        "HOBBIES",
    ],
}


SKIP_SECTIONS = {"personal", "hobbies"}


def clean_text(text: str) -> str:
    replacements = {
        "Win- dows": "Windows",
        "Micro soft": "Microsoft",
        "Soft ware": "Software",
        "Daten strukturen": "Datenstrukturen",
        "Maschi ne": "Maschine",
        "Program mier": "Programmier",
        "Ent wicklung": "Entwicklung",
        "Fehler analyse": "Fehleranalyse",
        "Team fähigkeit": "Teamfähigkeit",
        "Lern bereitschaft": "Lernbereitschaft",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def _heading_pattern() -> re.Pattern:
    headings = []
    for aliases in SECTION_ALIASES.values():
        headings.extend(aliases)

    escaped = [re.escape(heading) for heading in headings]

    return re.compile(
        r"\b(" + "|".join(escaped) + r")\b",
        flags=re.IGNORECASE,
    )


def _canonical_section(heading: str) -> str:
    heading_upper = heading.upper()

    for canonical, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            if heading_upper == alias.upper():
                return canonical

    return heading.lower()


def split_into_sections(text: str) -> list[tuple[str, str]]:
    text = clean_text(text)
    pattern = _heading_pattern()

    matches = list(pattern.finditer(text))

    if not matches:
        return [("general", text)]

    sections = []

    for index, match in enumerate(matches):
        heading = match.group(0)
        section_name = _canonical_section(heading)

        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)

        content = text[start:end].strip()

        if content:
            sections.append((section_name, content))

    return sections


def _split_long_section(section: str, content: str, chunk_size: int) -> list[str]:
    words = content.split()
    chunks = []
    current_words = []

    for word in words:
        candidate = " ".join(current_words + [word])

        if len(candidate) <= chunk_size:
            current_words.append(word)
        else:
            if current_words:
                chunks.append(f"SECTION: {section.upper()}\n" + " ".join(current_words))
            current_words = [word]

    if current_words:
        chunks.append(f"SECTION: {section.upper()}\n" + " ".join(current_words))

    return chunks


def chunk_text(text: str, chunk_size: int = 650, overlap: int = 0) -> list[str]:
    """
    Split the CV by semantic sections instead of raw character windows.
    This improves retrieval quality for education, projects, tools, and work experience.
    """

    sections = split_into_sections(text)

    chunks = []

    for section_name, content in sections:
        if section_name in SKIP_SECTIONS:
            continue

        content = clean_text(content)

        if not content:
            continue

        if len(content) <= chunk_size:
            chunks.append(f"SECTION: {section_name.upper()}\n{content}")
        else:
            chunks.extend(_split_long_section(section_name, content, chunk_size))

    return chunks
