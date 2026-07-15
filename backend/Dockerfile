# syntax=docker/dockerfile:1
# Backend API image. Deploy to Render/Railway; the frontend deploys separately to Vercel.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install .

# Build the recommender artifacts into the image so the API starts ready.
# With no Kaggle dataset at build time this uses the synthetic sample (see README);
# for real data, mount the CSVs or rebuild at runtime with `movierec-build`.
RUN movierec-build

ENV PORT=8000
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s \
    CMD python -c "import urllib.request,os; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\",8000)}/health')" || exit 1

CMD ["sh", "-c", "uvicorn movie_rec.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
