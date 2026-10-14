# from flask import Flask, render_template, request

# import pickle
# import os
# import pandas as pd
# import time
# import re
# import string
# import warnings
# import numpy as np
# from pathlib import Path

# try:
#     import mlflow
# except Exception as exc:  # pragma: no cover - defensive for container/local startup
#     mlflow = None
#     MLFLOW_IMPORT_ERROR = exc
# else:
#     MLFLOW_IMPORT_ERROR = None

# from prometheus_client import (
#     Counter,
#     Histogram,
#     generate_latest,
#     CollectorRegistry,
#     CONTENT_TYPE_LATEST,
# )

# from nltk.stem import WordNetLemmatizer
# from nltk.corpus import stopwords

# warnings.simplefilter("ignore", UserWarning)
# warnings.filterwarnings("ignore")


# # ============================================================
# # Text preprocessing
# # ============================================================


# def lemmatization(text):
#     """Lemmatize the text."""
#     lemmatizer = WordNetLemmatizer()

#     text = text.split()
#     text = [lemmatizer.lemmatize(word) for word in text]

#     return " ".join(text)


# def remove_stop_words(text):
#     """Remove stop words from the text."""
#     stop_words = set(stopwords.words("english"))

#     text = [word for word in str(text).split() if word not in stop_words]

#     return " ".join(text)


# def removing_numbers(text):
#     """Remove numbers from the text."""
#     return "".join([char for char in text if not char.isdigit()])


# def lower_case(text):
#     """Convert text to lower case."""
#     text = text.split()
#     text = [word.lower() for word in text]

#     return " ".join(text)


# def removing_punctuations(text):
#     """Remove punctuations from the text."""
#     text = re.sub("[%s]" % re.escape(string.punctuation), " ", text)

#     text = text.replace("؛", "")
#     text = re.sub(r"\s+", " ", text).strip()

#     return text


# def removing_urls(text):
#     """Remove URLs from the text."""
#     url_pattern = re.compile(r"https?://\S+|www\.\S+")

#     return url_pattern.sub("", text)


# def remove_small_sentences(df):
#     """Remove sentences with less than 3 words."""
#     for i in range(len(df)):
#         if len(df.text.iloc[i].split()) < 3:
#             df.text.iloc[i] = np.nan


# def normalize_text(text):
#     """Apply complete text preprocessing pipeline."""
#     text = lower_case(text)
#     text = remove_stop_words(text)
#     text = removing_numbers(text)
#     text = removing_punctuations(text)
#     text = removing_urls(text)
#     text = lemmatization(text)

#     return text


# # ============================================================
# # MLflow + DagsHub configuration
# # ============================================================
# BASE_DIR = Path(__file__).resolve().parent.parent
# MODEL_PATH = BASE_DIR / "models" / "model.pkl"
# VECTORIZER_PATH = BASE_DIR / "models" / "vectorizer.pkl"

# dagshub_url = "https://dagshub.com"
# repo_owner = "BapunSuna"
# repo_name = "Movie-Sentiment-Classification"


# def load_model_and_vectorizer():
#     """Load a remote MLflow model when credentials are available, otherwise use the local checkpoint."""
#     dagshub_token = os.getenv("DAGSHUB_TOKEN")

#     if dagshub_token and mlflow is not None:
#         try:
#             os.environ["MLFLOW_TRACKING_USERNAME"] = dagshub_token
#             os.environ["MLFLOW_TRACKING_PASSWORD"] = dagshub_token
#             mlflow.set_tracking_uri(f"{dagshub_url}/{repo_owner}/{repo_name}.mlflow")

#             model_name = "my_model"
#             model_alias = "champion"
#             model_uri = f"models:/{model_name}@{model_alias}"
#             model = mlflow.pyfunc.load_model(model_uri)
#             print(f"Loaded model from MLflow: {model_uri}")
#             with open(VECTORIZER_PATH, "rb") as vector_file:
#                 vectorizer = pickle.load(vector_file)
#             return model, vectorizer
#         except Exception as exc:
#             print(f"MLflow model load failed, falling back to local model: {exc}")

#     if MODEL_PATH.exists() and VECTORIZER_PATH.exists():
#         with open(MODEL_PATH, "rb") as model_file:
#             model = pickle.load(model_file)
#         with open(VECTORIZER_PATH, "rb") as vector_file:
#             vectorizer = pickle.load(vector_file)
#         print(f"Loaded local model from {MODEL_PATH}")
#         return model, vectorizer

#     if mlflow is None and MLFLOW_IMPORT_ERROR is not None:
#         raise RuntimeError(
#             f"MLflow could not be imported and no local model files were found: {MLFLOW_IMPORT_ERROR}"
#         )

#     raise RuntimeError(
#         "No DagsHub token was provided and no local model files were found in the models directory."
#     )


# # ============================================================
# # Flask application
# # ============================================================

# app = Flask(__name__)


# # ============================================================
# # Prometheus metrics
# # ============================================================

# registry = CollectorRegistry()

# REQUEST_COUNT = Counter(
#     "app_request_count",
#     "Total number of requests to the app",
#     ["method", "endpoint"],
#     registry=registry,
# )

# REQUEST_LATENCY = Histogram(
#     "app_request_latency_seconds",
#     "Latency of requests in seconds",
#     ["endpoint"],
#     registry=registry,
# )

# PREDICTION_COUNT = Counter(
#     "model_prediction_count",
#     "Count of predictions for each class",
#     ["prediction"],
#     registry=registry,
# )


# # ============================================================
# # Model and Vectorizer
# # ============================================================

# model, vectorizer = load_model_and_vectorizer()


# # ============================================================
# # Routes
# # ============================================================


# @app.route("/")
# def home():

#     REQUEST_COUNT.labels(method="GET", endpoint="/").inc()

#     start_time = time.time()

#     response = render_template("index.html", result=None)

#     REQUEST_LATENCY.labels(endpoint="/").observe(time.time() - start_time)

#     return response


# @app.route("/predict", methods=["POST"])
# def predict():

#     REQUEST_COUNT.labels(method="POST", endpoint="/predict").inc()

#     start_time = time.time()

#     text = request.form["text"]

#     # Clean text
#     text = normalize_text(text)

#     # Convert text to features
#     features = vectorizer.transform([text])

#     features_df = pd.DataFrame(
#         features.toarray(), columns=[str(i) for i in range(features.shape[1])]
#     )

#     # Predict
#     result = model.predict(features_df)

#     prediction = result[0]

#     # Count prediction
#     PREDICTION_COUNT.labels(prediction=str(prediction)).inc()

#     # Measure latency
#     REQUEST_LATENCY.labels(endpoint="/predict").observe(time.time() - start_time)

#     return render_template("index.html", result=prediction)


# @app.route("/metrics", methods=["GET"])
# def metrics():
#     """Expose custom Prometheus metrics."""

#     return (
#         generate_latest(registry),
#         200,
#         {"Content-Type": CONTENT_TYPE_LATEST},
#     )


# # ============================================================
# # Run Flask application
# # ============================================================

# if __name__ == "__main__":

#     app.run(host="0.0.0.0", port=5000)


from flask import Flask, render_template, request, redirect, url_for

import pickle
import os
import pandas as pd
import time
import re
import string
import warnings
import numpy as np
from pathlib import Path

try:
    import mlflow
except Exception as exc:  # pragma: no cover - defensive for container/local startup
    mlflow = None
    MLFLOW_IMPORT_ERROR = exc
else:
    MLFLOW_IMPORT_ERROR = None

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
# Text preprocessing (Initialized once at startup for speed)
# ============================================================

LEMMATIZER = WordNetLemmatizer()
STOP_WORDS = set(stopwords.words("english"))
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
PUNCT_PATTERN = re.compile("[%s]" % re.escape(string.punctuation))


def lemmatization(text):
    """Lemmatize the text."""
    return " ".join([LEMMATIZER.lemmatize(word) for word in text.split()])


def remove_stop_words(text):
    """Remove stop words from the text."""
    return " ".join([word for word in str(text).split() if word not in STOP_WORDS])


def removing_numbers(text):
    """Remove numbers from the text."""
    return "".join([char for char in text if not char.isdigit()])


def lower_case(text):
    """Convert text to lower case."""
    return " ".join([word.lower() for word in text.split()])


def removing_punctuations(text):
    """Remove punctuations from the text."""
    text = PUNCT_PATTERN.sub(" ", text)
    text = text.replace("؛", "")
    return re.sub(r"\s+", " ", text).strip()


def removing_urls(text):
    """Remove URLs from the text."""
    return URL_PATTERN.sub("", text)


def remove_small_sentences(df):
    """Remove sentences with less than 3 words."""
    for i in range(len(df)):
        if len(df.text.iloc[i].split()) < 3:
            df.text.iloc[i] = np.nan


def normalize_text(text):
    """Apply complete text preprocessing pipeline."""
    text = lower_case(text)
    text = removing_urls(text)  # Run before punctuation removal so https:// is intact
    text = remove_stop_words(text)
    text = removing_numbers(text)
    text = removing_punctuations(text)
    text = lemmatization(text)

    return text


# ============================================================
# MLflow + DagsHub configuration
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "model.pkl"
VECTORIZER_PATH = BASE_DIR / "models" / "vectorizer.pkl"
BUNDLED_MODEL_DIR = Path(os.getenv("MODEL_LOCAL_PATH", "/tmp/mlflow_champion_model"))

dagshub_url = "https://dagshub.com"
repo_owner = "BapunSuna"
repo_name = "Movie-Sentiment-Classification"


def load_model_and_vectorizer():
    """Load cached/bundled MLflow model first, then remote MLflow, then local pickle."""
    dagshub_token = os.getenv("DAGSHUB_TOKEN")

    # 1. If model is already cached on disk (or baked into Docker image), load immediately
    if (BUNDLED_MODEL_DIR / "MLmodel").exists() and mlflow is not None and VECTORIZER_PATH.exists():
        try:
            model = mlflow.pyfunc.load_model(str(BUNDLED_MODEL_DIR))
            with open(VECTORIZER_PATH, "rb") as vector_file:
                vectorizer = pickle.load(vector_file)
            print(f"Loaded cached MLflow model from disk: {BUNDLED_MODEL_DIR}")
            return model, vectorizer
        except Exception as exc:
            print(f"Cached MLflow model load failed, trying remote: {exc}")

    # 2. Download from DagsHub MLflow into BUNDLED_MODEL_DIR so restarts don't re-download
    if dagshub_token and mlflow is not None:
        try:
            os.environ["MLFLOW_TRACKING_USERNAME"] = dagshub_token
            os.environ["MLFLOW_TRACKING_PASSWORD"] = dagshub_token
            mlflow.set_tracking_uri(f"{dagshub_url}/{repo_owner}/{repo_name}.mlflow")

            model_uri = "models:/my_model@champion"
            BUNDLED_MODEL_DIR.mkdir(parents=True, exist_ok=True)
            local_dir = mlflow.artifacts.download_artifacts(
                artifact_uri=model_uri, dst_path=str(BUNDLED_MODEL_DIR)
            )
            model = mlflow.pyfunc.load_model(local_dir)
            print(f"Loaded model from MLflow: {model_uri} (cached at {local_dir})")
            with open(VECTORIZER_PATH, "rb") as vector_file:
                vectorizer = pickle.load(vector_file)
            return model, vectorizer
        except Exception as exc:
            print(f"MLflow model load failed, falling back to local model: {exc}")

    # 3. Fallback to local models/model.pkl if present
    if MODEL_PATH.exists() and VECTORIZER_PATH.exists():
        with open(MODEL_PATH, "rb") as model_file:
            model = pickle.load(model_file)
        with open(VECTORIZER_PATH, "rb") as vector_file:
            vectorizer = pickle.load(vector_file)
        print(f"Loaded local model from {MODEL_PATH}")
        return model, vectorizer

    if mlflow is None and MLFLOW_IMPORT_ERROR is not None:
        raise RuntimeError(
            f"MLflow could not be imported and no local model files were found: {MLFLOW_IMPORT_ERROR}"
        )

    raise RuntimeError(
        "No DagsHub token was provided and no local model files were found in the models directory."
    )


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

model, vectorizer = load_model_and_vectorizer()


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


@app.route("/predict", methods=["GET", "POST"])
def predict():
    # Redirect direct browser visits or mobile page refreshes cleanly to "/"
    if request.method == "GET":
        return redirect(url_for("home"))

    REQUEST_COUNT.labels(method="POST", endpoint="/predict").inc()
    start_time = time.time()

    text = request.form.get("text", "").strip()
    if not text:
        return render_template("index.html", result=None)

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
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
