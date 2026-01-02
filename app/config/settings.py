from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    NODE_ENV: str 
    PORT: int
    
    # MongoDB
    MONGODB_URL: str
    
    # JWT
    JWT_SECRET: str 
    JWT_ACCESS_EXPIRATION_MINUTES: int 
    JWT_REFRESH_EXPIRATION_DAYS: int
    
    # Meta Instagram API
    META_APP_ID: str
    META_APP_SECRET: str
    META_VERIFY_TOKEN: str
    META_API_VERSION: str
    
    # CORS - can be comma-separated string or "*" for all
    CORS_ORIGINS: str
    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

