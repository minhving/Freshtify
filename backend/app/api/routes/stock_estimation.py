"""
Stock estimation endpoints for the API.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import List, Optional
import time
import logging
import os
from datetime import datetime

from app.models.schemas import (
    StockEstimationRequest, 
    StockEstimationResponse, 
    ProductStockInfo, 
    ProductType,
    StockLevel,
    ModelInfo,
    ErrorResponse
)
from app.core.config import settings
from app.services.ai_engine import AIEngine
from app.services.file_processor import FileProcessor

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
ai_engine = AIEngine()
file_processor = FileProcessor()

@router.post("/estimate-stock", response_model=StockEstimationResponse)
async def estimate_stock(
    file: UploadFile = File(..., description="Image or video file to analyze"),
    model_type: str = Form(default="qwen-vl", description="AI model to use"),
    products: Optional[str] = Form(default=None, description="Comma-separated list of products to analyze"),
    confidence_threshold: float = Form(default=0.5, description="Minimum confidence threshold")
):
    """
    Estimate stock levels from uploaded image or video.
    """
    start_time = time.time()
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_ext} not supported. Allowed: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Parse products list
        product_list = None
        if products:
            try:
                product_list = [ProductType(p.strip()) for p in products.split(",")]
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid product type: {str(e)}")
        
        # Process file
        processed_data = await file_processor.process_upload(file)
        
        # Run AI estimation
        results = await ai_engine.estimate_stock_levels(
            processed_data=processed_data,
            model_type=model_type,
            products=product_list,
            confidence_threshold=confidence_threshold
        )
        
        processing_time = time.time() - start_time
        
        return StockEstimationResponse(
            success=True,
            message="Stock estimation completed successfully",
            processing_time=processing_time,
            results=results,
            model_used=model_type,
            image_metadata=processed_data.get("metadata", {})
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stock estimation failed: {str(e)}")
        processing_time = time.time() - start_time
        
        return StockEstimationResponse(
            success=False,
            message=f"Stock estimation failed: {str(e)}",
            processing_time=processing_time,
            results=[],
            model_used=model_type
        )

@router.get("/models", response_model=List[ModelInfo])
async def get_available_models():
    """
    Get list of available AI models and their capabilities.
    """
    try:
        models = await ai_engine.get_available_models()
        return models
    except Exception as e:
        logger.error(f"Failed to get available models: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get available models: {str(e)}")

@router.get("/products", response_model=List[str])
async def get_supported_products():
    """
    Get list of supported products for stock estimation.
    """
    return [product.value for product in ProductType]

@router.post("/estimate-stock-batch")
async def estimate_stock_batch(
    files: List[UploadFile] = File(..., description="Multiple image or video files to analyze"),
    model_type: str = Form(default="qwen-vl", description="AI model to use"),
    products: Optional[str] = Form(default=None, description="Comma-separated list of products to analyze"),
    confidence_threshold: float = Form(default=0.5, description="Minimum confidence threshold")
):
    """
    Estimate stock levels from multiple uploaded files (batch processing).
    """
    try:
        if len(files) > 10:  # Limit batch size
            raise HTTPException(status_code=400, detail="Maximum 10 files allowed per batch")
        
        results = []
        for file in files:
            try:
                # Process each file
                result = await estimate_stock(
                    file=file,
                    model_type=model_type,
                    products=products,
                    confidence_threshold=confidence_threshold
                )
                results.append({
                    "filename": file.filename,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "message": f"Batch processing completed for {len(files)} files",
            "results": results,
            "timestamp": datetime.now()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch estimation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch estimation failed: {str(e)}")


@router.post("/estimate-stock-integrated", response_model=StockEstimationResponse)
async def estimate_stock_integrated(
    file: UploadFile = File(...),
    products: str = Form("banana,broccoli"),
    confidence_threshold: float = Form(0.7)
):
    """
    Estimate stock levels using integrated AI models (detection + segmentation + depth estimation).
    """
    start_time = time.time()
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Process file
        file_path = await file_processor.save_uploaded_file(file)
        logger.info(f"Processing file: {file_path}")
        
        # Parse products
        product_list = [p.strip().lower() for p in products.split(',')]
        
        # Use integrated models
        results = await ai_engine.process_with_integrated_models(file_path, product_list)
        
        processing_time = time.time() - start_time
        
        return StockEstimationResponse(
            success=True,
            message="Stock estimation completed successfully using integrated AI models",
            processing_time=processing_time,
            timestamp=datetime.utcnow().isoformat() + "Z",
            results=results,
            model_used="integrated-ai",
            image_metadata={
                "filename": file.filename,
                "size": file.size if hasattr(file, 'size') else 0
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Integrated estimation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Integrated estimation failed: {str(e)}")