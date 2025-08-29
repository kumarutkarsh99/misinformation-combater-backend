from fastapi import APIRouter
from app.services import database_service
from collections import Counter

router = APIRouter()

@router.get("/heatmap")
async def get_heatmap_data():
    """Endpoint to provide data for the misinformation heatmap."""
    reports = database_service.get_recent_reports(hours=48)

    points = []
    for report in reports:
        report_dict = report.to_dict()
        location = report_dict.get('location')

        # Firestore returns GeoPoint objects, so access attributes instead of keys
        if location and hasattr(location, "latitude") and hasattr(location, "longitude"):
            points.append([
                location.latitude,
                location.longitude,
                0.5
            ])
    return points


@router.get("/categories")
async def get_category_data():
    """Endpoint to provide data for the category pie chart."""
    reports = database_service.get_recent_reports(hours=48)
    category_counts = Counter(report.to_dict().get('category') for report in reports)
    return category_counts
