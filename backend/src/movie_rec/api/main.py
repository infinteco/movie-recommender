"""FastAPI application exposing the movie recommender.

No ``from __future__ import annotations`` here: the slowapi rate-limit decorator
wraps endpoints, and FastAPI must resolve real annotation objects to build the
request/response schema.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from movie_rec.api.posters import poster_url
from movie_rec.api.schemas import (
    HealthResponse,
    RecommendationItem,
    RecommendResponse,
    SearchResponse,
)
from movie_rec.config import settings
from movie_rec.logging_config import get_logger
from movie_rec.recommender.model import MovieNotFoundError, Recommender

logger = get_logger("movie_rec.api")
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])

_recommender: Recommender | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _recommender
    try:
        _recommender = Recommender.load()
        logger.info("Recommender loaded", extra={"movies": len(_recommender.catalog)})
    except FileNotFoundError:
        logger.warning("No artifacts found; endpoints will return 503 until built")
        _recommender = None
    yield


app = FastAPI(
    title="Movie Recommender API",
    version="0.1.0",
    description="Content-based recommendations (TMDB 5000) blended with popularity.",
    lifespan=lifespan,
)
app.state.limiter = limiter

# CORS so the Vercel-hosted frontend can call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded."})


def _require_model() -> Recommender | JSONResponse:
    if _recommender is None:
        return JSONResponse(
            status_code=503,
            content={"detail": "Recommender not built. Run `movierec-build`."},
        )
    return _recommender


@app.get("/health", response_model=HealthResponse, tags=["ops"])
async def health() -> HealthResponse:
    """Liveness + readiness probe."""
    return HealthResponse(
        status="ok",
        model_loaded=_recommender is not None,
        n_movies=len(_recommender.catalog) if _recommender else None,
    )


@app.get("/recommend", response_model=RecommendResponse, tags=["recommend"])
@limiter.limit(settings.rate_limit)
async def recommend(
    request: Request,
    title: str = Query(..., min_length=1, description="Movie title (fuzzy-matched)."),
    k: int = Query(10, ge=1, le=50),
):
    """Recommend ``k`` movies similar to ``title`` (fuzzy title matching)."""
    model = _require_model()
    if isinstance(model, JSONResponse):
        return model
    try:
        recs = model.recommend(title, k=k)
        resolved = model.catalog.iloc[model.resolve_index(title)]["title"]
    except MovieNotFoundError as exc:
        return JSONResponse(
            status_code=404,
            content={
                "detail": f"No movie matched '{exc.query}'.",
                "suggestions": exc.suggestions,
            },
        )

    items = [
        RecommendationItem(
            id=r.id,
            title=r.title,
            score=r.score,
            similarity=r.similarity,
            vote_average=r.vote_average,
            genres=r.genres,
            release_date=r.release_date,
            poster_url=poster_url(r.id),
        )
        for r in recs
    ]
    logger.info("recommend", extra={"query": title, "resolved": resolved, "k": k})
    return RecommendResponse(
        query=title, resolved_title=str(resolved), count=len(items), results=items
    )


@app.get("/movies/search", response_model=SearchResponse, tags=["recommend"])
@limiter.limit(settings.rate_limit)
async def search(
    request: Request,
    q: str = Query("", description="Partial title for search-as-you-type."),
):
    """Return catalog titles matching ``q`` (for the search box)."""
    model = _require_model()
    if isinstance(model, JSONResponse):
        return model
    return SearchResponse(query=q, results=model.search(q))
