"""
Health check endpoints for the API.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import torch
import logging

from app.models.schemas import HealthResponse
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify API status and system resources.
    """
    try:
        # Check GPU availability
        gpu_available = torch.cuda.is_available()
        
        # List of models that should be loaded (placeholder for now)
        models_loaded = []
        
        # Add models based on configuration
        if settings.DEFAULT_MODEL:
            models_loaded.append(settings.DEFAULT_MODEL)
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            models_loaded=models_loaded,
            gpu_available=gpu_available
        )
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check with system information.
    """
    try:
        import psutil
        import platform
        
        system_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "gpu_available": torch.cuda.is_available(),
            "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            "gpu_names": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())] if torch.cuda.is_available() else []
        }
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(),
            "system_info": system_info
        }
    
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Detailed health check failed: {str(e)}")
