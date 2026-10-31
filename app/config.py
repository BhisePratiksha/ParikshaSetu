import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from root project directory
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'parikshasetu-secret-key-2026-production')
    
    # MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/parikshasetu_db')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'parikshasetu_db')
    
    # External Papers Mock API URL
    PAPERS_API_URL = os.getenv('PAPERS_API_URL', 'https://your-hosted-domain.com/papers.json')
    LOCAL_PAPERS_PATH = BASE_DIR / 'data' / 'papers.json'
    
    # Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads', 'pdfs')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16 MB max
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # Default Admin
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@parikshasetu.com')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Admin@123')
    ADMIN_NAME = os.getenv('ADMIN_NAME', 'System Administrator')

    # Security settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
