from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, APIRouter, BackgroundTasks, Form, Body, Depends,HTTPException, Header
from google.cloud import storage
from datetime import timedelta, datetime
from helper.store_script import *
import  os,uuid

app = FastAPI(title="GCS Ingest API", version="0.0.1")


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload_video")
async def upload_video(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    survey_id: str = Form(...),
    room_id: str = Form(...),
    scan_id: str = Form(...),
):

    start_time = datetime.now()
    if not GCS_BUCKET:
        raise HTTPException(status_code=500, detail="Server misconfigured: GCS_BUCKET not set")

    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported content type: {file.content_type}. Allowed: {sorted(ALLOWED_CONTENT_TYPES)}",
        )

    original_name = safe_filename(file.filename or "video.bin")
    object_id = str(uuid.uuid4())

    _, ext = os.path.splitext(original_name)
    if not ext:
        ext = ".mp4" if file.content_type == "video/mp4" else ""

    gcs_object_name = f"{GCS_PREFIX}/user_id={user_id}/survey_id={survey_id}/room_id={room_id}/scan_id={scan_id}/{object_id}{ext}"

    client = get_storage_client()
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(gcs_object_name)

    blob.chunk_size = 8 * 1024 * 1024

    bytes_written = 0
    try:
        with blob.open("wb", content_type=file.content_type) as gcs_f:
            while True:
                chunk = await file.read(8 * 1024 * 1024)  # 8 MiB
                if not chunk:
                    break
                bytes_written += len(chunk)
                if bytes_written > MAX_BYTES:
                    try:
                        blob.delete()
                    except Exception:
                        pass
                    raise HTTPException(status_code=413, detail=f"File too large. Max is {MAX_BYTES} bytes.")
                gcs_f.write(chunk)

    except HTTPException:
        raise
    except Exception as e:
        try:
            if blob.exists():
                blob.delete()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Upload failed: {type(e).__name__}: {e}")
    finally:
        await file.close()

    try:
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(seconds=SIGNED_URL_TTL_SECONDS),
            method="GET",
        )
    except Exception as e:
        signed_url = None

    return {
        "user_id": user_id,
        "survey_id": survey_id,
        "room_id": room_id,
        "scan_id": scan_id,
        "bucket": GCS_BUCKET,
        "object": gcs_object_name,
        "gs_uri": f"gs://{GCS_BUCKET}/{gcs_object_name}",
        "content_type": file.content_type,
        "bytes_written": bytes_written,
        "signed_url": signed_url,
        "signed_url_ttl_seconds": SIGNED_URL_TTL_SECONDS,
        "time": datetime.now() - start_time,

    }


@app.get("/")
async def root():
    return {"message": "Devlop 0.0.1 GCS ingest API"}


