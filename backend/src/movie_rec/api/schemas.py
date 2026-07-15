"""Pydantic response models for the recommender API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RecommendationItem(BaseModel):
    """A single recommended movie."""

    model_config = ConfigDict(protected_namespaces=())

    id: int
    title: str
    score: float = Field(description="Blended content + popularity score in [0, 1].")
    similarity: float = Field(description="Raw content cosine similarity in [0, 1].")
    vote_average: float
    genres: list[str]
    release_date: str | None = None
    poster_url: str | None = None


class RecommendResponse(BaseModel):
    query: str
    resolved_title: str
    count: int
    results: list[RecommendationItem]


class SearchResponse(BaseModel):
    query: str
    results: list[str]


class HealthResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    status: str
    model_loaded: bool
    n_movies: int | None = None
