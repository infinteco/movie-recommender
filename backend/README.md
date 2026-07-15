# Movie Recommender — Backend

FastAPI service for the content-based movie recommender (TMDB 5000): TF-IDF +
cosine similarity blended with an IMDb weighted-rating popularity signal, with
RapidFuzz fuzzy title matching.

See the [project README](../README.md) for the full architecture, evaluation
methodology, and deployment guide.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,data]"
movierec-build                              # build artifacts (synthetic if no CSV)
uvicorn movie_rec.api.main:app --reload     # http://localhost:8000/docs
```

## Endpoints

- `GET /recommend?title=&k=10` — recommendations (fuzzy title match; 404 with suggestions)
- `GET /movies/search?q=` — search-as-you-type titles
- `GET /health` — liveness + whether artifacts are loaded
