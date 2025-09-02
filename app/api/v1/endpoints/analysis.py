from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from app.schemas.analysis import AnalysisResponse
from app.services import scraping_service, search_service, ai_service
from urllib.parse import urlparse
from app.services.database_service import Report, save_report
from datetime import datetime, timezone
from typing import Optional
from google.cloud import firestore
from app.services import ai_service

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(
    content: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    
    content_to_analyze = ""

    if file:
        file_contents = await file.read()
        mime_type = file.content_type

        if "audio" in mime_type:
            content_to_analyze = ai_service.transcribe_audio(file_contents, mime_type)
        elif "image" in mime_type:
            content_to_analyze = ai_service.analyze_image_with_ai(file_contents, mime_type)
        elif "pdf" in mime_type:
            content_to_analyze = ai_service.extract_text_from_pdf(file_contents)
        elif "openxmlformats-officedocument" in mime_type: # This is for .docx
            content_to_analyze = ai_service.extract_text_from_doc(file_contents)
        elif "text" in mime_type:
            content_to_analyze = file_contents.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {mime_type}. Please upload an image, audio, PDF, DOCX, or text file.")

        if not content_to_analyze:
            raise HTTPException(status_code=500, detail=f"Could not extract content from the uploaded file.")

    elif content:
        content_to_analyze = content
    else:
        raise HTTPException(status_code=400, detail="No content provided. Please provide text, a URL, or a file.")

    is_url = urlparse(content_to_analyze).scheme in ('http', 'https')
    
    if is_url:
        scraped_text = scraping_service.scrape_url(content_to_analyze)
        if not scraped_text:
            raise HTTPException(status_code=400, detail="Could not retrieve content from the URL.")
        summary_of_article = ai_service.summarize_full_text(scraped_text)
        query_text = ai_service.generate_search_query(summary_of_article)
    else:
        query_text = content_to_analyze

    search_results = search_service.search_credible_sources(query_text)
    
    search_context = ""
    if search_results and "items" in search_results:
        snippets_with_info = []
        for item in search_results["items"]:
            url = item.get('link', '')
            domain_name = urlparse(url).netloc
            snippets_with_info.append(
                f"Source Name: {domain_name}\nSource URL: {url}\nSnippet: {item.get('snippet', '')}"
            )
        search_context = "\n---\n".join(snippets_with_info)

    if not search_context:
        search_context = "No information found in credible sources."

    analysis_result = ai_service.analyze_content_with_ai(
        user_content=content_to_analyze,
        search_context=search_context
    )

    if analysis_result.get("credibility_score", -1) == -1:
        raise HTTPException(status_code=500, detail="Failed to get analysis from the AI model.")
    
    if analysis_result.get("credibility_score", -1) != -1:
        if latitude and longitude:
            try:
                report_to_save = Report(
                    timestamp=datetime.now(timezone.utc),
                    credibility_score=analysis_result["credibility_score"],
                    category=analysis_result["category"],
                    report_summary=analysis_result["report_summary"],
                    latitude = latitude,
                    longitude = longitude,
                    state = ai_service.get_state_from_coords(latitude, longitude),
                    location=firestore.GeoPoint(latitude, longitude),
                    metrics=analysis_result["metrics"],
                    source_domains=[source.get('url', '') for source in analysis_result.get("sources", [])]
                )
                save_report(report_to_save)
            except Exception as e:
                print(f"Failed to save report to database: {e}")

    return AnalysisResponse(**analysis_result)