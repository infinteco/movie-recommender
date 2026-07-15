# syntax=docker/dockerfile:1
# Backend API image. Deploy to Render/Railway; the frontend deploys separately to Vercel.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Keep the raw data and built artifacts on fixed paths inside the image.
ENV MOVIEREC_RAW_DIR=/app/data/raw \
    MOVIEREC_ARTIFACTS_DIR=/app/artifacts

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install .

# Fetch the real TMDB 5000 dataset from public mirrors and build the artifacts
# into the image so the API starts ready with ~4,800 movies. If the download
# fails (mirror down / offline build), fall back to the synthetic sample so the
# build never breaks. Raw CSVs (~45 MB) are removed after the artifacts are built.
ARG MOVIES_URL=https://raw.githubusercontent.com/vamshi121/TMDB-5000-Movie-Dataset/main/tmdb_5000_movies.csv
ARG CREDITS_URL=https://raw.githubusercontent.com/harshitcodes/tmdb_movie_data_analysis/master/tmdb-5000-movie-dataset/tmdb_5000_credits.csv
RUN python -c "import os,urllib.request; os.makedirs('/app/data/raw',exist_ok=True); urllib.request.urlretrieve('$MOVIES_URL','/app/data/raw/tmdb_5000_movies.csv'); urllib.request.urlretrieve('$CREDITS_URL','/app/data/raw/tmdb_5000_credits.csv')" \
    && movierec-build --no-synthetic \
    && rm -rf /app/data/raw \
    || movierec-build

ENV PORT=8000
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s \
    CMD python -c "import urllib.request,os; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\",8000)}/health')" || exit 1

CMD ["sh", "-c", "uvicorn movie_rec.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
