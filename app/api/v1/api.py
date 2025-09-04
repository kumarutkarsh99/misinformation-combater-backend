
from fastapi import APIRouter
from app.api.v1.endpoints import analysis

"""
API router configuration.
Includes the analysis endpoints under the /analysis prefix.
"""

api_router = APIRouter()
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])