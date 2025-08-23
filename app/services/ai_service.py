import google.generativeai as genai
from app.core.config import settings
import json

# Configure the new Gemini API key
genai.configure(api_key=settings.GEMINI_API_KEY)


def summarize_full_text(full_text: str) -> str:
    """Uses Gemini to create a concise summary of a long document."""
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    
    # We use a shorter text snippet to avoid using too many tokens for a simple summary
    prompt = f"""
    Please read the following document and provide a concise, one-paragraph summary of its key ideas.

    DOCUMENT:
    "{full_text[:8000]}"
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error summarizing full text: {e}")
        # Fallback to just using the start of the text
        return full_text[:1000]


def generate_search_query(text_to_summarize: str) -> str:
    """Uses Gemini to generate a concise search query from a block of text."""
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    
    prompt = f"""
    Read the following text and summarize it into a clean, simple search engine query of 5-10 keywords.
    
    TEXT:
    "{text_to_summarize}"

    SEARCH QUERY:
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating search query: {e}")
        # Fallback to using the raw text if the AI fails
        return text_to_summarize[:100]


def analyze_content_with_ai(user_content: str, search_context: str) -> dict:
    """
    Analyzes user content using the Google AI Gemini API.
    """
    model = genai.GenerativeModel("gemini-1.5-pro-latest")

    safety_settings = {
        'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
        'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
        'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_ONLY_HIGH',
        'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_ONLY_HIGH',
    }
    
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
      "sources": ["<A list of the top 3 'Source URL' values provided in the context. Do not make up URLs. If no URLs are in the context, return an empty list.>"]
    }}
    """

    try:
        response = model.generate_content(
            prompt,
            safety_settings=safety_settings
        )
        
        if not response.parts:
            return {
                "credibility_score": -1,
                "summary": "Response blocked due to safety concerns.",
                "analysis": "The AI's safety filters were triggered by the input content or the search results.",
                "sources": []
            }

        raw_text = response.text.strip()
        json_text = raw_text[raw_text.find('{'):raw_text.rfind('}')+1]
        
        return json.loads(json_text)
    except Exception as e:
        print(f"Error calling Google AI: {e}")
        return {
            "credibility_score": -1,
            "summary": "Could not analyze the content due to an internal error.",
            "analysis": f"An error occurred while communicating with the AI model: {e}",
            "sources": []
        }