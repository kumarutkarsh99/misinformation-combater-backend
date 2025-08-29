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
            credibility_score = report_dict.get('credibility_score', 50)
            intensity = (100 - credibility_score) / 100.0
            points.append([
                location.latitude,
                location.longitude,
                intensity 
            ])
    return points

@router.get("/recentReports")
async def get_heatmap_data():
    """Endpoint to provide data for the misinformation heatmap."""
    reports = database_service.get_recent_reports(hours=48)

    result = []
    for report in reports:
        report_dict = report.to_dict()

        location = report_dict.get("location")
        if location and hasattr(location, "latitude") and hasattr(location, "longitude"):
            report_dict["location"] = {
                "latitude": location.latitude,
                "longitude": location.longitude
            }

        result.append(report_dict)

    return result


@router.get("/categories")
async def get_category_data():
    """Endpoint to provide data for the category pie chart."""
    reports = database_service.get_recent_reports(hours=48)
    category_counts = Counter(report.to_dict().get('category') for report in reports)
    return category_counts
