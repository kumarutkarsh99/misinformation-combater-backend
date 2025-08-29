from pydantic import BaseModel
from typing import List, Dict, Optional

class AnalysisRequest(BaseModel):
    content: str
    latitude: Optional[float] = None 
    longitude: Optional[float] = None

class Metrics(BaseModel):
    clarity: int
    tone: int
    correctness: int
    originality: int

class RawData(BaseModel):
    ts: int

class Source(BaseModel):
    name: str
    url: str
    credibility_score: int

class AnalysisResponse(BaseModel):
    credibility_score: int
    category: str
    key_entities: List[str]
    report_summary: str
    analysis: str
    metrics: Metrics
    sources: List[Source]
    formal_report: Optional[str] = None
    raw: RawData