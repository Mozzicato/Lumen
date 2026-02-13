import os
from pathlib import Path
from dotenv import load_dotenv

# Load env from parent directory (root of project)
env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = "Note Beautifier API"
    PROJECT_VERSION: str = "1.0.0"
    
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    
    DATABASE_URL: str = "sqlite:///./notes.db"
    
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")

    # Service Configuration
    LLM_PROVIDER: str = "groq" # Options: groq, gemini, openrouter
    LLM_MODEL: str = "llama-3.1-8b-instant" # Fast and good for formatting

settings = Settings()

# Ensure upload directory exists
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
