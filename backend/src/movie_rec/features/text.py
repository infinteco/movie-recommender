"""Parse TMDB JSON columns and build the combined "tags" field.

The tag string per movie concatenates a stemmed overview with normalized
genres, keywords, the top cast, and the director. Multi-word names/keywords are
collapsed into single tokens (e.g. ``"Science Fiction" -> "sciencefiction"``,
``"Christopher Nolan" -> "christophernolan"``) so TF-IDF treats them atomically.
"""

from __future__ import annotations

import ast
import json
import re

import pandas as pd
from nltk.stem import PorterStemmer

from movie_rec.config import settings

_STEMMER = PorterStemmer()
_WORD_RE = re.compile(r"[a-z0-9]+")


def _parse_json_list(value: object) -> list[dict]:
    """Parse a TMDB JSON-list cell into a list of dicts (robust to bad rows)."""
    if isinstance(value, list):
        return value
    if not isinstance(value, str) or not value.strip():
        return []
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        try:  # some exports use single-quoted Python-literal syntax
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return []


def parse_names(value: object) -> list[str]:
    """Extract the ``name`` field from a TMDB JSON list (genres, keywords)."""
    return [item["name"] for item in _parse_json_list(value) if "name" in item]


def parse_cast(value: object, top_n: int | None = None) -> list[str]:
    """Top-N billed cast names."""
    n = top_n if top_n is not None else settings.top_cast
    return parse_names(value)[:n]


def parse_director(crew: object) -> str:
    """First crew member whose job is Director, else empty string."""
    for member in _parse_json_list(crew):
        if member.get("job") == "Director":
            return member.get("name", "")
    return ""


def _collapse(name: str) -> str:
    """Lowercase and strip spaces so a multi-word entity becomes one token."""
    return re.sub(r"\s+", "", name.lower())


def _stem_overview(overview: str) -> list[str]:
    """Lowercase, tokenize and Porter-stem the free-text overview."""
    return [_STEMMER.stem(tok) for tok in _WORD_RE.findall(str(overview).lower())]


def build_tag(row: pd.Series) -> str:
    """Combine overview, genres, keywords, cast and director into one tag string."""
    tokens: list[str] = []
    tokens += _stem_overview(row.get("overview", ""))
    tokens += [_collapse(g) for g in parse_names(row.get("genres"))]
    tokens += [_collapse(k) for k in parse_names(row.get("keywords"))]
    tokens += [_collapse(c) for c in parse_cast(row.get("cast"))]
    director = parse_director(row.get("crew"))
    if director:
        tokens.append(_collapse(director))
    return " ".join(t for t in tokens if t)


def add_tags(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of ``df`` with parsed genre/director columns and a ``tags``
    column (used for vectorization and for the overlap-based evaluation)."""
    out = df.copy()
    out["genre_list"] = out["genres"].map(parse_names)
    out["keyword_list"] = out["keywords"].map(parse_names)
    out["director"] = out["crew"].map(parse_director)
    out["tags"] = out.apply(build_tag, axis=1)
    return out
