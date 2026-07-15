"""Load the TMDB 5000 dataset (movies + credits merged).

The raw CSVs are *not* committed (see ``.gitignore``). Use ``movierec-load`` to
fetch them via ``kagglehub`` into ``data/raw/``. ``make_synthetic_sample``
produces a schema-compatible frame so tests and CI run without Kaggle access.

Dataset: "TMDB 5000 Movie Metadata" on Kaggle
(https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata). This product uses the
TMDB API but is not endorsed or certified by TMDB. See the README for licensing.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from movie_rec.config import settings
from movie_rec.logging_config import get_logger

logger = get_logger(__name__)

# Columns kept from the merged frame.
KEEP_COLUMNS = [
    "id",
    "title",
    "overview",
    "genres",
    "keywords",
    "cast",
    "crew",
    "vote_average",
    "vote_count",
    "popularity",
    "release_date",
]


def download_dataset() -> Path:
    """Download both CSVs via ``kagglehub`` into ``data/raw`` and return the dir."""
    import shutil

    import kagglehub

    logger.info("Downloading dataset via kagglehub", extra={"dataset": settings.dataset})
    source_dir = Path(kagglehub.dataset_download(settings.dataset))
    settings.raw_dir.mkdir(parents=True, exist_ok=True)
    for name in (settings.movies_csv, settings.credits_csv):
        matches = list(source_dir.rglob(name))
        if not matches:
            raise FileNotFoundError(f"{name!r} not found in downloaded dataset at {source_dir}")
        shutil.copyfile(matches[0], settings.raw_dir / name)
    logger.info("Saved raw CSVs", extra={"dir": str(settings.raw_dir)})
    return settings.raw_dir


def load_raw(raw_dir: str | Path | None = None) -> pd.DataFrame:
    """Load and merge the movies + credits CSVs into one frame.

    Raises ``FileNotFoundError`` if either CSV is missing.
    """
    base = Path(raw_dir) if raw_dir is not None else settings.raw_dir
    movies_path = base / settings.movies_csv
    credits_path = base / settings.credits_csv
    for path in (movies_path, credits_path):
        if not path.exists():
            raise FileNotFoundError(
                f"Missing {path}. Run `movierec-load` to fetch the TMDB dataset."
            )

    movies = pd.read_csv(movies_path)
    credits = pd.read_csv(credits_path)
    # credits has movie_id + title + cast + crew; merge on id.
    credits = credits.rename(columns={"movie_id": "id"})
    merged = movies.merge(credits[["id", "cast", "crew"]], on="id", how="inner")

    merged = merged[KEEP_COLUMNS].copy()
    merged = merged.dropna(subset=["title"]).drop_duplicates(subset=["id"])
    merged["overview"] = merged["overview"].fillna("")
    logger.info("Loaded merged dataset", extra={"rows": len(merged)})
    return merged.reset_index(drop=True)


def _json_people(names: list[str], with_job: str | None = None) -> str:
    """Build a TMDB-style JSON list of ``{"name": ...}`` (optionally with job)."""
    items = []
    for n in names:
        entry = {"name": n}
        if with_job:
            entry["job"] = with_job
        items.append(entry)
    return json.dumps(items)


def make_synthetic_sample() -> pd.DataFrame:
    """A tiny schema-compatible dataset for tests and CI.

    Two clusters (space-action vs. romance) so overlap-based evaluation has
    something meaningful to measure.
    """
    rows = [
        {
            "id": 1,
            "title": "Star Voyager",
            "overview": "A crew explores a distant galaxy under alien threat.",
            "genres": '[{"name": "Action"}, {"name": "Science Fiction"}]',
            "keywords": '[{"name": "space"}, {"name": "alien"}, {"name": "spaceship"}]',
            "cast": _json_people(["Alice Nova", "Bob Star", "Cara Vega", "Extra One"]),
            "crew": _json_people(["Dana Comet"], with_job="Director"),
            "vote_average": 7.8,
            "vote_count": 5000,
            "popularity": 120.0,
            "release_date": "2015-06-01",
        },
        {
            "id": 2,
            "title": "Galaxy Warriors",
            "overview": "Rebels fight an empire across the stars with spaceships.",
            "genres": '[{"name": "Action"}, {"name": "Science Fiction"}]',
            "keywords": '[{"name": "space"}, {"name": "alien"}, {"name": "battle"}]',
            "cast": _json_people(["Alice Nova", "Cara Vega", "Ed Ray", "Extra Two"]),
            "crew": _json_people(["Dana Comet"], with_job="Director"),
            "vote_average": 7.2,
            "vote_count": 4200,
            "popularity": 95.0,
            "release_date": "2017-05-01",
        },
        {
            "id": 3,
            "title": "Cosmic Frontier",
            "overview": "An astronaut battles aliens aboard a derelict spaceship.",
            "genres": '[{"name": "Science Fiction"}, {"name": "Thriller"}]',
            "keywords": '[{"name": "space"}, {"name": "alien"}, {"name": "survival"}]',
            "cast": _json_people(["Bob Star", "Cara Vega", "Fay Lin", "Extra Three"]),
            "crew": _json_people(["Gil Orbit"], with_job="Director"),
            "vote_average": 6.9,
            "vote_count": 3000,
            "popularity": 70.0,
            "release_date": "2019-03-01",
        },
        {
            "id": 4,
            "title": "Paris in Love",
            "overview": "Two strangers fall in love over a summer in Paris.",
            "genres": '[{"name": "Romance"}, {"name": "Drama"}]',
            "keywords": '[{"name": "love"}, {"name": "paris"}, {"name": "summer"}]',
            "cast": _json_people(["Hana Rose", "Ivan Poe", "Jo Wells", "Extra Four"]),
            "crew": _json_people(["Kim Vale"], with_job="Director"),
            "vote_average": 7.0,
            "vote_count": 2500,
            "popularity": 60.0,
            "release_date": "2016-02-01",
        },
        {
            "id": 5,
            "title": "Autumn Hearts",
            "overview": "A romance rekindles between old lovers one autumn.",
            "genres": '[{"name": "Romance"}, {"name": "Drama"}]',
            "keywords": '[{"name": "love"}, {"name": "reunion"}, {"name": "autumn"}]',
            "cast": _json_people(["Hana Rose", "Jo Wells", "Liam Frost", "Extra Five"]),
            "crew": _json_people(["Kim Vale"], with_job="Director"),
            "vote_average": 6.5,
            "vote_count": 1800,
            "popularity": 40.0,
            "release_date": "2018-10-01",
        },
        {
            "id": 6,
            "title": "Winter Promise",
            "overview": "A heartfelt love story set during a snowy winter.",
            "genres": '[{"name": "Romance"}]',
            "keywords": '[{"name": "love"}, {"name": "winter"}, {"name": "wedding"}]',
            "cast": _json_people(["Ivan Poe", "Mia Snow", "Jo Wells", "Extra Six"]),
            "crew": _json_people(["Nora Pine"], with_job="Director"),
            "vote_average": 6.1,
            "vote_count": 900,
            "popularity": 25.0,
            "release_date": "2020-12-01",
        },
    ]
    return pd.DataFrame(rows)[KEEP_COLUMNS]


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch the TMDB 5000 dataset via kagglehub.")
    parser.parse_args()
    path = download_dataset()
    print(f"Dataset ready in: {path}")


if __name__ == "__main__":
    main()
