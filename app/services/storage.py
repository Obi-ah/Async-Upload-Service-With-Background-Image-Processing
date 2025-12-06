import io
from minio import Minio
from app.core.config import settings
from uuid import uuid4


client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_USE_SSL,
)


def ensure_bucket(bucket: str) -> None:
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)


def upload_bytes(bucket: str, data: bytes, content_type: str) -> tuple[str, str]:
    ensure_bucket(bucket)
    object_name = f"{uuid4().hex}"
    data_stream = io.BytesIO(data)
    size = len(data)
    client.put_object(
        bucket_name=bucket,
        object_name=object_name,
        data=data_stream,
        length=size,
        content_type=content_type,
    )

    protocol = "https" if settings.MINIO_USE_SSL else "http"
    url = f"{protocol}://{settings.MINIO_ENDPOINT}/{bucket}/{object_name}"

    return url, object_name