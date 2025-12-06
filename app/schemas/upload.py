import uuid
from datetime import datetime
from pydantic import BaseModel, HttpUrl
from app.models.upload import UploadStatus


class UploadResponse(BaseModel):
    id: uuid.UUID
    status: UploadStatus
    original_url: HttpUrl | None = None

    class Config:
        from_attributes = True


class UploadStatusResponse(BaseModel):
    id: uuid.UUID
    status: UploadStatus
    error_message: str | None = None

    class Config:
        from_attributes = True


class UploadResultResponse(BaseModel):
    id: uuid.UUID
    status: UploadStatus
    original_url: HttpUrl | None = None
    processed_url: HttpUrl | None = None
    thumbnail_url: HttpUrl | None = None
    error_message: str | None = None

    class Config:
        from_attributes = True