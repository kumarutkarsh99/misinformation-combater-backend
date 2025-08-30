from fastapi import APIRouter
from app.services import database_service
from collections import Counter
from datetime import datetime, timedelta, timezone

router = APIRouter()

@router.get("/traffic")
async def get_traffic_data():
    """
    Returns a single JSON object containing daily, weekly, and monthly
    traffic data based on the number of reports processed.
    """
    # Fetch all reports from the last 30 days once.
    reports = database_service.get_reports_since(days=30)
    now = datetime.now(timezone.utc)

    # --- Daily Traffic (Last 24 hours by hour) ---
    daily_threshold = now - timedelta(days=1)
    daily_reports = [r for r in reports if r['timestamp'] >= daily_threshold]
    hourly_counts = Counter(r['timestamp'].strftime('%H') for r in daily_reports)
    
    daily_data = []
    for i in range(23, -1, -1):
        hour = (now - timedelta(hours=i)).strftime('%H')
        daily_data.append({
            "hour": f"{hour}:00",
            "reports": hourly_counts.get(hour, 0)
        })

    # --- Weekly Traffic (Last 7 days by day name) ---
    weekly_threshold = now - timedelta(days=7)
    weekly_reports = [r for r in reports if r['timestamp'] >= weekly_threshold]
    day_counts = Counter(r['timestamp'].strftime('%A') for r in weekly_reports)
    
    weekly_data = []
    for i in range(6, -1, -1):
        day = (now - timedelta(days=i)).strftime('%A')
        weekly_data.append({
            "day": day,
            "reports": day_counts.get(day, 0)
        })

    # --- Monthly Traffic (Last 30 days by date) ---
    date_counts = Counter(r['timestamp'].strftime('%Y-%m-%d') for r in reports)
    
    monthly_data = []
    for i in range(29, -1, -1):
        date = (now - timedelta(days=i)).strftime('%Y-%m-%d')
        monthly_data.append({
            "date": date,
            "reports": date_counts.get(date, 0)
        })

    return {
        "daily": daily_data,
        "weekly": weekly_data,
        "monthly": monthly_data
    }

@router.get("/radar")
async def get_radar_data():
    """
    Endpoint to provide the average of all metrics for the radar chart,
    calculated from reports in the last 48 hours.
    """
    reports = database_service.get_reports_since(days=2)
    
    total_reports = 0
    valid_reports = 0
    sum_clarity = 0
    sum_tone = 0
    sum_correctness = 0
    sum_originality = 0
    sum_credibility = 0
    
    for report in reports:
        metrics = report.get("metrics")
        total_reports += 1
        if metrics:
            valid_reports += 1
            sum_clarity += metrics.get("clarity", 0)
            sum_tone += metrics.get("tone", 0)
            sum_correctness += metrics.get("correctness", 0)
            sum_originality += metrics.get("originality", 0)
            
        sum_credibility += report.get("credibility_score", 0)

    print(total_reports, sum_clarity, sum_tone,sum_correctness,sum_originality,sum_credibility)
            
    if total_reports == 0:
        return {
            "clarity": 0,
            "tone": 0,
            "correctness": 0,
            "originality": 0,
            "credibility_score": 0
        }

    return {
        "clarity": round(sum_clarity / valid_reports),
        "tone": round(sum_tone / valid_reports),
        "correctness": round(sum_correctness / valid_reports),
        "originality": round(sum_originality / valid_reports),
        "credibility_score": round(sum_credibility / total_reports)
    }
