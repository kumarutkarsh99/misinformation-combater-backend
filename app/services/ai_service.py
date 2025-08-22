import vertexai
from vertexai.generative_models import GenerativeModel, Part
from app.core.config import settings
import json

# Initialize Vertex AI
vertexai.init(project=settings.GCP_PROJECT, location=settings.GCP_LOCATION)

def analyze_content_with_ai(user_content: str, search_context: str) -> dict:
    """
    Analyzes user content using Gemini, providing search results as context.
    """
    model = GenerativeModel("gemini-1.5-pro-001")

    prompt = f"""
    You are a neutral, unbiased fact-checking analyst. Your task is to analyze a piece of user-submitted content against a set of search results from trusted, credible sources and provide an educational report.

    **User Content:**
    "{user_content}"

    **Trusted Source Snippets for Context:**
    "{search_context}"

    **Your Task:**
    Respond ONLY with a JSON object with the following structure:
    {{
      "credibility_score": <An integer from 0 (Highly Misleading) to 100 (Highly Credible)>,
      "summary": "<A brief, neutral summary of what the trusted sources say about this topic.>",
      "analysis": "<Explain WHY the user's content might be misleading in a simple, educational way. Identify specific manipulative techniques like emotional language, false urgency, or unsourced claims if present.>",
      "sources": ["<A list of up to 3 relevant source URLs from the provided context>"]
    }}
    """

    try:
        response = model.generate_content(prompt)
        
        # Clean the response to extract the JSON object
        raw_text = response.text.strip()
        json_text = raw_text[raw_text.find('{'):raw_text.rfind('}')+1]
        
        return json.loads(json_text)
    except Exception as e:
        print(f"Error calling Vertex AI: {e}")
        # Return a default error structure
        return {
            "credibility_score": -1,
            "summary": "Could not analyze the content due to an internal error.",
            "analysis": f"An error occurred while communicating with the AI model: {e}",
            "sources": []
        }