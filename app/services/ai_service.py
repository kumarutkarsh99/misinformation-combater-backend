import google.generativeai as genai
from app.core.config import settings
import json
import time
import re
import io
import PyPDF2
import docx
from geopy.geocoders import Nominatim

# Configure the Gemini API key
genai.configure(api_key=settings.GEMINI_API_KEY)

# Define safety settings as a constant
SAFETY_SETTINGS = {
    'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_ONLY_HIGH',
    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_ONLY_HIGH',
}

# --- Text Extraction and Generation Functions ---

def summarize_full_text(full_text: str) -> str:
    # ... (This function is correct and remains the same) ...
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    prompt = f"Please read the following document and provide a concise, one-paragraph summary of its key ideas.\n\nDOCUMENT:\n\"{full_text}\""
    try:
        response = model.generate_content(prompt, safety_settings=SAFETY_SETTINGS)
        if not response.parts:
            print("Error summarizing full text: Response was blocked by safety filters.")
            return full_text[:8000]
        return response.text.strip()
    except Exception as e:
        print(f"Error summarizing full text: {e}")
        return full_text[:1000]

def generate_search_query(text_to_summarize: str) -> str:
    # ... (This function is correct and remains the same) ...
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    prompt = f"Read the following text and summarize it into a clean, simple search engine query of 5-10 keywords.\n\nTEXT:\n\"{text_to_summarize}\"\n\nSEARCH QUERY:"
    try:
        response = model.generate_content(prompt, safety_settings=SAFETY_SETTINGS)
        if not response.parts:
            print("Error generating search query: Response was blocked by safety filters.")
            return text_to_summarize[:100]
        return response.text.strip()
    except Exception as e:
        print(f"Error generating search query: {e}")
        return text_to_summarize[:100]

def transcribe_audio(file_contents: bytes, mime_type: str) -> str:
    """Uses Gemini 1.5 Pro to transcribe an audio file."""
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    
    # CORRECTED LOGIC: Pass audio data directly as a 'Part'
    audio_part = {
        "mime_type": mime_type,
        "data": file_contents
    }

    prompt = "Transcribe the following audio file. Provide only the text transcription."

    try:
        response = model.generate_content([prompt, audio_part], safety_settings=SAFETY_SETTINGS)
        if not response.parts:
            print("Error transcribing audio: Response was blocked by safety filters.")
            return None
        return response.text.strip()
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None


def analyze_image_with_ai(file_contents: bytes, mime_type: str) -> str:
    # ... (This function is correct and remains the same) ...
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    image_part = {"mime_type": mime_type, "data": file_contents}
    prompt = "Extract all text from the following image using Optical Character Recognition (OCR). Provide only the extracted text."
    try:
        response = model.generate_content([prompt, image_part], safety_settings=SAFETY_SETTINGS)
        return response.text.strip()
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return None

def extract_text_from_doc(file_contents: bytes) -> str:
    # ... (This function is correct and remains the same) ...
    try:
        doc = docx.Document(io.BytesIO(file_contents))
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error reading DOCX file: {e}")
        return None

def extract_text_from_pdf(file_contents: bytes) -> str:
    # ... (This function is correct and remains the same) ...
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_contents))
        return "".join(page.extract_text() for page in pdf_reader.pages)
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return None

# --- Main Analysis Function ---

def analyze_content_with_ai(user_content: str, search_context: str) -> dict:
    # ... (This function is correct and remains the same) ...
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
          }}
      ],
      "formal_report": "<Generate a formal, multi-paragraph report suitable for submission to authorities. It should start with 'To Whom It May Concern,', state the category, summarize the claim, explain why it is misleading based on the trusted sources, and end with a request for review. Use neutral and professional language. Use '\\n' for new lines.>",
      "raw": {{ "ts": 0 }}
    }}
    """

    try:
        response = model.generate_content(prompt, safety_settings=SAFETY_SETTINGS)
        
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

def get_state_from_coords(lat: float, lon: float):
    """
    Finds the state for a given latitude and longitude.
    """
    try:
        geolocator = Nominatim(user_agent="state_finder_app")

        location_str = f"{lat}, {lon}"

        location = geolocator.reverse(location_str, exactly_one=True, language='en')

        if location:
            address = location.raw.get('address', {})
            state = address.get('state') or address.get('city')
            
            if state:
                return state
            else:
                return "State not found in the address details."
        else:
            return "Could not determine location."

    except Exception as e:
        return f"An error occurred: {e}"