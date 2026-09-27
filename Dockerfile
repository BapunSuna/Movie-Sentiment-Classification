FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --locked --no-dev

ENV PYTHONPATH=/app

# NLTK data location
ENV NLTK_DATA=/root/nltk_data

# DagsHub MLflow tracking URI
ENV MLFLOW_TRACKING_URI=https://dagshub.com/BapunSuna/Movie-Sentiment-Classification.mlflow

# Download NLTK resources
RUN uv run python -c "import nltk; nltk.download('stopwords', download_dir='/root/nltk_data'); nltk.download('wordnet', download_dir='/root/nltk_data'); nltk.download('omw-1.4', download_dir='/root/nltk_data')"

# Extract NLTK corpora
RUN unzip -q /root/nltk_data/corpora/wordnet.zip -d /root/nltk_data/corpora/ \
    && unzip -q /root/nltk_data/corpora/omw-1.4.zip -d /root/nltk_data/corpora/

# Verify NLTK resources during image build
RUN uv run python -c "import nltk; nltk.data.find('corpora/stopwords'); nltk.data.find('corpora/wordnet'); print('NLTK data OK')"

# Copy application
COPY . .

EXPOSE 5000

# Start Flask application with Gunicorn
CMD ["uv", "run", "--no-dev", "gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "flask_app.app:app"]

