from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title="Misinformation Detector API",
    description="An API to analyze content for potential misinformation.",
    version="1.0.0"
)

origins = [
    "http://localhost:5173",  # Your local frontend development server
    "http://localhost:3000",  # A common alternative local port
    "https://misinformation-combater-frontend.vercel.app", # <-- REPLACE THIS
    "https://misinformation-combater-frontend-386097269689.europe-west1.run.app"
]

# NEW: Add the CORSMiddleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Misinformation Detector API!"}

app.include_router(api_router, prefix="/api/v1")