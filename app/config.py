import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "resume-screening-secret-key-change-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

    # NLP Configuration
    SPACY_MODEL = "en_core_web_sm"

    # Matching Weights
    MATCH_WEIGHTS = {
        "skill": 0.40,
        "experience": 0.30,
        "education": 0.10,
        "semantic": 0.20,
    }


class DevelopmentConfig(Config):
    """Development configuration - uses MySQL locally."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:Root%4012345@localhost:3306/resume_screening_dev"
    )


class ProductionConfig(Config):
    """Production configuration - uses SQLite for deployment."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///jobmatchfinder.db"
    )


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
