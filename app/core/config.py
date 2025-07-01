import os
from typing import List, Optional
from pydantic import field_validator, ConfigDict
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Allow extra fields from .env without validation errors
    )
    # FastAPI settings
    PROJECT_NAME: str = "FastAPI App"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    DEBUG_MODE: bool = True  # Default to True for development
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS - More permissive defaults for development
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000,http://localhost:3001,http://127.0.0.1:3001"
    
    # Database settings - PostgreSQL with better defaults
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://postgres:postgres@localhost/fastapi_db"
    )
    
    # AWS settings (optional)
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_S3_BUCKET: Optional[str] = os.getenv("AWS_S3_BUCKET")
    
    # GCP settings (optional)
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    GCP_PROJECT_ID: Optional[str] = os.getenv("GCP_PROJECT_ID")
    GCP_BUCKET_NAME: Optional[str] = os.getenv("GCP_BUCKET_NAME")
    
    # Security
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "dev-secret-key-change-this-in-production-use-openssl-rand-hex-32"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # HTTPS settings (optional)
    SSL_KEYFILE: Optional[str] = os.getenv("SSL_KEYFILE")
    SSL_CERTFILE: Optional[str] = os.getenv("SSL_CERTFILE")
    
    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v):
        if not v or v == "":
            # Provide a development default instead of raising an error
            return "dev-secret-key-change-this-in-production-use-openssl-rand-hex-32"
        return v

    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert ALLOWED_ORIGINS string to list"""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
        return self.ALLOWED_ORIGINS

settings = Settings()