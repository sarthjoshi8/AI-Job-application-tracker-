import logging
import os
from google.cloud import secretmanager
from app.core.config import settings

logger = logging.getLogger(__name__)

def get_secret(secret_id: str, default: str = "") -> str:
    """
    Fetches a secret payload from Google Secret Manager.
    Falls back to environment variable if Secret Manager call fails or is not in GCP.
    """
    env_val = os.getenv(secret_id.upper().replace("-", "_"))
    if env_val:
        return env_val

    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{settings.PROJECT_ID}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logger.warning(f"Could not load secret {secret_id} from Secret Manager: {e}. Falling back to default.")
        return default
