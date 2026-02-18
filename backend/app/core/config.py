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
    
    # API Keys
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "deepseek-chat")
    
    # Google Sheets
    GOOGLE_SERVICE_ACCOUNT_JSON: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    SPREADSHEET_ID: str = os.getenv("SPREADSHEET_ID", "")
    
    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "")
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
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

         # Thai-English word mappings
        self.translations = {
            'ผู้ชาย': 'man',
            'ผู้หญิง': 'woman',
            'คน': 'person',
            'เสื้อ': 'shirt',
            'กางเกง': 'pants',
            'หมวก': 'hat',
            'แว่นตา': 'glasses',
            'รองเท้า': 'shoes',
            'กระเป๋า': 'bag',
            'สีแดง': 'red',
            'สีน้ำเงิน': 'blue',
            'สีเขียว': 'green',
            'สีเหลือง': 'yellow',
            'สีดำ': 'black',
            'สีขาว': 'white',
            'ใส่': 'wearing',
            'ถือ': 'holding',
            'ใกล้': 'near',
        }
        
        # Color keywords
        self.colors = {
            'แดง', 'red', 'น้ำเงิน', 'blue', 'เขียว', 'green',
            'เหลือง', 'yellow', 'ดำ', 'black', 'ขาว', 'white',
            'ส้ม', 'orange', 'ม่วง', 'purple', 'ชมพู', 'pink',
            'เทา', 'gray', 'น้ำตาล', 'brown'
        }

        def translate_thai_to_english(self, text: str) -> str:
            """Translate Thai words to English"""
            result = text
            for thai, eng in self.translations.items():
                result = result.replace(thai, eng)
            return result

# Global settings instance
settings = Settings()
