"""
Configuration management for the AI Stock Level Estimation API.
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional, Union
import os

class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS Settings
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000", 
        "http://localhost:8080", 
        "http://localhost:5173",  # React Router dev server
        "http://localhost:8000"   # Backend port
    ]
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            # Handle comma-separated or space-separated values
            if ',' in v:
                return [origin.strip() for origin in v.split(',')]
            else:
                return [origin.strip() for origin in v.split()]
        return v
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".mp4", ".avi", ".mov"]
    
    # Directory Settings
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"
    MODEL_CACHE_DIR: str = "model_cache"
    
    # AI Model Settings
    DEFAULT_MODEL: str = "qwen-vl"
    ENABLE_GPU: bool = True
    BATCH_SIZE: int = 1
    
    # Vision-Language Model Settings
    QWEN_VL_MODEL: str = "Qwen/Qwen-VL-Chat"
    PALIGEMMA_MODEL: str = "google/paligemma-3b-pt-448"
    FLORENCE_MODEL: str = "microsoft/Florence-2-base"
    
    # Segmentation Model Settings
    SAM_MODEL: str = "sam_vit_h_4b8939.pth"
    
    # Depth Estimation Settings
    MIDAS_MODEL: str = "MiDaS_small"
    MARIGOLD_MODEL: str = "prs-eth/marigold-v1-0"
    
    # Stock Level Thresholds
    LOW_STOCK_THRESHOLD: float = 0.3
    NORMAL_STOCK_THRESHOLD: float = 0.7
    OVERSTOCK_THRESHOLD: float = 0.9
    
    # Supported Products
    SUPPORTED_PRODUCTS: List[str] = [
        "potato section", "onion", "eggplant section", "tomato", "cucumber"
    ]
    
    # API Keys (for commercial models)
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
