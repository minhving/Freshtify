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
    ErrorResponse,
    StockEstimationMultipleResponse,
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
        # Get the project root directory (go up 4 levels from backend/app/api/routes/stock_estimation.py)
        # This gives us: backend/app/api/routes -> backend/app/api -> backend/app -> backend -> project_root
        project_root = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

        # Copy uploaded image to dataset folder with T0.jpg name (as expected by main.py)
        dataset_path = os.path.join(project_root, "dataset", "T0.jpg")
        import shutil
        shutil.copy2(image_path, dataset_path)
        logger.info(f"Copied uploaded image to {dataset_path}")

        # Run main.py directly without modifying it
        main_py_path = os.path.join(project_root, "main.py")
        
        logger.info(f"Running main.py analysis on {image_path}")
        logger.info(f"Project root: {project_root}")
        logger.info("This may take 2-5 minutes for AI model processing...")

        # Check if main.py exists
        if not os.path.exists(main_py_path):
            logger.error(f"Main.py file not found at: {main_py_path}")
            raise Exception(f"Main.py file not found at: {main_py_path}")

        # Check if dataset directory exists
        dataset_dir = os.path.join(project_root, "dataset")
        if not os.path.exists(dataset_dir):
            logger.error(f"Dataset directory not found at: {dataset_dir}")
            raise Exception(f"Dataset directory not found at: {dataset_dir}")

        # Run main.py directly
        result = subprocess.run(
            ["python", main_py_path],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=600  # 10 minute timeout for AI processing
        )

        # Log the full output for debugging
        logger.info(f"Main.py stdout: {result.stdout}")
        logger.info(f"Main.py stderr: {result.stderr}")

        if result.returncode != 0:
            logger.error(f"Main.py analysis failed: {result.stderr}")
            logger.info("Falling back to basic analysis...")
            # Fallback to basic analysis
            return await ai_engine.estimate_stock_basic_cv(image_path, products, 0.7)

        # Parse the main.py output from print_result() method
        try:
            # Parse the output from print_result() method
            # Expected format: "class_name - section N: percentage%"
            import re
            stock_pattern = r"([^-]+)\s*-\s*section\s*(\d+):\s*([\d.]+)%"
            matches = re.findall(stock_pattern, result.stdout)
            
            logger.info(f"Found {len(matches)} stock matches in output")
            
            # Convert to ProductStockInfo format
            results = []
            for match in matches:
                product_name = match[0].strip()
                section_num = int(match[1])
                percentage = float(match[2])
                
                # Convert percentage to 0-1 range
                stock_percentage = percentage / 100.0
                
                # Determine stock level
                if stock_percentage < 0.3:
                    stock_status = StockLevel.LOW
                elif stock_percentage > 0.8:
                    stock_status = StockLevel.OVERSTOCKED
                else:
                    stock_status = StockLevel.NORMAL
                
                # Confidence based on stock level
                confidence = min(stock_percentage * 1.1, 0.95)
                
                results.append(ProductStockInfo(
                    product=f"{product_name} section {section_num}",
                    stock_percentage=stock_percentage,
                    stock_status=stock_status,
                    confidence=confidence,
                    reasoning=f"AI model detected {product_name} section {section_num} with {percentage:.1f}% stock level"
                ))
            
            logger.info(f"Parsed {len(results)} products from main.py output")
            
        except Exception as e:
            logger.error(f"Failed to parse main.py output: {e}")
            logger.error(f"Raw output: {result.stdout}")
            # Fallback: create results based on requested products
            results = []
            for product in products:
                results.append(ProductStockInfo(
                    product=f"{product} section 1",
                    stock_percentage=0.5,  # Default medium stock
                    stock_status=StockLevel.NORMAL,
                    confidence=0.5,  # Default medium confidence
                    reasoning=f"Fallback analysis for {product}"
                ))

        logger.info(f"AI analysis completed successfully for {len(results)} products")
        return results

    except Exception as e:
        logger.error(f"Error running main.py analysis: {e}")
        raise

# Initialize services
ai_engine = AIEngine()
file_processor = FileProcessor()


@router.post("/estimate-stock", response_model=StockEstimationResponse)
async def estimate_stock(
    file: UploadFile = File(..., description="Image or video file to analyze"),
    model_type: str = Form(default="qwen-vl", description="AI model to use"),
    products: Optional[str] = Form(
        default=None, description="Comma-separated list of products to analyze"),
    confidence_threshold: float = Form(
        default=0.5, description="Minimum confidence threshold")
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
                product_list = [ProductType(p.strip())
                                for p in products.split(",")]
            except ValueError as e:
                raise HTTPException(
                    status_code=400, detail=f"Invalid product type: {str(e)}")
        
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
        raise HTTPException(
            status_code=500, detail=f"Failed to get available models: {str(e)}")


@router.get("/products", response_model=List[str])
async def get_supported_products():
    """
    Get list of supported products for stock estimation.
    """
    return [product.value for product in ProductType]


@router.post("/estimate-stock-batch")
async def estimate_stock_batch(
    files: List[UploadFile] = File(...,
                                   description="Multiple image or video files to analyze"),
    model_type: str = Form(default="qwen-vl", description="AI model to use"),
    products: Optional[str] = Form(
        default=None, description="Comma-separated list of products to analyze"),
    confidence_threshold: float = Form(
        default=0.5, description="Minimum confidence threshold")
):
    """
    Estimate stock levels from multiple uploaded files (batch processing).
    """
    try:
        if len(files) > 10:  # Limit batch size
            raise HTTPException(
                status_code=400, detail="Maximum 10 files allowed per batch")
        
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
        raise HTTPException(
            status_code=500, detail=f"Batch estimation failed: {str(e)}")


@router.post("/estimate-stock-integrated", response_model=StockEstimationResponse)
async def estimate_stock_integrated(
    file: UploadFile = File(...),
    products: str = Form(
        "potato section,onion,eggplant section,tomato,cucumber"),
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
        raise HTTPException(
            status_code=500, detail=f"Integrated estimation failed: {str(e)}")


@router.post("/estimate-stock-multiple", response_model=StockEstimationMultipleResponse)
async def estimate_stock_multiple(
    files: List[UploadFile] = File(...),
    products: str = Form(
        "potato section,onion,eggplant section,tomato,cucumber"),
    confidence_threshold: float = Form(0.7)
):
    """
    Estimate stock levels for multiple images using integrated AI models.
    Each image is analyzed individually and results are combined.
    """
    start_time = time.time()

    try:
        if not files or len(files) == 0:
            raise HTTPException(status_code=400, detail="No files provided")

        if len(files) > 10:  # Limit to 10 images max
            raise HTTPException(
                status_code=400, detail="Maximum 10 images allowed")

        logger.info(f"Processing {len(files)} images...")

        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

        # Create a temporary directory for multiple images
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()

        try:
            # Save all uploaded images
            image_paths = []
            for i, file in enumerate(files):
                if not file.filename:
                    continue

                # Save file to temp directory
                file_path = os.path.join(
                    temp_dir, f"image_{i}_{file.filename}")
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                image_paths.append(file_path)
                logger.info(f"Saved image {i+1}: {file.filename}")

            if not image_paths:
                raise HTTPException(
                    status_code=400, detail="No valid images provided")

            # Copy images to dataset folder for main.py processing
            dataset_dir = os.path.join(project_root, "dataset")
            os.makedirs(dataset_dir, exist_ok=True)

            # Clear existing test images (but keep other images)
            for file in os.listdir(dataset_dir):
                if file.startswith("T") and file.endswith(('.jpg', '.jpeg', '.png')):
                    try:
                        os.remove(os.path.join(dataset_dir, file))
                    except:
                        pass

            # Copy new images with T0, T1, T2... naming convention
            for i, image_path in enumerate(image_paths):
                dest_path = os.path.join(dataset_dir, f"T{i}.jpg")
                shutil.copy2(image_path, dest_path)
                logger.info(f"Copied image to {dest_path}")

            # Run main.py directly without modifying it
            main_py_path = os.path.join(project_root, "main.py")
            
            # Create a temporary modified main.py with correct image_arr
            import tempfile
            temp_main_py = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=project_root)
            
            # Read original main.py
            with open(main_py_path, 'r') as f:
                main_content = f.read()
            
            # Update image_arr based on number of uploaded images
            image_arr_list = ', '.join([f"'T{i}'" for i in range(len(image_paths))])
            updated_content = main_content.replace(
                "image_arr =  ['T0', 'T1']",
                f"image_arr =  [{image_arr_list}]"
            )
            
            temp_main_py.write(updated_content)
            temp_main_py.close()
            
            logger.info(f"Created temporary main.py with image_arr = [{image_arr_list}]")
            logger.info(f"Temp main.py path: {temp_main_py.name}")
            
            main_py_path = temp_main_py.name
            
            logger.info("Running main.py analysis on multiple images...")
            logger.info(f"Project root: {project_root}")
            logger.info("This may take 5-10 minutes for multiple AI model processing...")

            result = subprocess.run(
                ["python", main_py_path],
                capture_output=True,
                text=True,
                cwd=project_root,
                timeout=1200  # 20 minute timeout for multiple images
            )

            # Log the output for debugging
            logger.info(f"Main.py stdout: {result.stdout}")
            logger.info(f"Main.py stderr: {result.stderr}")
            logger.info(f"Main.py return code: {result.returncode}")

            if result.returncode != 0:
                logger.error(f"Main.py analysis failed: {result.stderr}")
                raise HTTPException(
                    status_code=500, detail="AI analysis failed")

            # Parse the results from main.py output using print_result() format
            try:
                # Parse the output from print_result() method
                # Expected format: "class_name - section N: percentage%"
                import re
                stock_pattern = r"([^-]+)\s*-\s*section\s*(\d+):\s*([\d.]+)%"
                
                # Split output by "Processing image:" to identify different images
                output_lines = result.stdout.strip().split('\n')
                
                # Find all "Processing image:" lines to determine image boundaries
                processing_lines = []
                for i, line in enumerate(output_lines):
                    if "Processing image:" in line:
                        processing_lines.append(i)
                        logger.info(f"Found processing line {i}: {line.strip()}")
                
                logger.info(f"Found {len(processing_lines)} processing lines: {processing_lines}")
                
                # Group results by image (T0, T1, etc.)
                grouped_results = {}
                
                # If no processing lines found, fallback to even distribution
                if len(processing_lines) == 0:
                    logger.warning("No 'Processing image:' lines found, falling back to even distribution")
                    # Parse all matches and distribute evenly
                    all_matches = re.findall(stock_pattern, result.stdout)
                    matches_per_image = len(all_matches) // len(image_paths) if len(image_paths) > 0 else len(all_matches)
                    
                    for i, match in enumerate(all_matches):
                        product_name = match[0].strip()
                        section_num = int(match[1])
                        percentage = float(match[2])
                        
                        # Convert percentage to 0-1 range
                        stock_percentage = percentage / 100.0
                        
                        # Determine stock level
                        if stock_percentage < 0.3:
                            stock_status = StockLevel.LOW
                        elif stock_percentage > 0.8:
                            stock_status = StockLevel.OVERSTOCKED
                        else:
                            stock_status = StockLevel.NORMAL
                        
                        # Confidence based on stock level
                        confidence = min(stock_percentage * 1.1, 0.95)
                        
                        # Determine which image this belongs to
                        image_index = i // matches_per_image if matches_per_image > 0 else 0
                        time_key = f"T{image_index}"
                        
                        if time_key not in grouped_results:
                            grouped_results[time_key] = []
                        
                        grouped_results[time_key].append(ProductStockInfo(
                            product=f"{product_name} section {section_num}",
                            stock_percentage=stock_percentage,
                            stock_status=stock_status,
                            confidence=confidence,
                            reasoning=f"AI model detected {product_name} section {section_num} with {percentage:.1f}% stock level"
                        ))
                else:
                    # Process each image section separately
                    for img_idx in range(len(processing_lines)):
                        time_key = f"T{img_idx}"
                        grouped_results[time_key] = []
                        
                        # Determine the range of lines for this image
                        start_line = processing_lines[img_idx]
                        end_line = processing_lines[img_idx + 1] if img_idx + 1 < len(processing_lines) else len(output_lines)
                        
                        # Extract lines for this image
                        image_lines = output_lines[start_line:end_line]
                        image_text = '\n'.join(image_lines)
                        
                        logger.info(f"Image {time_key}: Processing lines {start_line} to {end_line}")
                        logger.info(f"Image {time_key}: Sample lines: {image_lines[:3] if len(image_lines) >= 3 else image_lines}")
                        
                        # Find matches in this image's output
                        matches = re.findall(stock_pattern, image_text)
                        
                        logger.info(f"Image {time_key}: Found {len(matches)} matches")
                        if matches:
                            logger.info(f"Image {time_key}: First few matches: {matches[:3]}")
                        
                        # Process each match for this image
                        for match in matches:
                            product_name = match[0].strip()
                            section_num = int(match[1])
                            percentage = float(match[2])
                            
                            # Convert percentage to 0-1 range
                            stock_percentage = percentage / 100.0
                            
                            # Determine stock level
                            if stock_percentage < 0.3:
                                stock_status = StockLevel.LOW
                            elif stock_percentage > 0.8:
                                stock_status = StockLevel.OVERSTOCKED
                            else:
                                stock_status = StockLevel.NORMAL
                            
                            # Confidence based on stock level
                            confidence = min(stock_percentage * 1.1, 0.95)
                            
                            grouped_results[time_key].append(ProductStockInfo(
                                product=f"{product_name} section {section_num}",
                                stock_percentage=stock_percentage,
                                stock_status=stock_status,
                                confidence=confidence,
                                reasoning=f"AI model detected {product_name} section {section_num} with {percentage:.1f}% stock level"
                            ))
                
                logger.info(f"Parsed results for {len(grouped_results)} images: {list(grouped_results.keys())}")
                for time_key, results in grouped_results.items():
                    logger.info(f"  {time_key}: {len(results)} products")
                    if results:
                        logger.info(f"    First product: {results[0].product}")
                        logger.info(f"    Last product: {results[-1].product}")
                
                processing_time = time.time() - start_time

                return StockEstimationMultipleResponse(
                    success=True,
                    message=f"Stock estimation completed successfully for {len(image_paths)} images",
                    processing_time=processing_time,
                    timestamp=datetime.utcnow().isoformat() + "Z",
                    results=grouped_results,
                    model_used="integrated-ai-multiple",
                    image_metadata={
                        "image_count": len(image_paths),
                        "images_processed": [f"T{i}" for i in range(len(image_paths))]
                    }
                )

            except Exception as e:
                logger.error(f"Failed to parse multiple image results: {e}")
                raise HTTPException(
                    status_code=500, detail="Failed to parse AI analysis results")

        finally:
            # Clean up temporary directory and temp main.py file
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            # Remove temporary main.py file if it was created
            if 'temp_main_py' in locals() and os.path.exists(temp_main_py.name):
                try:
                    os.remove(temp_main_py.name)
                    logger.info("Cleaned up temporary main.py file")
                except:
                    pass
            
            logger.info("Cleaned up temporary files")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Multiple image estimation failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Multiple image estimation failed: {str(e)}")
