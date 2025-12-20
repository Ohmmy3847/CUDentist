"""
Application Configuration and Settings
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings"""
    
    # API Configuration
    API_TITLE: str = "Risk Classification API"
    API_VERSION: str = "1.0.0"
    
    # Google API
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-2.0-flash-lite")
    
    # Google Sheets
    GOOGLE_SERVICE_ACCOUNT_JSON: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    SPREADSHEET_ID: str = os.getenv("SPREADSHEET_ID", "")
    
    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "")
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://cudent-e3utbty62-ohmmy3847s-projects.vercel.app",
        "https://cudent.vercel.app",
    ]
    ALLOW_ORIGIN_REGEX: str = r"https://.*\.vercel\.app"
    
    # Directories
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # CSV Processing
    MAX_CONCURRENT_REQUESTS: int = 10
    
    def __init__(self):
        """Initialize settings and validate"""
        if not self.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        
        # Add FRONTEND_URL to allowed origins if specified
        if self.FRONTEND_URL and self.FRONTEND_URL not in self.ALLOWED_ORIGINS:
            self.ALLOWED_ORIGINS.append(self.FRONTEND_URL)
        
        # Create directories if they don't exist
        self.DATA_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)


# Global settings instance
settings = Settings()
