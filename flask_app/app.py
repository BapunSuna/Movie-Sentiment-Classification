from flask import Flask, render_template, request

import mlflow
import pickle
import os
import pandas as pd
import time
import re
import string
import warnings
import dagshub
import numpy as np

from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CollectorRegistry,
    CONTENT_TYPE_LATEST,
)

from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

warnings.simplefilter("ignore", UserWarning)
warnings.filterwarnings("ignore")


# ============================================================
# Text preprocessing
# ============================================================


def lemmatization(text):
    """Lemmatize the text."""
    lemmatizer = WordNetLemmatizer()

    text = text.split()
    text = [lemmatizer.lemmatize(word) for word in text]

    return " ".join(text)


def remove_stop_words(text):
    """Remove stop words from the text."""
    stop_words = set(stopwords.words("english"))

    text = [word for word in str(text).split() if word not in stop_words]

    return " ".join(text)


def removing_numbers(text):
    """Remove numbers from the text."""
    return "".join([char for char in text if not char.isdigit()])


def lower_case(text):
    """Convert text to lower case."""
    text = text.split()
    text = [word.lower() for word in text]

    return " ".join(text)


def removing_punctuations(text):
    """Remove punctuations from the text."""
    text = re.sub("[%s]" % re.escape(string.punctuation), " ", text)

    text = text.replace("؛", "")
    text = re.sub(r"\s+", " ", text).strip()

    return text


def removing_urls(text):
    """Remove URLs from the text."""
    url_pattern = re.compile(r"https?://\S+|www\.\S+")

    return url_pattern.sub("", text)


def remove_small_sentences(df):
    """Remove sentences with less than 3 words."""
    for i in range(len(df)):
        if len(df.text.iloc[i].split()) < 3:
            df.text.iloc[i] = np.nan


def normalize_text(text):
    """Apply complete text preprocessing pipeline."""
    text = lower_case(text)
    text = remove_stop_words(text)
    text = removing_numbers(text)
    text = removing_punctuations(text)
    text = removing_urls(text)
    text = lemmatization(text)

    return text


# ============================================================
# MLflow + DagsHub configuration
# ============================================================
dagshub_token = os.getenv("DAGSHUB_TOKEN")

if not dagshub_token:
    raise EnvironmentError("DAGSHUB_TOKEN environment variable is not set")

# Configure MLflow authentication
os.environ["MLFLOW_TRACKING_USERNAME"] = dagshub_token
os.environ["MLFLOW_TRACKING_PASSWORD"] = dagshub_token

# DagsHub MLflow tracking URI
dagshub_url = "https://dagshub.com"
repo_owner = "BapunSuna"
repo_name = "Movie-Sentiment-Classification"

mlflow.set_tracking_uri(f"{dagshub_url}/{repo_owner}/{repo_name}.mlflow")

# ============================================================
# Flask application
# ============================================================

app = Flask(__name__)


# ============================================================
# Prometheus metrics
# ============================================================

registry = CollectorRegistry()

REQUEST_COUNT = Counter(
    "app_request_count",
    "Total number of requests to the app",
    ["method", "endpoint"],
    registry=registry,
)

REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Latency of requests in seconds",
    ["endpoint"],
    registry=registry,
)

PREDICTION_COUNT = Counter(
    "model_prediction_count",
    "Count of predictions for each class",
    ["prediction"],
    registry=registry,
)


# ============================================================
# Model and Vectorizer
# ============================================================

model_name = "my_model"
model_alias = "champion"

# Use MLflow alias instead of model registry stages
model_uri = f"models:/{model_name}@{model_alias}"

print(f"Fetching model from: {model_uri}")

model = mlflow.pyfunc.load_model(model_uri)

vectorizer = pickle.load(open("models/vectorizer.pkl", "rb"))


# ============================================================
# Routes
# ============================================================


@app.route("/")
def home():

    REQUEST_COUNT.labels(method="GET", endpoint="/").inc()

    start_time = time.time()

    response = render_template("index.html", result=None)

    REQUEST_LATENCY.labels(endpoint="/").observe(time.time() - start_time)

    return response


@app.route("/predict", methods=["POST"])
def predict():

    REQUEST_COUNT.labels(method="POST", endpoint="/predict").inc()

    start_time = time.time()

    text = request.form["text"]

    # Clean text
    text = normalize_text(text)

    # Convert text to features
    features = vectorizer.transform([text])

    features_df = pd.DataFrame(
        features.toarray(), columns=[str(i) for i in range(features.shape[1])]
    )

    # Predict
    result = model.predict(features_df)

    prediction = result[0]

    # Count prediction
    PREDICTION_COUNT.labels(prediction=str(prediction)).inc()

    # Measure latency
    REQUEST_LATENCY.labels(endpoint="/predict").observe(time.time() - start_time)

    return render_template("index.html", result=prediction)


@app.route("/metrics", methods=["GET"])
def metrics():
    """Expose custom Prometheus metrics."""

    return (
        generate_latest(registry),
        200,
        {"Content-Type": CONTENT_TYPE_LATEST},
    )


# ============================================================
# Run Flask application
# ============================================================

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000)
