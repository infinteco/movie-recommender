"""Optional poster-image enrichment via the TMDB API.

The TMDB 5000 CSV has no ``poster_path``. If ``MOVIEREC_TMDB_API_KEY`` is set,
we look up the poster for a movie id and build a CDN URL; otherwise we return
``None`` and the frontend shows a placeholder. Results are memoized so repeated
recommendations don't re-hit the API.
"""

from __future__ import annotations

from functools import lru_cache

import requests

from movie_rec.config import settings
from movie_rec.logging_config import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=4096)
def poster_url(movie_id: int) -> str | None:
    """Return a TMDB poster URL for ``movie_id``, or ``None`` if unavailable."""
    if not settings.tmdb_api_key:
        return None
    try:
        resp = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}",
            params={"api_key": settings.tmdb_api_key},
            timeout=4,
        )
        resp.raise_for_status()
        path = resp.json().get("poster_path")
        return f"{settings.tmdb_image_base}{path}" if path else None
    except requests.RequestException as exc:  # network/HTTP error → placeholder
        logger.warning("Poster lookup failed", extra={"movie_id": movie_id, "error": str(exc)})
        return None
