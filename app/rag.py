from __future__ import annotations

import re

SECTION_ENDINGS = [
    "TECHNISCHE FÄHIGKEITEN",
    "TECHNISCHE FAHIGKEITEN",
    "FÄHIGKEITEN",
    "FAEHIGKEITEN",
    "SKILLS",
    "TOOLS",
    "SPRACHEN",
    "LANGUAGES",
    "BERUFSERFAHRUNG",
    "WORK EXPERIENCE",
    "AUSBILDUNG",
    "EDUCATION",
    "WEITERBILDUNG",
    "CERTIFICATIONS",
]



def _clean_text(text: str) -> str:
    replacements = {
        "\u00ad": "",
        "￾": "",
        "Win- dows": "Windows",
        "Micro soft": "Microsoft",
        "Soft ware": "Software",
        "Daten strukturen": "Datenstrukturen",
        "Maschi ne": "Maschine",
        "Long￾Term": "Long-Term",
        "effizien￾teren": "effizienteren",
        "Deep-Learning￾Modelle": "Deep-Learning-Modelle",
        "daten￾satzspezifischen": "datensatzspezifischen",
        "RM￾SProp": "RMSProp",
        "Rekon￾struktion": "Rekonstruktion",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def _detect_intent(question: str) -> str:
    q = question.lower()

    if any(word in q for word in ["project", "projects", "projekt", "projekte"]):
        return "projects"

    if any(word in q for word in ["tool", "tools", "technolog", "git", "docker", "excel", "power"]):
        return "tools"

    if any(word in q for word in ["education", "study", "studies", "degree", "university", "bachelor", "ausbildung", "studium"]):
        return "education"

    if any(word in q for word in ["work", "experience", "job", "employment", "berufserfahrung", "werkstudent"]):
        return "work"

    if any(word in q for word in ["language", "languages", "sprache", "sprachen", "german", "english", "deutsch", "englisch"]):
        return "languages"

    if any(word in q for word in ["skill", "skills", "fähigkeit", "fähigkeiten", "programming", "programmiersprachen"]):
        return "skills"

    return "general"


def _section_between(text: str, start_keywords: list[str], end_keywords: list[str]) -> str:
    text_upper = text.upper()

    start_positions = [
        text_upper.find(keyword.upper())
        for keyword in start_keywords
        if text_upper.find(keyword.upper()) != -1
    ]

    if not start_positions:
        return ""

    start = min(start_positions)

    end_candidates = [
        text_upper.find(keyword.upper(), start + 1)
        for keyword in end_keywords
        if text_upper.find(keyword.upper(), start + 1) != -1
    ]

    end = min(end_candidates) if end_candidates else len(text)

    return text[start:end].strip()


def _lines(text: str) -> list[str]:
    cleaned = _clean_text(text)
    result = []

    for line in cleaned.splitlines():
        line = line.strip(" •–-:\t ")

        if not line:
            continue

        if len(line) < 3:
            continue

        result.append(line)

    return result


def _format_answer(items: list[str], evidence: str | None = None) -> str:
    if not items:
        return (
            "I cannot answer this reliably from the uploaded CV. "
            "Try asking about work experience, education, projects, skills, tools, or languages."
        )

    unique_items = []
    seen = set()

    for item in items:
        item = _clean_text(item)
        normalized = item.lower()

        if normalized in seen:
            continue

        unique_items.append(item)
        seen.add(normalized)

    lines = ["Answer:", ""]

    for item in unique_items[:5]:
        lines.append(f"- {item}")

    if evidence:
        lines.append("")
        lines.append(f"Evidence: {evidence}")

    lines.append("Local mode: no API keys or external AI services used.")

    return "\n".join(lines)


def _answer_projects(full_text: str) -> str:
    section = _section_between(
        full_text,
        ["PROJEKTE", "PROJECTS"],
        SECTION_ENDINGS,
    )

    lines = _lines(section)

    projects = []

    detail_prefixes = [
        "entwicklung",
        "implementierung",
        "training",
        "optimierung",
        "analyse",
        "verbesserung",
        "datenpipeline",
        "evaluation",
        "unit testing",
        "gui-entwicklung",
        "erstellung",
        "anwendung",
    ]

    project_keywords = [
        "sparsetsf",
        "forecasting",
        "bachelorarbeit",
        "generative",
        "adversarial",
        "dcgan",
        "bigan",
        "kotlin",
        "card game",
        "software-praktikum",
        "fachprojekt",
        "azul",
        "kaboo",
    ]

    for line in lines:
        lower = line.lower()

        if lower in ["projekte", "projects"]:
            continue

        if any(lower.startswith(prefix) for prefix in detail_prefixes):
            continue

        if any(keyword in lower for keyword in project_keywords):
            projects.append(line)

    return _format_answer(projects, "projects section")


def _answer_tools(full_text: str) -> str:
    section = _section_between(
        full_text,
        ["FÄHIGKEITEN", "FAEHIGKEITEN", "SKILLS"],
        ["PROFIL", "PROFILE", "AUSBILDUNG", "EDUCATION"],
    )

    lines = _lines(section)

    tools = []
    current_group = None

    wanted_groups = {
        "Programmiersprachen": "Programming languages",
        "Tools und Technologien": "Tools and technologies",
        "Microsoft Tools": "Microsoft tools",
        "Software Engineering": "Software engineering",
    }

    collected = {
        "Programming languages": [],
        "Tools and technologies": [],
        "Microsoft tools": [],
        "Software engineering": [],
    }

    for line in lines:
        for raw_group, clean_group in wanted_groups.items():
            if raw_group.lower() in line.lower():
                current_group = clean_group
                possible_value = line.split(":", 1)[-1].strip()

                if possible_value and possible_value.lower() != raw_group.lower():
                    collected[current_group].append(possible_value)

                break
        else:
            if current_group and not any(
                stop in line.lower()
                for stop in ["persönliche stärken", "persoenliche stärken", "profil"]
            ):
                collected[current_group].append(line)

    for group, values in collected.items():
        if values:
            compact_values = ", ".join(values[:12])
            tools.append(f"{group}: {compact_values}")

    return _format_answer(tools, "FÄHIGKEITEN / tools section")


def _answer_education(full_text: str) -> str:
    section = _section_between(
        full_text,
        ["AUSBILDUNG", "EDUCATION"],
        ["PROJEKTE", "PROJECTS", "BERUFSERFAHRUNG", "WORK EXPERIENCE"],
    )

    lines = _lines(section)

    education_items = []

    for line in lines:
        lower = line.lower()

        if any(term in lower for term in ["bachelor", "tu dortmund", "schwerpunkte", "abitur", "gymnasium", "nebenfach"]):
            education_items.append(line)

    return _format_answer(education_items, "education section")


def _answer_work(full_text: str) -> str:
    section = _section_between(
        full_text,
        ["BERUFSERFAHRUNG", "WORK EXPERIENCE"],
        ["WEITERBILDUNG", "CERTIFICATIONS", "SPRACHEN", "LANGUAGES"],
    )

    lines = _lines(section)

    work_items = []

    for line in lines:
        lower = line.lower()

        if any(term in lower for term in ["werkstudent", "installation", "migration", "ticket", "sccm", "onboarding", "client", "windows"]):
            work_items.append(line)

    return _format_answer(work_items[:4], "work experience section")


def _answer_languages(full_text: str) -> str:
    section = _section_between(
        full_text,
        ["SPRACHEN", "LANGUAGES"],
        ["HOBBYS", "HOBBIES", "BERUFSERFAHRUNG", "WORK EXPERIENCE"],
    )

    lines = _lines(section)

    languages = [
        line for line in lines
        if any(term in line.lower() for term in ["deutsch", "englisch", "französisch", "arabisch", "german", "english", "french", "arabic"])
    ]

    return _format_answer(languages, "languages section")


def _fallback_from_chunks(retrieved_chunks: list[dict]) -> str:
    items = []

    for chunk in retrieved_chunks[:3]:
        text = chunk.get("text", "")
        text = re.sub(r"SECTION:\s*\w+", "", text, flags=re.IGNORECASE)
        chunk_lines = _lines(text)

        for line in chunk_lines:
            if len(line) <= 180:
                items.append(line)

            if len(items) >= 3:
                break

    return _format_answer(items, "retrieved semantic chunks")


def generate_answer(question: str, retrieved_chunks: list[dict], full_text: str = "") -> str:
    if not question or not question.strip():
        return "Please ask a question about the uploaded CV."

    if not full_text and not retrieved_chunks:
        return "Please upload a CV first, then ask a question."

    intent = _detect_intent(question)

    if full_text:
        if intent == "projects":
            return _answer_projects(full_text)

        if intent == "tools" or intent == "skills":
            return _answer_tools(full_text)

        if intent == "education":
            return _answer_education(full_text)

        if intent == "work":
            return _answer_work(full_text)

        if intent == "languages":
            return _answer_languages(full_text)

    return _fallback_from_chunks(retrieved_chunks)


def answer_question(question: str, retrieved_chunks: list[dict], full_text: str = "") -> str:
    return generate_answer(question, retrieved_chunks, full_text)
