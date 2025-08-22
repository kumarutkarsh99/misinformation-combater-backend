from pydantic import BaseModel
from typing import List, Optional

class AnalysisRequest(BaseModel):
    content: str # Can be a URL or a block of text

class AnalysisResponse(BaseModel):
    credibility_score: int
    summary: str
    analysis: str
    sources: List[str]