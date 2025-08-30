from fastapi import APIRouter
from app.services import database_service
from collections import Counter
from google.cloud import firestore

router = APIRouter()

@router.get("/heatmap")
async def get_heatmap_data():
    """Endpoint to provide rich data for the misinformation heatmap."""
    reports = database_service.get_recent_reports(hours=48)
    
    points = []
    for report in reports:
        report_dict = report.to_dict()
        location = report_dict.get('location')
        
        if isinstance(location, firestore.GeoPoint):
            credibility_score = report_dict.get('credibility_score', 50)
            intensity = (100 - credibility_score) / 100.0

            points.append({
                "latitude": location.latitude,
                "longitude": location.longitude,
                "report_summary": report_dict.get("report_summary", "No summary available."),
                "intensity": intensity
            })
            
    return {"points": points}

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
