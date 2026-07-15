"""Build and persist the recommender artifacts.

Steps: load data -> parse tags -> TF-IDF vectorize -> cosine similarity ->
compute the normalized weighted rating -> persist (vectorizer, similarity
matrix, catalog). Run with ``movierec-build``.
"""

from __future__ import annotations

import argparse

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from movie_rec.config import settings
from movie_rec.data.loader import load_raw, make_synthetic_sample
from movie_rec.features.text import add_tags
from movie_rec.logging_config import get_logger
from movie_rec.recommender.model import Recommender
from movie_rec.recommender.ranking import min_max_normalize, weighted_rating

logger = get_logger(__name__)

_CATALOG_COLUMNS = [
    "id",
    "title",
    "genre_list",
    "keyword_list",
    "vote_average",
    "vote_count",
    "release_date",
    "wr_norm",
]


def load_dataframe(allow_synthetic: bool = True) -> pd.DataFrame:
    """Load the real TMDB data if present, else the synthetic sample."""
    try:
        df = load_raw()
        logger.info("Using real TMDB dataset", extra={"rows": len(df)})
    except FileNotFoundError:
        if not allow_synthetic:
            raise
        logger.warning("Real dataset not found; using synthetic sample instead")
        df = make_synthetic_sample()
    return df


def build_recommender(allow_synthetic: bool = True, persist: bool = True) -> Recommender:
    """Construct a :class:`Recommender`, optionally persisting artifacts."""
    df = add_tags(load_dataframe(allow_synthetic=allow_synthetic))

    vectorizer = TfidfVectorizer(stop_words="english", max_features=settings.max_features)
    tfidf = vectorizer.fit_transform(df["tags"])
    similarity = cosine_similarity(tfidf).astype(np.float32)

    df["wr"] = weighted_rating(df, settings.vote_count_quantile)
    df["wr_norm"] = min_max_normalize(df["wr"])

    catalog = df[_CATALOG_COLUMNS].reset_index(drop=True)

    if persist:
        settings.artifacts_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(vectorizer, settings.vectorizer_path)
        np.save(settings.similarity_path, similarity)
        joblib.dump(catalog, settings.catalog_path)
        logger.info(
            "Persisted artifacts",
            extra={"dir": str(settings.artifacts_dir), "movies": len(catalog)},
        )

    return Recommender(catalog, similarity)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the recommender artifacts.")
    parser.add_argument("--no-synthetic", action="store_true", help="fail if real data missing")
    args = parser.parse_args()
    rec = build_recommender(allow_synthetic=not args.no_synthetic)
    print(
        f"Built recommender over {len(rec.catalog)} movies. Artifacts in {settings.artifacts_dir}"
    )


if __name__ == "__main__":
    main()
