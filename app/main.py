from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title="Misinformation Detector API",
    description="An API to analyze content for potential misinformation.",
    version="1.0.0"
)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Misinformation Detector API!"}

app.include_router(api_router, prefix="/api/v1")