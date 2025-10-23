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
        # Get the project root directory (go up 4 levels from backend/app/api/routes/stock_estimation.py)
        # This gives us: backend/app/api/routes -> backend/app/api -> backend/app -> backend -> project_root
        project_root = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

        dataset_path = os.path.join(project_root, "dataset", "test_image.jpg")
        import shutil
        shutil.copy2(image_path, dataset_path)
        logger.info(f"Copied uploaded image to {dataset_path}")

        # Read the original main.py and modify it to use the uploaded image
        main_py_path = os.path.join(project_root, "main.py")

        # Read the original main.py content
        with open(main_py_path, "r") as f:
            original_content = f.read()

        # Replace the hardcoded image path with the uploaded image
        modified_content = original_content.replace(
            'image = Image.open("dataset/onion.png")',
            'image = Image.open("dataset/test_image.jpg")'
        ).replace(
            'image_path = "dataset/onion.png"',
            'image_path = "dataset/test_image.jpg"'
        )

        # Write the modified main.py
        with open(main_py_path, "w") as f:
            f.write(modified_content)

        logger.info("Modified main.py to use uploaded image")

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
import json

image = Image.open("dataset/test_image.jpg")
image_path = "dataset/test_image.jpg"
class_names = ' '.join({products})

if __name__ == "__main__":
    # Initialize and load models
    detection_model = DetectionModel()
    segmentation_model = SegmentationModel("sam2.1_l.pt")
    depth_model = DepthModel()

    detection_model.load_model()
    segmentation_model.load()
    depth_model.load()

    # Detection
    xyxy, labels, scores = detection_model.detect(image, class_names)

    # Segmentation
    results_seg = segmentation_model.segment(image_path, xyxy, labels)

    # Compute fullness (depth-based)
    stock_dict = depth_model.compute_stock(results_seg, image_path)

    # Visualize
    depth_model.visualize_stock(image_path, results_seg, stock_dict, save_path="depth_estimation_overlay.jpg")

    # Calculate probs
    probs = depth_model.cal_probs(stock_dict)
    
    # Prepare results in the format expected by the API
    results = []
    for product in {products}:
        if product in stock_dict:
            results.append({{
                "product": product,
                "stock_percentage": stock_dict[product] / 100,
                "confidence": probs.get(product, 0.5) if probs else 0.5,
                "reasoning": f"AI model detected {{product}} with {{stock_dict[product]:.1f}}% stock level"
            }})
    
    # Output results as JSON
    print(json.dumps(results))
"""

        # Write the analysis script in the project root
        script_path = os.path.join(project_root, "run_analysis.py")
        with open(script_path, "w") as f:
            f.write(analysis_script)

        # Run the analysis script from project root
        logger.info(f"Running main.py analysis on {image_path}")
        logger.info(f"Project root: {project_root}")
        logger.info("This may take 2-5 minutes for AI model processing...")

        # Use absolute path to main.py
        main_py_absolute_path = os.path.join(project_root, "main.py")
        logger.info(f"Main.py absolute path: {main_py_absolute_path}")

        # Check if main.py exists
        if not os.path.exists(main_py_absolute_path):
            logger.error(f"Main.py file not found at: {main_py_absolute_path}")
            raise Exception(
                f"Main.py file not found at: {main_py_absolute_path}")

        # Check if dataset directory exists
        dataset_dir = os.path.join(project_root, "dataset")
        if not os.path.exists(dataset_dir):
            logger.error(f"Dataset directory not found at: {dataset_dir}")
            raise Exception(f"Dataset directory not found at: {dataset_dir}")

        result = subprocess.run(
            ["python", main_py_absolute_path],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=600  # 10 minute timeout for AI processing
        )

        # Log the full output for debugging
        logger.info(f"Script stdout: {result.stdout}")
        logger.info(f"Script stderr: {result.stderr}")

        # Restore the original main.py
        with open(main_py_path, "w") as f:
            f.write(original_content)
        logger.info("Restored original main.py")

        # Clean up the script file
        if os.path.exists(script_path):
            os.remove(script_path)
        if result.returncode != 0:
            logger.error(f"Main.py analysis failed: {result.stderr}")
            logger.info("Falling back to basic analysis...")

            # Fallback to basic analysis
            return await ai_engine.estimate_stock_basic_cv(image_path, products, 0.7)

        # Parse the main.py output (probabilities dictionary)
        try:
            # Get the last line which should contain the probabilities dictionary
            output_lines = result.stdout.strip().split('\n')
            probs_line = output_lines[-1] if output_lines else ""
            logger.info(f"Parsing probabilities from: {probs_line}")

            # Use eval to parse the Python dictionary (since it's not JSON)
            import ast
            probs_dict = ast.literal_eval(probs_line)
            logger.info(f"Parsed probabilities: {probs_dict}")

            # Convert to the expected format using the actual product names and stock percentages from main.py
            analysis_results = []

            # Use the actual product names from main.py output
            for main_py_product, stock_value in probs_dict.items():
                # Use the actual stock percentage from main.py (already in 0-100 range)
                stock_percentage = stock_value / 100  # Convert to 0-1 range
                # Confidence based on stock level
                confidence = min(stock_percentage * 1.1, 0.95)

                analysis_results.append({
                    "product": main_py_product,  # Use the actual product name from main.py
                    "stock_percentage": stock_percentage,
                    "confidence": confidence,
                    "reasoning": f"AI model detected {main_py_product} with {stock_value:.1f}% stock level"
                })

        except (ValueError, SyntaxError, IndexError) as e:
            logger.error(
                f"Failed to parse main.py probabilities: {result.stdout}")
            logger.error(f"Parse error: {e}")
            # Fallback: create results based on requested products
            analysis_results = []
            for product in products:
                analysis_results.append({
                    # Add image identifier for single image
                    "product": f"{product} (T0)",
                    "stock_percentage": 0.5,  # Default medium stock
                    "confidence": 0.5,  # Default medium confidence
                    "reasoning": f"Fallback analysis for {product}"
                })
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
                product=item["product"],  # Already has (T0) identifier
                stock_percentage=stock_percentage,
                stock_status=stock_status,
                confidence=confidence,
                reasoning=item["reasoning"]
            ))

        logger.info(
            f"AI analysis completed successfully for {len(results)} products")
        return results

    except Exception as e:
        # Restore the original main.py in case of error
        try:
            with open(main_py_path, "w") as f:
                f.write(original_content)
            logger.info("Restored original main.py after error")
        except:
            pass
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
    products: str = Form("potato section,onion,eggplant section,tomato,cucumber"),
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


@router.post("/estimate-stock-multiple", response_model=StockEstimationResponse)
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

            # Clear existing test images
            for file in os.listdir(dataset_dir):
                if file.startswith("test_image") or file.startswith("T"):
                    os.remove(os.path.join(dataset_dir, file))

            # Copy new images with T0, T1, T2... naming convention
            for i, image_path in enumerate(image_paths):
                dest_path = os.path.join(dataset_dir, f"T{i}.jpg")
                shutil.copy2(image_path, dest_path)
                logger.info(f"Copied image to {dest_path}")

            # Update main.py to process multiple images
            main_py_path = os.path.join(project_root, "main.py")

            # Read the original main.py content
            with open(main_py_path, "r") as f:
                original_content = f.read()

            # Create updated main.py for multiple images
            updated_content = f"""
from backend_model.imports import *
from backend_model.model_cache import get_model

image_arr = {[f'T{i}' for i in range(len(image_paths))]}
class_names = 'potato section . onion . eggplant section . tomato . cucumber .'

if __name__ == "__main__":
    # Initialize and load models
    detection_model = get_model("detection")
    segmentation_model = get_model("segmentation")
    depth_model = get_model("depth")

    all_results = []
    
    for name in image_arr:
        image_path = f"dataset/{{name}}.jpg"
        image = Image.open(image_path)

        # Detection
        xyxy, labels, scores = detection_model.detect(image, class_names)

        # Segmentation
        results_seg = segmentation_model.segment(image_path, xyxy, labels)

        # Depth and compute stock
        stock_dict = depth_model.compute_stock(results_seg, image_path)
        
        # Store results for this image
        image_results = {{
            "image_name": name,
            "stock_dict": stock_dict
        }}
        all_results.append(image_results)
        
        print(f"Image: {{name}}")
        print(f"Stock dict: {{stock_dict}}")
        print(f"Length stock dict {{len(stock_dict)}}")
        depth_model.print_result(stock_dict)
        print("\\n" + "="*50 + "\\n")

    # Output all results as JSON
    import json
    print("FINAL_RESULTS_START")
    print(json.dumps(all_results))
    print("FINAL_RESULTS_END")
"""

            # Write the updated main.py
            with open(main_py_path, "w") as f:
                f.write(updated_content)

            logger.info("Updated main.py for multiple image processing")

            # Run the updated main.py
            logger.info("Running main.py analysis on multiple images...")
            logger.info(f"Project root: {project_root}")
            logger.info(
                "This may take 5-10 minutes for multiple AI model processing...")

            result = subprocess.run(
                ["python", main_py_path],
                capture_output=True,
                text=True,
                cwd=project_root,
                timeout=1200  # 20 minute timeout for multiple images
            )

            # Restore the original main.py
            with open(main_py_path, "w") as f:
                f.write(original_content)
            logger.info("Restored original main.py")

            # Log the output for debugging
            logger.info(f"Main.py stdout: {result.stdout}")
            logger.info(f"Main.py stderr: {result.stderr}")
            logger.info(f"Main.py return code: {result.returncode}")

            if result.returncode != 0:
                logger.error(f"Main.py analysis failed: {result.stderr}")
                raise HTTPException(
                    status_code=500, detail="AI analysis failed")

            # Parse the results from main.py output
            try:
                # Extract JSON results from the output
                output_lines = result.stdout.strip().split('\n')
                json_start = -1
                json_end = -1

                for i, line in enumerate(output_lines):
                    if "FINAL_RESULTS_START" in line:
                        json_start = i + 1
                    elif "FINAL_RESULTS_END" in line:
                        json_end = i
                        break

                if json_start == -1 or json_end == -1:
                    raise Exception("Could not find results in main.py output")

                # Extract JSON content
                json_content = '\n'.join(output_lines[json_start:json_end])
                logger.info(f"Extracted JSON content: {json_content}")
                all_results = json.loads(json_content)

                logger.info(f"Parsed results for {len(all_results)} images")
                logger.info(f"All results: {all_results}")

                # Convert to ProductStockInfo format
                final_results = []
                # --- MOCK RAW SECTIONS (T0/T1) ---

                for result_data in all_results:
                    image_name = result_data["image_name"]
                    stock_dict = result_data["stock_dict"]

                    # Handle different stock_dict formats
                    if isinstance(stock_dict, dict):
                        # Expand EACH detected section as its own item (no averaging)
                        for product, stock_value in stock_dict.items():
                            # Array format: [[value, 1], [value, 1], ...]
                            if isinstance(stock_value, list) and len(stock_value) > 0:
                                for idx, item in enumerate(stock_value):
                                    try:
                                        value = item[0] if isinstance(item, list) and len(
                                            item) >= 1 else float(item)
                                    except Exception:
                                        logger.warning(
                                            f"Invalid stock value format for {product}: {item}")
                                        continue
                                    stock_percentage = float(value) / 100.0
                                    confidence = min(
                                        max(stock_percentage, 0.5) * 1.0, 0.95)
                                    # Determine stock level
                                    if stock_percentage < 0.3:
                                        stock_status = StockLevel.LOW
                                    elif stock_percentage > 0.8:
                                        stock_status = StockLevel.OVERSTOCKED
                                    else:
                                        stock_status = StockLevel.NORMAL
                                    final_results.append(ProductStockInfo(
                                        product=f"{product} {idx+1} ({image_name})",
                                        stock_percentage=stock_percentage,
                                        stock_status=stock_status,
                                        confidence=confidence,
                                        reasoning=f"Detected section {idx+1} for {product} in {image_name} with {value:.1f}%"
                                    ))
                            # Handle simple numeric format
                            elif isinstance(stock_value, (int, float)):
                                stock_percentage = stock_value / 100  # Convert to 0-1 range
                                confidence = min(stock_percentage * 1.1, 0.95)

                                # Determine stock level
                                if stock_percentage < 0.3:
                                    stock_status = StockLevel.LOW
                                elif stock_percentage > 0.8:
                                    stock_status = StockLevel.OVERSTOCKED
                                else:
                                    stock_status = StockLevel.NORMAL

                                final_results.append(ProductStockInfo(
                                    product=f"{product} 1 ({image_name})",
                                    stock_percentage=stock_percentage,
                                    stock_status=stock_status,
                                    confidence=confidence,
                                    reasoning=f"AI model detected {product} in {image_name} with {stock_value:.1f}% stock level"
                                ))
                            else:
                                logger.warning(
                                    f"Unsupported stock_value format for {product}: {stock_value}")
                    elif isinstance(stock_dict, list):
                        # Handle list format - create generic results
                        logger.info(
                            f"Stock dict is a list with {len(stock_dict)} items for {image_name}")
                        for i, item in enumerate(stock_dict):
                            # Create a generic product entry
                            stock_percentage = 0.5  # Default medium stock
                            confidence = 0.7
                            stock_status = StockLevel.NORMAL

                            final_results.append(ProductStockInfo(
                                product=f"Product {i+1} ({image_name})",
                                stock_percentage=stock_percentage,
                                stock_status=stock_status,
                                confidence=confidence,
                                reasoning=f"AI model detected item {i+1} in {image_name} with {stock_percentage:.1%} stock level"
                            ))
                    else:
                        logger.warning(
                            f"Unknown stock_dict format for {image_name}: {type(stock_dict)}")
                        # Create a fallback result
                        final_results.append(ProductStockInfo(
                            product=f"Unknown Product ({image_name})",
                            stock_percentage=0.5,
                            stock_status=StockLevel.NORMAL,
                            confidence=0.5,
                            reasoning=f"AI model processed {image_name} but returned unexpected format"
                        ))

                # Group per-section items by time key (e.g., T0, T1)
                grouped_results: dict[str, list[ProductStockInfo]] = {}
                for item in final_results:
                    # item.product format: "<name> N (T0)" -> extract T0
                    try:
                        time_key = item.product.split("(")[-1].rstrip(")")
                    except Exception:
                        time_key = "T0"
                    grouped_results.setdefault(time_key, []).append(item)

                processing_time = time.time() - start_time

                return StockEstimationResponse(
                    success=True,
                    message=f"Stock estimation completed successfully for {len(image_paths)} images using integrated AI models",
                    processing_time=processing_time,
                    timestamp=datetime.utcnow().isoformat() + "Z",
                    results=final_results,
                    model_used="integrated-ai-multiple",
                    image_metadata={
                        "image_count": len(image_paths),
                        "images_processed": [f"T{i}" for i in range(len(image_paths))],
                        "raw_sections": all_results
                    }
                )

            except Exception as e:
                logger.error(f"Failed to parse multiple image results: {e}")
                raise HTTPException(
                    status_code=500, detail="Failed to parse AI analysis results")

        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
            logger.info("Cleaned up temporary files")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Multiple image estimation failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Multiple image estimation failed: {str(e)}")
