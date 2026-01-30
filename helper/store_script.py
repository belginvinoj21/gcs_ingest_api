
import os
from google.cloud import storage
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "second-raceway-477108-k9-4fb3bc641e0e.json"


GCP_PROJECT = os.getenv("second-raceway-477108-k9")
GCS_BUCKET = os.getenv("GCS_BUCKET", "bundlebox-rfdetr-uploads")
GCS_PREFIX = os.getenv("GCS_PREFIX", "uploads")
SIGNED_URL_TTL_SECONDS = int(os.getenv("SIGNED_URL_TTL_SECONDS", "3600"))  # 1 hour default
MAX_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(500 * 1024 * 1024)))

ALLOWED_CONTENT_TYPES = {
    "video/mp4",
    "video/quicktime",     # .mov
    "video/x-matroska",    # .mkv
    "video/webm",
    "video/avi",
    "video/x-msvideo",
}


def get_storage_client() -> storage.Client:
    return storage.Client(project=GCP_PROJECT) if GCP_PROJECT else storage.Client()

def safe_filename(name: str) -> str:
    base = os.path.basename(name or "upload.bin")
    base = base.replace(" ", "_")
    return "".join(ch for ch in base if ch.isalnum() or ch in "._-")