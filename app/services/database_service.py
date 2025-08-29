from google.cloud import firestore
from app.core.config import settings
from app.schemas.database import Report
from datetime import datetime, timezone, timedelta

db = firestore.Client(project=settings.GCP_PROJECT, database="misinfo-reports")

print("Firestore client initialized successfully.")

def save_report(report_data: Report):
    """Saves a report document to the 'reports' collection."""
    try:
        reports_collection = db.collection('reports')
        reports_collection.add(report_data.model_dump())
        print(f"Successfully saved report for location: {report_data.location}")
    except Exception as e:
        print(f"Error saving report to Firestore: {e}")


def get_recent_reports(hours: int):
    """Fetches all reports from the last X hours."""
    time_threshold = datetime.now(timezone.utc) - timedelta(hours=hours)
    reports_ref = db.collection('reports').where('timestamp', '>=', time_threshold)
    return reports_ref.stream()