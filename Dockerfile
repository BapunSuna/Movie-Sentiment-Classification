FROM python:3.10-slim

# 1. Faster startup: pre-compile .pyc bytecode & use venv directly without `uv run`
# 2. Prevent Python from buffering stdout/stderr so Render logs appear immediately
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONPATH=/app \
    NLTK_DATA=/root/nltk_data \
    MLFLOW_TRACKING_URI=https://dagshub.com/BapunSuna/Movie-Sentiment-Classification.mlflow \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Copy uv binary directly from official image (much faster than `pip install uv`)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files and install (cached unless pyproject.toml/uv.lock change)
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# Download, extract, clean up, and verify NLTK resources in a SINGLE layer
RUN python -c "import nltk; \
    nltk.download('stopwords', download_dir='/root/nltk_data'); \
    nltk.download('wordnet', download_dir='/root/nltk_data'); \
    nltk.download('omw-1.4', download_dir='/root/nltk_data')" \
    && unzip -q -o /root/nltk_data/corpora/wordnet.zip -d /root/nltk_data/corpora/ \
    && unzip -q -o /root/nltk_data/corpora/omw-1.4.zip -d /root/nltk_data/corpora/ \
    && rm -f /root/nltk_data/corpora/*.zip \
    && python -c "import nltk; nltk.data.find('corpora/stopwords'); nltk.data.find('corpora/wordnet'); print('NLTK data OK')"

# Copy application code
COPY . .

EXPOSE 5000

# Start Flask application with Gunicorn directly from .venv
# - Binds dynamically to Render's $PORT (prevents Render from restarting the deploy)
# - Uses --preload so Gunicorn binds/loads cleanly and saves RAM on Render Free tier
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 --timeout 120 --preload flask_app.app:app"]