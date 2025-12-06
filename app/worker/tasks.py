import uuid
from celery import shared_task
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.upload import Upload, UploadStatus
from app.services.storage import upload_bytes
from app.services.image_processor import resize_image, create_thumbnail
from minio import Minio
from app.core.config import settings

# Direct MinIO client for reading original file
minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_USE_SSL,
)


@shared_task(name="app.worker.tasks.process_upload")
def process_upload_task(upload_id: str):
    db: Session = SessionLocal()
    try:
        uid = uuid.UUID(upload_id)
        upload = db.get(Upload, uid)
        if not upload or not upload.bucket or not upload.object_name:
            return

        upload.status = UploadStatus.PROCESSING
        db.commit()

        # Download original from MinIO
        resp = minio_client.get_object(upload.bucket, upload.object_name)
        original_bytes = resp.read()
        resp.close()
        resp.release_conn()

        # Resize + compress
        resized_bytes = resize_image(original_bytes)
        thumb_bytes = create_thumbnail(original_bytes)

        # Store processed & thumb
        processed_url, _ = upload_bytes(
            settings.MINIO_BUCKET_PROCESSED,
            resized_bytes,
            content_type="image/jpeg",
        )
        thumb_url, _ = upload_bytes(
            settings.MINIO_BUCKET_PROCESSED,
            thumb_bytes,
            content_type="image/jpeg",
        )

        upload.processed_url = processed_url
        upload.thumbnail_url = thumb_url
        upload.status = UploadStatus.COMPLETED
        upload.error_message = None
        db.commit()

    except Exception as e:
        if "upload" in locals() and upload:
            upload.status = UploadStatus.FAILED
            upload.error_message = str(e)
            db.commit()
    finally:
        db.close()