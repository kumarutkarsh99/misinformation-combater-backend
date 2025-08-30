from fastapi import APIRouter
from app.services import database_service
from collections import Counter
from datetime import datetime, timedelta, timezone
from thefuzz import process as fuzzy_process
from itertools import chain
from urllib.parse import urlparse
from collections import defaultdict

router = APIRouter()

@router.get("/traffic")
async def get_traffic_data():
    """
    Returns a single JSON object containing daily, weekly, and monthly
    traffic data, including a specific count for misinformation reports
    for each time bucket.
    """
    reports = database_service.get_reports_since(days=30)
    now = datetime.now(timezone.utc)

    # --- Daily Data (Last 24 hours by hour) ---
    daily_threshold = now - timedelta(days=1)
    # Use a dictionary to store counts for each hour
    hourly_stats = defaultdict(lambda: {"reports": 0, "total_misinfo_count": 0})
    
    daily_reports = [r for r in reports if r['timestamp'] >= daily_threshold]
    for report in daily_reports:
        hour_key = report['timestamp'].strftime('%H')
        hourly_stats[hour_key]["reports"] += 1
        if report.get('credibility_score', 100) < 75:
            hourly_stats[hour_key]["total_misinfo_count"] += 1

    daily_data = []
    for i in range(23, -1, -1):
        hour = (now - timedelta(hours=i)).strftime('%H')
        stats = hourly_stats[hour]
        daily_data.append({
            "hour": f"{hour}:00",
            "reports": stats["reports"],
            "total_misinfo_count": stats["total_misinfo_count"]
        })
    daily_total_misinfo = sum(stats['total_misinfo_count'] for stats in hourly_stats.values())

    # --- Weekly Data (Last 7 days by day name) ---
    weekly_threshold = now - timedelta(days=7)
    day_stats = defaultdict(lambda: {"reports": 0, "total_misinfo_count": 0})
    
    weekly_reports = [r for r in reports if r['timestamp'] >= weekly_threshold]
    for report in weekly_reports:
        day_key = report['timestamp'].strftime('%A')
        day_stats[day_key]["reports"] += 1
        if report.get('credibility_score', 100) < 75:
            day_stats[day_key]["total_misinfo_count"] += 1
    
    weekly_data = []
    for i in range(6, -1, -1):
        day = (now - timedelta(days=i)).strftime('%A')
        stats = day_stats[day]
        weekly_data.append({
            "day": day,
            "reports": stats["reports"],
            "total_misinfo_count": stats["total_misinfo_count"]
        })

    # --- Monthly Data (Last 30 days by date) ---
    date_stats = defaultdict(lambda: {"reports": 0, "total_misinfo_count": 0})
    
    for report in reports:
        date_key = report['timestamp'].strftime('%Y-%m-%d')
        date_stats[date_key]["reports"] += 1
        if report.get('credibility_score', 100) < 75:
            date_stats[date_key]["total_misinfo_count"] += 1

    monthly_data = []
    for i in range(29, -1, -1):
        date = (now - timedelta(days=i)).strftime('%Y-%m-%d')
        stats = date_stats[date]
        monthly_data.append({
            "date": date,
            "reports": stats["reports"],
            "total_misinfo_count": stats["total_misinfo_count"]
        })

    return {
        "daily": {
            "traffic": daily_data,
            "total_misinfo_count": daily_total_misinfo
        },
        "weekly": {
            "traffic": weekly_data
        },
        "monthly": {
            "traffic": monthly_data
        }
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
        "score": round(sum_credibility / total_reports)
    }

@router.get("/sources")
async def get_sources_data():
    """
    Endpoint to get a list of the most frequently used source domains
    from reports in the last 48 hours, represented as percentages.
    """
    reports = database_service.get_reports_since(days=2)
    
    all_domains = list(chain.from_iterable(
        [urlparse(url).netloc for url in report.get('source_domains', [])] 
        for report in reports
    ))
    
    total_domains = len(all_domains)
    if total_domains == 0:
        return {"top_sources": []}
        
    domain_counts = Counter(all_domains)
    
    top_sources = [
        {
            "domain": domain, 
            "percentage": round((count / total_domains) * 100)
        }
        for domain, count in domain_counts.most_common(10)
    ]
            
    return {"top_sources": top_sources}