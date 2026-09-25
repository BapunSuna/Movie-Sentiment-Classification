import os
import mlflow
from mlflow import MlflowClient


def promote_model():

    # Get DagsHub token
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

    # Create MLflow client
    client = MlflowClient()

    model_name = "my_model"
    champion_alias = "champion"

    # Get all registered versions
    versions = client.search_model_versions(f"name='{model_name}'")

    if not versions:
        raise ValueError(f"No registered versions found for model '{model_name}'")

    # Find the latest registered version
    latest_version = max(versions, key=lambda version: int(version.version))

    latest_version_number = latest_version.version

    print(f"Latest registered model version: " f"{latest_version_number}")

    # Get the current champion, if one exists
    try:
        current_champion = client.get_model_version_by_alias(model_name, champion_alias)

        print(f"Current champion version: " f"{current_champion.version}")

    except Exception:
        current_champion = None
        print("No existing champion model found.")

    # Promote the latest version by assigning the champion alias
    client.set_registered_model_alias(
        name=model_name, alias=champion_alias, version=latest_version_number
    )

    print(
        f"Model version {latest_version_number} "
        f"is now the '{champion_alias}' model."
    )


if __name__ == "__main__":
    promote_model()
