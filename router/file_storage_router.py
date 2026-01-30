from fastapi import FastAPI, File, UploadFile, APIRouter, BackgroundTasks, Form, Body, Depends
from typing import Optional
from controller.gcs_controller import StorageController

router = APIRouter(
    prefix='/upload',
    tags=['File Storage']
)


@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    survey_id: str = Form(...),
    room_id: str = Form(...),
    scan_id: str = Form(...),


):

    store_dict = {
        "file": file,"user_id": user_id,"survey_id": survey_id,
        "room_id": room_id,"scan_id": scan_id
    }

    controller = StorageController(store_dict)
    job = controller.store_video()

    return job




