"""Shared fixtures for the recommender tests."""

from __future__ import annotations

import pytest

from movie_rec.config import settings
from movie_rec.recommender.build import build_recommender
from movie_rec.recommender.model import Recommender


@pytest.fixture(scope="session")
def recommender() -> Recommender:
    """A recommender built in-memory from the synthetic sample."""
    return build_recommender(allow_synthetic=True, persist=False)


@pytest.fixture()
def built_artifacts(tmp_path, monkeypatch):
    """Persist synthetic artifacts to a temp dir and point settings at them."""
    monkeypatch.setattr(settings, "artifacts_dir", tmp_path)
    build_recommender(allow_synthetic=True, persist=True)
    return tmp_path
