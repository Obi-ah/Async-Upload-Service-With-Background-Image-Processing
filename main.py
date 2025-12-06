from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine

app = FastAPI(title="Upload Service")

# Create tables (for demo; in real life, use Alembic)
Base.metadata.create_all(bind=engine)
