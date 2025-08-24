import requests
from typing import Optional, Dict, Any
from app.core.config import settings

def search_credible_sources(query: str) -> Optional[Dict[str, Any]]:
    """Searches a query using the configured credible sources search engine."""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": settings.SEARCH_API_KEY,
        "cx": settings.SEARCH_ENGINE_ID,
        "q": query,
        "num": 5
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error calling Search API: {e}")
        return None