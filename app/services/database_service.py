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


def get_reports_since(days: int):
    """Fetches all reports from the last X days as a list of dictionaries."""
    time_threshold = datetime.now(timezone.utc) - timedelta(days=days)
    reports_ref = db.collection('reports').where('timestamp', '>=', time_threshold)
    # Convert each document to a dictionary
    return [doc.to_dict() for doc in reports_ref.stream()]