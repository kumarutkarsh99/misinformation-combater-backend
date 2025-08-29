import google.generativeai as genai
from app.core.config import settings
import json
import time
import re

genai.configure(api_key=settings.GEMINI_API_KEY)

SAFETY_SETTINGS = {
    'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_ONLY_HIGH',
    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_ONLY_HIGH',
}

def summarize_full_text(full_text: str) -> str:
    """Uses Gemini to create a concise summary of a long document."""
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    
    prompt = f"""
    Please read the following document and provide a concise, one-paragraph summary of its key ideas.

    DOCUMENT:
    "{full_text[:8000]}"
    """
    
    try:
        response = model.generate_content(prompt, safety_settings=SAFETY_SETTINGS)
        
        if not response.parts:
            print("Error summarizing full text: Response was blocked by safety filters.")
            return full_text[:1000] # Fallback
            
        return response.text.strip()
    except Exception as e:
        print(f"Error summarizing full text: {e}")
        return full_text[:1000] # Fallback


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
        response = model.generate_content(prompt, safety_settings=SAFETY_SETTINGS)

        if not response.parts:
            print("Error generating search query: Response was blocked by safety filters.")
            return text_to_summarize[:100] # Fallback

        return response.text.strip()
    except Exception as e:
        print(f"Error generating search query: {e}")
        return text_to_summarize[:100] # Fallback


def analyze_content_with_ai(user_content: str, search_context: str) -> dict:
    """
    Analyzes user content and generates a full, merged report card.
    """
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    raw_text = ""

    prompt = f"""
    You are a neutral, unbiased fact-checking analyst. Your task is to analyze user-submitted content against trusted search results and provide a detailed report as a JSON object.

    **User Content:**
    "{user_content}"

    **Trusted Source Snippets for Context:**
    "{search_context}"

    **Your Task:**
    Respond ONLY with a JSON object with the following structure. Do not add any text before or after the JSON object.
    {{
      "credibility_score": <An integer from 0 (Highly Misleading) to 100 (Highly Credible)>,
      "category": "<A short category like 'Health Misinformation', 'Financial Scam', 'Political Disinformation', or 'Satire'>",
      "key_entities": ["<A list of the main people, places, or topics mentioned>"],
      "report_summary": "<A brief, one-sentence summary of why the content is misleading.>",
      "analysis": "<A detailed, one-paragraph explanation of why the content is misleading, based on the context. Explain the manipulative techniques used, if any.>",
      "metrics": {{
          "clarity": <An integer from 0 (Very Unclear) to 100 (Very Clear)>,
          "tone": <An integer from 0 (Very Negative/Aggressive) to 100 (Very Positive/Neutral)>,
          "correctness": <An integer from 0 (Factually Incorrect) to 100 (Factually Correct) based on the context>,
          "originality": <An integer from 0 (Plagiarized) to 100 (Highly Original)>
      }},
      "sources": [
          {{
              "name": "<The 'Source Name' of the first source from the context>",
              "url": "<The 'Source URL' of the first source from the context>",
              "credibility_score": <An integer from 0 to 100 representing the credibility of this specific source>
          }},
          {{
              "name": "<The 'Source Name' of the second source from the context>",
              "url": "<The 'Source URL' of the second source from the context>",
              "credibility_score": <An integer from 0 to 100 representing the credibility of this specific source>
          }}
      ],
      "formal_report": "<Generate a formal, multi-paragraph report suitable for submission to authorities. It should start with 'To Whom It May Concern,', state the category, summarize the claim, explain why it is misleading based on the trusted sources, and end with a request for review. Use neutral and professional language. Use '\\n' for new lines.>",
      "raw": {{ "ts": 0 }}
    }}
    """

    try:
        response = model.generate_content(
            prompt,
            safety_settings=SAFETY_SETTINGS
        )
        
        if not response.parts:
            return {
                "credibility_score": -1, "category": "Error", "key_entities": [],
                "report_summary": "Response blocked due to safety concerns.",
                "analysis": "The AI's safety filters were triggered by the input content or the search results.",
                "metrics": {"clarity": 0, "tone": 0, "correctness": 0, "originality": 0},
                "sources": [],
                "formal_report": "Could not generate a report because the content was blocked by safety filters.",
                "raw": {"ts": int(time.time() * 1000)}
            }

        raw_text = response.text.strip()
        
        json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found in the AI response.")
        
        json_text = json_match.group(0)
        
        result = json.loads(json_text)
        result['raw']['ts'] = int(time.time() * 1000)

        if result.get("credibility_score", 0) > 74:
            result.pop("formal_report", None)

        return result
    except Exception as e:
        print("\n--- DEBUG: FAILED TO PARSE AI RESPONSE ---")
        print("Raw text received from AI:")
        print(raw_text)
        print("-------------------------------------------\n")

        print(f"Error calling Google AI: {e}")
        return {
            "credibility_score": -1, "category": "Error", "key_entities": [],
            "report_summary": "Could not analyze the content due to an internal error.",
            "analysis": f"An error occurred while communicating with the AI model: {e}",
            "metrics": {"clarity": 0, "tone": 0, "correctness": 0, "originality": 0},
            "sources": [],
            "formal_report": "Could not generate a report due to an internal error.",
            "raw": {"ts": int(time.time() * 1000)}
        }

def get_state_from_coords(latitude: float, longitude: float) -> str:
    """Uses Gemini to get the Indian state from latitude and longitude."""
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    prompt = f"What Indian state is at latitude {latitude}, longitude {longitude}? Respond with only the name of the state, or 'Unknown' if it's not in India."
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error in reverse geocoding: {e}")
        return "Unknown"
