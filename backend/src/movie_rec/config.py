"""Central configuration for the recommender (env-overridable)."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime configuration, overridable via ``MOVIEREC_*`` env vars."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="MOVIEREC_",
        extra="ignore",
        protected_namespaces=(),
    )

    # Data
    dataset: str = "tmdb/tmdb-movie-metadata"
    movies_csv: str = "tmdb_5000_movies.csv"
    credits_csv: str = "tmdb_5000_credits.csv"
    raw_dir: Path = PROJECT_ROOT / "data" / "raw"

    # Artifacts (persisted by `movierec-build`)
    artifacts_dir: Path = PROJECT_ROOT / "artifacts"

    # Ranking
    # Final score = blend_alpha * content_similarity
    #             + (1 - blend_alpha) * normalized_weighted_rating.
    blend_alpha: float = 0.7
    # Percentile of vote_count used as the `m` cutoff in the IMDb weighted rating.
    vote_count_quantile: float = 0.80
    top_cast: int = 3
    max_features: int = 20000

    # Optional TMDB API enrichment for poster images.
    tmdb_api_key: str | None = None
    tmdb_image_base: str = "https://image.tmdb.org/t/p/w500"

    # API
    rate_limit: str = "60/minute"
    log_level: str = "INFO"

    @property
    def vectorizer_path(self) -> Path:
        return self.artifacts_dir / "vectorizer.joblib"

    @property
    def similarity_path(self) -> Path:
        return self.artifacts_dir / "similarity.npy"

    @property
    def catalog_path(self) -> Path:
        return self.artifacts_dir / "catalog.joblib"


settings = Settings()
