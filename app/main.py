from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.api.v1.endpoints import analysis, dashboard , trends

app = FastAPI(
    title="Misinformation Detector API",
    description="An API to analyze content for potential misinformation.",
    version="1.0.0"
)

origins = [
    "http://localhost:5173", 
    "http://localhost:8080",
    "https://misinformation-combater-frontend.vercel.app",
    "https://misinformation-combater-frontend-386097269689.europe-west1.run.app"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Misinformation Detector API!"}

app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(trends.router, prefix="/api/v1/trends", tags=["trends"])