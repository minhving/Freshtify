"""
Stock estimation endpoints for the API.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import List, Optional
import time
import logging
import os
import subprocess
import json
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

async def run_main_py_analysis(image_path: str, products: List[str]) -> List[ProductStockInfo]:
    """
    Run main.py with the uploaded image and capture the results.
    """
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # Create analysis script based on your main.py
        analysis_script = f"""
import sys
import os
import json

# Add the project root to the path
sys.path.append(r"{project_root}")

# Import modules (same as your main.py)
from backend_model.imports import *
from backend_model.detection_model import *
from backend_model.segmentation_model import *
from backend_model.prob_calculation import *
from backend_model.stock_estimation_depth import *

# Use the uploaded image (same as your main.py)
image = Image.open(r"{image_path}")
image_path = r"{image_path}"
class_names = ' '.join({products})

# Initialize and load models (same as your main.py)
detection_model = DetectionModel()
segmentation_model = SegmentationModel("sam2.1_l.pt")
depth_model = DepthModel()

detection_model.load_model()
segmentation_model.load()
depth_model.load()

# Detection (same as your main.py)
xyxy, labels, scores = detection_model.detect(image, class_names)

# Segmentation (same as your main.py)
results_seg = segmentation_model.segment(image_path, xyxy, labels)

# Compute stock levels (same as your main.py)
stock_dict = depth_model.compute_stock(results_seg, image_path)

# Calculate probabilities (same as your main.py)
probs = depth_model.cal_probs(stock_dict)

# Output results as JSON for the dashboard
results = []
for product in {products}:
    if product in stock_dict:
        results.append({{
            "product": product,
            "stock_percentage": stock_dict[product] / 100,  # Convert to 0-1 range
            "confidence": probs.get(product, 0.5) if probs else 0.5,
            "reasoning": f"AI model detected {{product}} with {{stock_dict[product]:.1f}}% stock level"
        }})

print(json.dumps(results))
"""
        
        # Write the analysis script in the project root
        script_path = os.path.join(project_root, "run_analysis.py")
        with open(script_path, "w") as f:
            f.write(analysis_script)
        
        # Run the analysis script from project root
        logger.info(f"Running main.py analysis on {image_path}")
        result = subprocess.run(
            ["python", "run_analysis.py"],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=300  # 5 minute timeout
        )
        
        # Log the full output for debugging
        logger.info(f"Script stdout: {result.stdout}")
        logger.info(f"Script stderr: {result.stderr}")
        
        # Clean up the script file
        if os.path.exists(script_path):
            os.remove(script_path)
        
        if result.returncode != 0:
            logger.error(f"AI analysis failed: {result.stderr}")
            logger.info("Falling back to basic analysis...")
            
            # Fallback to basic analysis
            return await ai_engine.estimate_stock_basic_cv(image_path, products, 0.7)
        
        # Parse the JSON output
        try:
            # Get the last line which should contain the JSON
            output_lines = result.stdout.strip().split('\n')
            json_line = output_lines[-1] if output_lines else ""
            analysis_results = json.loads(json_line)
        except (json.JSONDecodeError, IndexError) as e:
            logger.error(f"Failed to parse AI results: {result.stdout}")
            logger.error(f"JSON decode error: {e}")
            raise Exception("Failed to parse AI analysis results")
        
        # Convert to ProductStockInfo format
        results = []
        for item in analysis_results:
            stock_percentage = item["stock_percentage"]
            confidence = item["confidence"]
            
            # Determine stock level
            if stock_percentage < 0.3:
                stock_status = StockLevel.LOW
            elif stock_percentage > 0.8:
                stock_status = StockLevel.OVERSTOCKED
            else:
                stock_status = StockLevel.NORMAL
            
            results.append(ProductStockInfo(
                product=item["product"],
                stock_percentage=stock_percentage,
                stock_status=stock_status,
                confidence=confidence,
                reasoning=item["reasoning"]
            ))
        
        logger.info(f"AI analysis completed successfully for {len(results)} products")
        return results
        
    except Exception as e:
        logger.error(f"Error running AI analysis: {e}")
        raise

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
        
        # Run main.py with the uploaded image to get real AI analysis
        logger.info("Running main.py with uploaded image...")
        results = await run_main_py_analysis(file_path, product_list)
        
        processing_time = time.time() - start_time
        
        return StockEstimationResponse(
            success=True,
            message="Stock estimation completed successfully using basic CV model",
            processing_time=processing_time,
            timestamp=datetime.utcnow().isoformat() + "Z",
            results=results,
            model_used="basic-cv-fallback",
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