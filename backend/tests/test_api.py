"""API tests using FastAPI's TestClient (lifespan loads the built artifacts)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from movie_rec.api.main import app


def test_health_reports_loaded(built_artifacts):
    with TestClient(app) as client:
        resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True
    assert body["n_movies"] == 6


def test_recommend_returns_results(built_artifacts):
    with TestClient(app) as client:
        resp = client.get("/recommend", params={"title": "Star Voyager", "k": 3})
    assert resp.status_code == 200
    body = resp.json()
    assert body["resolved_title"] == "Star Voyager"
    assert body["count"] == 3
    assert body["results"][0]["poster_url"] is None  # no TMDB key in tests
    assert 0.0 <= body["results"][0]["score"] <= 1.0


def test_recommend_fuzzy_title(built_artifacts):
    with TestClient(app) as client:
        resp = client.get("/recommend", params={"title": "star voyagr"})
    assert resp.status_code == 200
    assert resp.json()["resolved_title"] == "Star Voyager"


def test_recommend_unknown_title_404_with_suggestions(built_artifacts):
    with TestClient(app) as client:
        resp = client.get("/recommend", params={"title": "zzzz nonexistent qqq"})
    assert resp.status_code == 404
    assert "suggestions" in resp.json()


def test_search_endpoint(built_artifacts):
    with TestClient(app) as client:
        resp = client.get("/movies/search", params={"q": "galax"})
    assert resp.status_code == 200
    assert "Galaxy Warriors" in resp.json()["results"]


def test_recommend_without_artifacts_503(tmp_path, monkeypatch):
    from movie_rec.config import settings

    monkeypatch.setattr(settings, "artifacts_dir", tmp_path)  # empty dir
    with TestClient(app) as client:
        resp = client.get("/recommend", params={"title": "Star Voyager"})
    assert resp.status_code == 503
