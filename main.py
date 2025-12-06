from fastapi import FastAPI
from app.routes.upload import router as upload_router
from app.db.base import Base
from app.db.session import engine

app = FastAPI(title="Upload Service")

Base.metadata.create_all(bind=engine)

app.include_router(upload_router)