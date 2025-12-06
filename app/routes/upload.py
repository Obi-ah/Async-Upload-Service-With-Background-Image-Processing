import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.upload import Upload, UploadStatus
from app.schemas.upload import (
    UploadResponse,
    UploadStatusResponse,
    UploadResultResponse,
)
from app.services.storage import upload_bytes
from app.core.config import settings
from app.worker.celery_app import celery_app

router = APIRouter(prefix="/upload", tags=["upload"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image uploads are allowed.",
        )

    data = await file.read()
    # Store original in MinIO
    original_url, object_name = upload_bytes(
        settings.MINIO_BUCKET_ORIGINAL,
        data,
        content_type=file.content_type,
    )

    upload = Upload(
        original_url=original_url,
        status=UploadStatus.PENDING,
        bucket=settings.MINIO_BUCKET_ORIGINAL,
        object_name=object_name,
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)

    # Enqueue background processing
    celery_app.send_task(
        "app.worker.tasks.process_upload",
        args=[str(upload.id)],
        queue="uploads",
    )

    return UploadResponse(
        id=upload.id,
        status=upload.status,
        original_url=upload.original_url,
    )


@router.get("/{upload_id}/status", response_model=UploadStatusResponse)
def get_upload_status(upload_id: uuid.UUID, db: Session = Depends(get_db)):
    upload = db.get(Upload, upload_id)
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    return UploadStatusResponse(
        id=upload.id,
        status=upload.status,
        error_message=upload.error_message,
    )


@router.get("/{upload_id}/result", response_model=UploadResultResponse)
def get_upload_result(upload_id: uuid.UUID, db: Session = Depends(get_db)):
    upload = db.get(Upload, upload_id)
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    return UploadResultResponse(
        id=upload.id,
        status=upload.status,
        original_url=upload.original_url,
        processed_url=upload.processed_url,
        thumbnail_url=upload.thumbnail_url,
        error_message=upload.error_message,
    )