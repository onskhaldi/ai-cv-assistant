from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np
from sentence_transformers import SentenceTransformer


SECTION_QUERY_TERMS = {
    "WORK EXPERIENCE": {
        "work", "experience", "job", "employment", "berufserfahrung", "werkstudent", "internship"
    },
    "EDUCATION": {
        "education", "study", "studies", "degree", "university", "bachelor", "master", "ausbildung", "studium"
    },
    "PROJECTS": {
        "project", "projects", "projekt", "projekte", "portfolio", "thesis", "bachelorarbeit"
    },
    "TOOLS": {
        "tools", "technologies", "technology", "technologien", "werkzeuge", "git", "docker", "excel", "power"
    },
    "SKILLS": {
        "skills", "fähigkeiten", "programming", "programmiersprachen", "python", "sql", "java"
    },
    "LANGUAGES": {
        "languages", "language", "sprachen", "sprache", "german", "english", "deutsch", "englisch"
    },
}


QUERY_EXPANSIONS = {
    "WORK EXPERIENCE": "work experience berufserfahrung werkstudent internship job support tickets installation migration",
    "EDUCATION": "education ausbildung studium university bachelor master degree abitur",
    "PROJECTS": "projects projekte projekt thesis bachelorarbeit software application implementation github model tests",
    "TOOLS": "tools technologien technologies git github gitlab mysql power bi docker sccm usm excel teams outlook",
    "SKILLS": "skills fähigkeiten programming programmiersprachen python sql java kotlin machine learning",
    "LANGUAGES": "languages sprachen deutsch englisch german english french arabic",
}


@dataclass
class SearchResult:
    text: str
    score: float
    chunk_id: int


def _tokens(text: str) -> set[str]:
    return {
        token.lower()
        for token in re.findall(r"[A-Za-zÄÖÜäöüß0-9+#]+", text)
        if len(token) > 1
    }


def _section_name(text: str) -> str:
    first_line = text.splitlines()[0] if text.splitlines() else ""

    if first_line.upper().startswith("SECTION:"):
        return first_line.replace("SECTION:", "").strip().upper()

    return "GENERAL"


def _detect_expected_section(query: str) -> str | None:
    query_lower = query.lower()

    best_section = None
    best_score = 0

    for section, terms in SECTION_QUERY_TERMS.items():
        score = sum(1 for term in terms if term in query_lower)

        if score > best_score:
            best_score = score
            best_section = section

    return best_section


class VectorStore:
    """
    In-memory semantic vector store using local multilingual embeddings.
    No API keys. No external LLM calls.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.chunks: list[str] = []
        self.embeddings: np.ndarray | None = None

    def build_index(self, chunks: list[str]) -> None:
        clean_chunks = [chunk.strip() for chunk in chunks if chunk and chunk.strip()]
        self.chunks = clean_chunks

        if not clean_chunks:
            self.embeddings = None
            return

        self.embeddings = self.model.encode(
            clean_chunks,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

    def search(self, query: str, top_k: int = 12) -> list[dict]:
        if self.embeddings is None or not self.chunks:
            return []

        if not query or not query.strip():
            return []

        expected_section = _detect_expected_section(query)
        expanded_query = query.strip()

        if expected_section in QUERY_EXPANSIONS:
            expanded_query = f"{query.strip()} {QUERY_EXPANSIONS[expected_section]}"

        query_embedding = self.model.encode(
            [expanded_query],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]

        semantic_scores = np.dot(self.embeddings, query_embedding)
        query_tokens = _tokens(expanded_query)

        final_scores = []

        for index, chunk in enumerate(self.chunks):
            section = _section_name(chunk)
            chunk_tokens = _tokens(chunk)

            keyword_overlap = len(query_tokens.intersection(chunk_tokens))
            keyword_bonus = min(0.25, keyword_overlap * 0.025)

            section_bonus = 0.0
            if expected_section and section == expected_section:
                section_bonus = 0.45

            final_score = float(semantic_scores[index]) + keyword_bonus + section_bonus
            final_scores.append(final_score)

        top_indices = np.argsort(final_scores)[::-1][:top_k]

        results: list[SearchResult] = []

        for index in top_indices:
            results.append(
                SearchResult(
                    text=self.chunks[index],
                    score=float(final_scores[index]),
                    chunk_id=int(index),
                )
            )

        return [result.__dict__ for result in results]
