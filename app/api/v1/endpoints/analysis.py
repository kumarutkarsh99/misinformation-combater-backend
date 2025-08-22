from fastapi import APIRouter, HTTPException
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services import scraping_service, search_service, ai_service
from urllib.parse import urlparse

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(request: AnalysisRequest):
    content_to_analyze = request.content
    
    # Check if the content is a URL
    is_url = urlparse(content_to_analyze).scheme in ('http', 'https')
    
    if is_url:
        scraped_text = scraping_service.scrape_url(content_to_analyze)
        if not scraped_text:
            raise HTTPException(status_code=400, detail="Could not retrieve content from the URL.")
        query_text = scraped_text[:500] # Use the first 500 chars for a search query
    else:
        query_text = content_to_analyze

    # Step 2: Get context from credible sources
    search_results = search_service.search_credible_sources(query_text)
    
    search_context = ""
    if search_results and "items" in search_results:
        # Create a simple context string from search result snippets
        snippets = [item.get("snippet", "") for item in search_results["items"]]
        search_context = " ".join(snippets)

    if not search_context:
        # Handle cases with no search results gracefully
        search_context = "No information found in credible sources."

    # Step 3: Call the AI for the final analysis
    analysis_result = ai_service.analyze_content_with_ai(
        user_content=content_to_analyze,
        search_context=search_context
    )

    if analysis_result.get("credibility_score", -1) == -1:
        raise HTTPException(status_code=500, detail="Failed to get analysis from the AI model.")

    return AnalysisResponse(**analysis_result)