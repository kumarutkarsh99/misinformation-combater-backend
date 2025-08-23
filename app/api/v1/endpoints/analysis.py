from fastapi import APIRouter, HTTPException
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services import scraping_service, search_service, ai_service
from urllib.parse import urlparse

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(request: AnalysisRequest):
    content_to_analyze = request.content
    
    is_url = urlparse(content_to_analyze).scheme in ('http', 'https')
    
    if is_url:
        scraped_text = scraping_service.scrape_url(content_to_analyze)
        if not scraped_text:
            raise HTTPException(status_code=400, detail="Could not retrieve content from the URL.")
        
        # ADVANCED LOGIC: First, summarize the entire article
        summary_of_article = ai_service.summarize_full_text(scraped_text)
        
        # THEN, generate a search query from that summary
        query_text = ai_service.generate_search_query(summary_of_article)
    else:
        query_text = content_to_analyze

    # The rest of the process remains the same
    search_results = search_service.search_credible_sources(query_text)
    
    search_context = ""
    if search_results and "items" in search_results:
        snippets_with_urls = [
            f"Source URL: {item.get('link', '')}\nSnippet: {item.get('snippet', '')}"
            for item in search_results["items"]
        ]
        search_context = "\n---\n".join(snippets_with_urls)

    if not search_context:
        search_context = "No information found in credible sources."

    analysis_result = ai_service.analyze_content_with_ai(
        user_content=content_to_analyze,
        search_context=search_context
    )

    if analysis_result.get("credibility_score", -1) == -1:
        raise HTTPException(status_code=500, detail="Failed to get analysis from the AI model.")

    return AnalysisResponse(**analysis_result)