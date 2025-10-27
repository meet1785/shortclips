"""
Configuration module for the Short Clips AI tool.
Loads environment variables and provides application settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        # API Keys
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.freesound_api_key = os.getenv("FREESOUND_API_KEY", "")
        
        # Server Configuration
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        
        # Video Processing Settings
        self.min_clip_duration = int(os.getenv("MIN_CLIP_DURATION", "15"))
        self.max_clip_duration = int(os.getenv("MAX_CLIP_DURATION", "60"))
        self.target_aspect_ratio = os.getenv("TARGET_ASPECT_RATIO", "9:16")
        self.output_resolution = os.getenv("OUTPUT_RESOLUTION", "1080x1920")
        
        # Directories
        self.downloads_dir = "downloads"
        self.outputs_dir = "outputs"
        self.temp_dir = "temp"
        self.models_dir = "models"


settings = Settings()

# Create necessary directories
for directory in [settings.downloads_dir, settings.outputs_dir, 
                  settings.temp_dir, settings.models_dir]:
    os.makedirs(directory, exist_ok=True)
