import json
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

def load_trusted_sources() -> List[str]:
    """Loads the list of trusted domains from the JSON file."""
    # Build a path to the file relative to this config file
    json_path = Path(__file__).parent / "trusted_sources.json"
    if not json_path.is_file():
        return []
    with open(json_path, 'r') as f:
        data = json.load(f)
        return data.get("sources", [])

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

    # Google Cloud Settings
    GCP_PROJECT: str
    GCP_LOCATION: str

    # Search API Settings
    SEARCH_API_KEY: str
    SEARCH_ENGINE_ID: str

    GEMINI_API_KEY: str
    
    # Load the trusted sources list into your settings
    TRUSTED_SOURCES: List[str] = load_trusted_sources()

# Create a single instance of the settings
settings = Settings()