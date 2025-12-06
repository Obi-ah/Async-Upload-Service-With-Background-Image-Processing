# Async Upload Service With Background Image Processing

## Overview
This service provides an API for uploading images and processing them asynchronously. Uploaded images are stored in MinIO, and a Celery worker performs background processing such as resizing, compressing, and generating thumbnails. Clients can poll for processing status and retrieve final processed image URLs.

## Tech Stack
- FastAPI  
- Celery  
- Redis (message broker)  
- MinIO (S3-compatible storage)  
- Pillow (image processing)  
- SQLAlchemy

## Setup Instructions

### 1. Install dependencies
```
pip install -r requirements.txt
```

### 2. Start Redis
```
redis-server
```

Or via Docker:
```
docker run -p 6379:6379 redis
```

### 3. Start MinIO
```
docker run -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

Create buckets:
- uploads-original  
- uploads-processed  

Make them publicly readable:
```
mc alias set local http://localhost:9000 minioadmin minioadmin
mc anonymous set download local/uploads-original
mc anonymous set download local/uploads-processed
```

### 4. Start FastAPI server
```
uvicorn app.main:app --reload
```

### 5. Start Celery worker
```
celery -A app.worker.celery_app.celery_app worker -Q uploads --loglevel=info
```

## How to Use the API

### 1. Upload an image
```
POST /upload
```

Example:
```
curl -X POST http://127.0.0.1:8000/upload \
  -F "file=@example.png"
```

Response:
```
{
  "id": "<uuid>",
  "status": "pending",
  "original_url": "http://localhost:9000/uploads-original/<file>"
}
```

### 2. Check upload status
```
GET /upload/{id}/status
```
Possible statuses: pending, processing, completed, failed.

### 3. Get processed results
```
GET /upload/{id}/result
```

Response includes:
- original_url  
- processed_url  
- thumbnail_url  
- status  

## Summary
This service demonstrates a complete asynchronous image-processing pipeline using FastAPI, Celery, Redis, and MinIO. It supports file upload, background processing, and result retrieval through simple REST endpoints.
