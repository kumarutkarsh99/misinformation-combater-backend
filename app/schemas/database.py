from pydantic import BaseModel, ConfigDict
from typing import List, Dict
from datetime import datetime
from google.cloud.firestore_v1 import GeoPoint

class Report(BaseModel):
    """
    Pydantic model for a single document in the 'reports' collection.
    This model is used when writing new report data to Firestore.
    """
    timestamp: datetime
    credibility_score: int
    category: str
    location: GeoPoint
    latitude: float
    longitude: float
    state: str
    source_domains: List[str]
    report_summary: str
    metrics: Dict[str, int]

    model_config = ConfigDict(arbitrary_types_allowed=True)



