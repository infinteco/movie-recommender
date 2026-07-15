"""The content-based recommender: cosine similarity blended with popularity."""

from __future__ import annotations

from dataclasses import dataclass

import joblib
import numpy as np
import pandas as pd
from rapidfuzz import fuzz, process

from movie_rec.config import settings
from movie_rec.logging_config import get_logger

logger = get_logger(__name__)


class MovieNotFoundError(Exception):
    """Raised when a title cannot be resolved, carrying close suggestions."""

    def __init__(self, query: str, suggestions: list[str]) -> None:
        self.query = query
        self.suggestions = suggestions
        super().__init__(f"No movie matched {query!r}.")


@dataclass
class Recommendation:
    """One recommended movie."""

    id: int
    title: str
    score: float  # blended content + popularity, in [0, 1]
    similarity: float  # raw content cosine similarity, in [0, 1]
    vote_average: float
    genres: list[str]
    release_date: str | None


class Recommender:
    """Holds the catalog and precomputed cosine-similarity matrix.

    ``catalog`` must contain: ``id``, ``title``, ``genre_list``,
    ``vote_average``, ``release_date`` and ``wr_norm`` (normalized weighted
    rating). ``similarity`` is an (n, n) cosine-similarity matrix aligned to the
    catalog's row order.
    """

    def __init__(
        self,
        catalog: pd.DataFrame,
        similarity: np.ndarray,
        blend_alpha: float | None = None,
    ) -> None:
        self.catalog = catalog.reset_index(drop=True)
        self.similarity = similarity
        self.blend_alpha = settings.blend_alpha if blend_alpha is None else blend_alpha
        self._titles = self.catalog["title"].tolist()
        # Lowercased exact-match lookup: title -> row index.
        self._lower_index = {t.lower(): i for i, t in enumerate(self._titles)}

    @property
    def titles(self) -> list[str]:
        return self._titles

    def resolve_index(self, query: str, score_cutoff: float = 60.0) -> int:
        """Resolve a (possibly fuzzy) title to a catalog row index.

        Exact case-insensitive match wins; otherwise the best RapidFuzz match
        above ``score_cutoff`` is used. Raises :class:`MovieNotFoundError` with
        suggestions if nothing is close enough.
        """
        key = query.strip().lower()
        if key in self._lower_index:
            return self._lower_index[key]

        match = process.extractOne(
            query, self._titles, scorer=fuzz.WRatio, score_cutoff=score_cutoff
        )
        if match is None:
            raise MovieNotFoundError(query, self.suggest(query))
        return match[2]  # (choice, score, index)

    def suggest(self, query: str, limit: int = 5) -> list[str]:
        """Closest catalog titles to ``query`` (for helpful error messages)."""
        results = process.extract(query, self._titles, scorer=fuzz.WRatio, limit=limit)
        return [choice for choice, _score, _idx in results]

    def search(self, query: str, limit: int = 10) -> list[str]:
        """Title search-as-you-type for the frontend.

        Substring matches come first (best for type-ahead — "aveng" surfaces
        "The Avengers"), ranked by where the match occurs then by title length;
        fuzzy matches (typo tolerance) fill any remaining slots.
        """
        q = query.strip().lower()
        if not q:
            return []

        substring = sorted(
            (t for t in self._titles if q in t.lower()),
            key=lambda t: (t.lower().find(q), len(t)),
        )
        results = substring[:limit]
        if len(results) >= limit:
            return results

        seen = set(results)
        for choice, score, _idx in process.extract(
            query, self._titles, scorer=fuzz.WRatio, limit=limit * 2
        ):
            if score > 60 and choice not in seen:
                results.append(choice)
                seen.add(choice)
            if len(results) >= limit:
                break
        return results

    def recommend(self, title: str, k: int = 10) -> list[Recommendation]:
        """Top-``k`` recommendations for ``title`` by blended score."""
        idx = self.resolve_index(title)
        content = self.similarity[idx].astype(float)
        popularity = self.catalog["wr_norm"].to_numpy()
        blended = self.blend_alpha * content + (1.0 - self.blend_alpha) * popularity

        order = np.argsort(blended)[::-1]
        results: list[Recommendation] = []
        for j in order:
            if j == idx:
                continue
            row = self.catalog.iloc[j]
            results.append(
                Recommendation(
                    id=int(row["id"]),
                    title=str(row["title"]),
                    score=round(float(blended[j]), 4),
                    similarity=round(float(content[j]), 4),
                    vote_average=float(row["vote_average"]),
                    genres=list(row["genre_list"]),
                    release_date=(
                        None if pd.isna(row["release_date"]) else str(row["release_date"])
                    ),
                )
            )
            if len(results) >= k:
                break
        return results

    @classmethod
    def load(cls) -> Recommender:
        """Load persisted artifacts (``movierec-build`` must have run)."""
        if not settings.catalog_path.exists() or not settings.similarity_path.exists():
            raise FileNotFoundError(
                "Recommender artifacts not found. Build them with `movierec-build`."
            )
        catalog = joblib.load(settings.catalog_path)
        similarity = np.load(settings.similarity_path)
        logger.info("Loaded recommender", extra={"movies": len(catalog)})
        return cls(catalog, similarity)
