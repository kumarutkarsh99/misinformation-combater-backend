from fastapi import APIRouter
from app.services import database_service
from collections import Counter
from google.cloud import firestore
from thefuzz import process as fuzzy_process
from app.services import ai_service

router = APIRouter()

@router.get("/heatmap")
async def get_heatmap_data():
    """Endpoint to provide rich data for the misinformation heatmap."""
    reports = database_service.get_reports_since(days=30)
    
    points = []
    for report in reports:
        location = report.get('location')
        
        if isinstance(location, firestore.GeoPoint):
            credibility_score = report.get('credibility_score', 50)
            intensity = (100 - credibility_score) / 100.0

            if credibility_score < 75:
                points.append({
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "report_summary": report.get("report_summary", "No summary available."),
                    "intensity": intensity
                })
            
    return {"points": points}

@router.get("/recentReports")
async def get_heatmap_data():
    """Endpoint to provide data for the misinformation heatmap."""
    reports = database_service.get_reports_since(days=30)

    result = []
    for report in reports:
        if(report.get('credibility_score') < 74):
            result.append(report)
    return result

@router.get("/categories")
async def get_category_data():
    """Endpoint to provide data for the category pie chart with fuzzy matching."""
    reports = database_service.get_reports_since(days=30)
    
    canonical_categories = [
        "Health", 
        "Political", 
        "Financial", 
        "Science", 
        "Social", 
        "Satire",
        "Geopolitics",
        "Other"
    ]
    
    raw_category_counts = Counter(report.get('category') for report in reports if report.get('category'))

    normalized_counts = Counter()
    for raw_category, count in raw_category_counts.items():
        best_match, score = fuzzy_process.extractOne(raw_category, canonical_categories)
        if score > 75:
            normalized_counts[best_match] += count
        else:
            normalized_counts["Other"] += count
            
    return normalized_counts
