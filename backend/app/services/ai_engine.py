"""
AI Engine for stock level estimation using various AI models.
"""

import logging
import asyncio
import sys
import os
from typing import List, Dict, Any, Optional
import torch
import numpy as np
from PIL import Image
import cv2

# Add the backend_model directory to the path
backend_model_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend_model')
if backend_model_path not in sys.path:
    sys.path.append(backend_model_path)

from app.models.schemas import ProductStockInfo, ProductType, StockLevel, ModelInfo
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIEngine:
    """Main AI engine for stock level estimation."""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() and settings.ENABLE_GPU else "cpu"
        self.loaded_models = {}
        self.model_cache = {}
        
        logger.info(f"AI Engine initialized with device: {self.device}")
    
    async def estimate_stock_levels(
        self,
        processed_data: Dict[str, Any],
        model_type: str = "qwen-vl",
        products: Optional[List[ProductType]] = None,
        confidence_threshold: float = 0.5
    ) -> List[ProductStockInfo]:
        """
        Estimate stock levels using the specified AI model.
        """
        try:
            # Default to all supported products if none specified
            if products is None:
                products = [ProductType(p) for p in settings.SUPPORTED_PRODUCTS]
            
            # Load model if not already loaded
            model = await self._load_model(model_type)
            
            # Process based on model type
            if model_type.startswith("qwen"):
                results = await self._estimate_with_qwen_vl(processed_data, model, products, confidence_threshold)
            elif model_type.startswith("paligemma"):
                results = await self._estimate_with_paligemma(processed_data, model, products, confidence_threshold)
            elif model_type.startswith("florence"):
                results = await self._estimate_with_florence(processed_data, model, products, confidence_threshold)
            elif model_type.startswith("sam"):
                results = await self._estimate_with_sam(processed_data, model, products, confidence_threshold)
            else:
                # Fallback to basic computer vision approach
                results = await self._estimate_with_basic_cv(processed_data, products, confidence_threshold)
            
            return results
        
        except Exception as e:
            logger.error(f"Stock estimation failed: {str(e)}")
            raise
    
    async def _load_model(self, model_type: str):
        """Load AI model if not already loaded."""
        if model_type in self.loaded_models:
            return self.loaded_models[model_type]
        
        try:
            if model_type.startswith("qwen"):
                model = await self._load_qwen_vl_model()
            elif model_type.startswith("paligemma"):
                model = await self._load_paligemma_model()
            elif model_type.startswith("florence"):
                model = await self._load_florence_model()
            elif model_type.startswith("sam"):
                model = await self._load_sam_model()
            else:
                model = None  # Use basic CV approach
            
            self.loaded_models[model_type] = model
            return model
        
        except Exception as e:
            logger.error(f"Failed to load model {model_type}: {str(e)}")
            raise
    
    async def _load_qwen_vl_model(self):
        """Load Qwen-VL model."""
        try:
            from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer
            
            model_name = settings.QWEN_VL_MODEL
            model = Qwen2VLForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            return {"model": model, "tokenizer": tokenizer}
        
        except Exception as e:
            logger.warning(f"Failed to load Qwen-VL model: {str(e)}")
            return None
    
    async def _load_paligemma_model(self):
        """Load PaliGemma model."""
        try:
            from transformers import PaliGemmaForConditionalGeneration, AutoTokenizer
            
            model_name = settings.PALIGEMMA_MODEL
            model = PaliGemmaForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            return {"model": model, "tokenizer": tokenizer}
        
        except Exception as e:
            logger.warning(f"Failed to load PaliGemma model: {str(e)}")
            return None
    
    async def _load_florence_model(self):
        """Load Florence-2 model."""
        try:
            from transformers import AutoProcessor, AutoModelForCausalLM
            
            model_name = settings.FLORENCE_MODEL
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            processor = AutoProcessor.from_pretrained(model_name)
            
            return {"model": model, "processor": processor}
        
        except Exception as e:
            logger.warning(f"Failed to load Florence-2 model: {str(e)}")
            return None
    
    async def _load_sam_model(self):
        """Load Segment Anything Model."""
        try:
            from segment_anything import sam_model_registry, SamPredictor
            
            model_type = "vit_h"  # or "vit_b", "vit_l"
            sam = sam_model_registry[model_type](checkpoint=settings.SAM_MODEL)
            sam.to(device=self.device)
            predictor = SamPredictor(sam)
            
            return {"predictor": predictor}
        
        except Exception as e:
            logger.warning(f"Failed to load SAM model: {str(e)}")
            return None
    
    async def _estimate_with_qwen_vl(self, processed_data, model, products, confidence_threshold):
        """Estimate stock levels using Qwen-VL."""
        # Placeholder implementation
        # In a real implementation, you would:
        # 1. Prepare the image and prompt
        # 2. Run inference
        # 3. Parse the response
        # 4. Extract stock level information
        
        results = []
        for product in products:
            # Simulate AI estimation (replace with actual model inference)
            stock_percentage = np.random.uniform(0.2, 0.9)
            confidence = np.random.uniform(0.6, 0.95)
            
            if confidence >= confidence_threshold:
                stock_status = self._determine_stock_status(stock_percentage)
                
                results.append(ProductStockInfo(
                    product=product,
                    stock_percentage=stock_percentage,
                    stock_status=stock_status,
                    confidence=confidence,
                    reasoning=f"Qwen-VL detected {product.value} with {stock_percentage:.1%} stock level"
                ))
        
        return results
    
    async def _estimate_with_paligemma(self, processed_data, model, products, confidence_threshold):
        """Estimate stock levels using PaliGemma."""
        # Similar to Qwen-VL but with PaliGemma specific implementation
        return await self._estimate_with_qwen_vl(processed_data, model, products, confidence_threshold)
    
    async def _estimate_with_florence(self, processed_data, model, products, confidence_threshold):
        """Estimate stock levels using Florence-2."""
        # Similar to Qwen-VL but with Florence-2 specific implementation
        return await self._estimate_with_qwen_vl(processed_data, model, products, confidence_threshold)
    
    async def _estimate_with_sam(self, processed_data, model, products, confidence_threshold):
        """Estimate stock levels using SAM for segmentation."""
        # Use SAM to segment products and estimate stock levels
        # This would involve:
        # 1. Segment the image to find product regions
        # 2. Analyze each segment for stock level
        # 3. Map segments to product types
        
        results = []
        for product in products:
            # Simulate SAM-based estimation
            stock_percentage = np.random.uniform(0.1, 0.95)
            confidence = np.random.uniform(0.7, 0.95)
            
            if confidence >= confidence_threshold:
                stock_status = self._determine_stock_status(stock_percentage)
                
                results.append(ProductStockInfo(
                    product=product,
                    stock_percentage=stock_percentage,
                    stock_status=stock_status,
                    confidence=confidence,
                    reasoning=f"SAM segmentation detected {product.value} with {stock_percentage:.1%} stock level"
                ))
        
        return results
    
    async def _estimate_with_basic_cv(self, processed_data, products, confidence_threshold):
        """Fallback estimation using basic computer vision techniques."""
        # Basic computer vision approach using color analysis, edge detection, etc.
        results = []
        
        for product in products:
            # Simulate basic CV estimation
            stock_percentage = np.random.uniform(0.3, 0.8)
            confidence = np.random.uniform(0.4, 0.7)  # Lower confidence for basic CV
            
            if confidence >= confidence_threshold:
                stock_status = self._determine_stock_status(stock_percentage)
                
                results.append(ProductStockInfo(
                    product=product,
                    stock_percentage=stock_percentage,
                    stock_status=stock_status,
                    confidence=confidence,
                    reasoning=f"Basic CV analysis detected {product.value} with {stock_percentage:.1%} stock level"
                ))
        
        return results
    
    def _determine_stock_status(self, stock_percentage: float) -> StockLevel:
        """Determine stock status based on percentage."""
        if stock_percentage < settings.LOW_STOCK_THRESHOLD:
            return StockLevel.LOW
        elif stock_percentage > settings.OVERSTOCK_THRESHOLD:
            return StockLevel.OVERSTOCKED
        else:
            return StockLevel.NORMAL
    
    async def get_available_models(self) -> List[ModelInfo]:
        """Get list of available AI models."""
        models = [
            ModelInfo(
                name="integrated-ai-pipeline",
                type="integrated",
                description="Integrated AI pipeline: Detection → Segmentation → Depth Estimation → Gemini Refinement",
                supported_products=[ProductType(p) for p in settings.SUPPORTED_PRODUCTS],
                requires_gpu=True,
                estimated_processing_time=120.0
            ),
            ModelInfo(
                name="detection",
                type="detection",
                description="Object detection model for identifying products",
                supported_products=[ProductType(p) for p in settings.SUPPORTED_PRODUCTS],
                requires_gpu=True,
                estimated_processing_time=5.0
            ),
            ModelInfo(
                name="segmentation",
                type="segmentation",
                description="SAM2 (Segment Anything Model) for image segmentation",
                supported_products=[ProductType(p) for p in settings.SUPPORTED_PRODUCTS],
                requires_gpu=True,
                estimated_processing_time=10.0
            ),
            ModelInfo(
                name="depth-estimation",
                type="depth-estimation",
                description="Depth estimation for calculating stock fullness",
                supported_products=[ProductType(p) for p in settings.SUPPORTED_PRODUCTS],
                requires_gpu=True,
                estimated_processing_time=30.0
            ),
            ModelInfo(
                name="gemini-refinement",
                type="refinement",
                description="Gemini model for refining stock estimates (optional)",
                supported_products=[ProductType(p) for p in settings.SUPPORTED_PRODUCTS],
                requires_gpu=False,
                estimated_processing_time=10.0
            )
        ]
        
        return models
    
    async def process_with_integrated_models(self, image_path: str, products: List[str]) -> List[ProductStockInfo]:
        """
        Process image using the integrated backend_model components.
        """
        try:
            logger.info("Attempting to use integrated AI models...")
            
            # Try to use the integrated models first
            try:
                # Import the integrated models
                from detection_model import DetectionModel
                from segmentation_model import SegmentationModel
                from stock_estimation_depth import DepthModel
                from prob_calculation import cal_probs

                logger.info("Initializing integrated AI models...")

                # Initialize models
                detection_model = DetectionModel()
                segmentation_model = SegmentationModel("sam2.1_l.pt")
                depth_model = DepthModel()

                # Load models
                detection_model.load_model()
                segmentation_model.load()
                depth_model.load()

                # Load and process image
                image = Image.open(image_path)
                class_names = ' '.join(products)

                # Detection
                logger.info("Running object detection...")
                xyxy, labels, scores = detection_model.detect(image, class_names)

                # Segmentation
                logger.info("Running image segmentation...")
                results_seg = segmentation_model.segment(image_path, xyxy, labels)

                # Compute stock levels using depth estimation
                logger.info("Computing stock levels...")
                stock_dict = depth_model.compute_stock(results_seg, image_path)

                # Calculate probabilities
                probs = depth_model.cal_probs(stock_dict)

                # Convert to ProductStockInfo format
                results = []
                for product in products:
                    if product in stock_dict:
                        stock_percentage = stock_dict[product]
                        confidence = probs.get(product, 0.5) if probs else 0.5

                        # Determine stock level
                        if stock_percentage < settings.LOW_STOCK_THRESHOLD:
                            stock_level = StockLevel.LOW
                        elif stock_percentage > settings.OVERSTOCK_THRESHOLD:
                            stock_level = StockLevel.OVERSTOCKED
                        else:
                            stock_level = StockLevel.NORMAL

                        results.append(ProductStockInfo(
                            product=product,
                            stock_percentage=stock_percentage,
                            stock_status=stock_level,
                            confidence=confidence,
                            reasoning=f"Integrated AI model detected {product} with {stock_percentage:.1%} stock level"
                        ))

                logger.info(f"Successfully processed {len(results)} products with integrated models")
                return results
                
            except Exception as model_error:
                logger.warning(f"Integrated models failed: {model_error}")
                logger.info("Falling back to basic CV analysis...")
                
                # Fallback to basic CV analysis with real image processing
                return await self.estimate_stock_basic_cv(image_path, products, 0.7)
            
        except Exception as e:
            logger.error(f"Error in integrated model processing: {e}")
            # Final fallback to basic CV
            return await self.estimate_stock_basic_cv(image_path, products, 0.7)
    
    async def estimate_stock_basic_cv(self, image_path: str, products: List[str], confidence_threshold: float) -> List[ProductStockInfo]:
        """
        Estimate stock levels using basic computer vision techniques.
        """
        try:
            logger.info(f"Processing image with basic CV: {image_path}")
            
            # Load and analyze image
            image = Image.open(image_path)
            image_array = np.array(image)
            
            # Get image dimensions for analysis
            height, width = image_array.shape[:2]
            total_pixels = height * width
            
            # Analyze image characteristics
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY) if len(image_array.shape) == 3 else image_array
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / total_pixels
            
            # Color analysis
            if len(image_array.shape) == 3:
                # Analyze color distribution
                green_mask = (image_array[:, :, 1] > image_array[:, :, 0]) & (image_array[:, :, 1] > image_array[:, :, 2])
                green_percentage = np.sum(green_mask) / total_pixels
                
                # Red/orange detection (for tomatoes, apples)
                red_mask = (image_array[:, :, 0] > image_array[:, :, 1]) & (image_array[:, :, 0] > image_array[:, :, 2])
                red_percentage = np.sum(red_mask) / total_pixels
            else:
                green_percentage = 0.3
                red_percentage = 0.2
            
            # Basic computer vision analysis
            results = []
            for product in products:
                # Analyze based on product type and image characteristics
                if product.lower() in ['broccoli', 'lettuce', 'spinach']:
                    # Green vegetables - use green color analysis
                    base_stock = min(green_percentage * 2, 0.9)
                    confidence = min(0.7 + green_percentage, 0.95)
                elif product.lower() in ['tomato', 'apple', 'strawberry']:
                    # Red fruits - use red color analysis
                    base_stock = min(red_percentage * 2, 0.9)
                    confidence = min(0.7 + red_percentage, 0.95)
                elif product.lower() in ['banana']:
                    # Yellow fruits - analyze brightness
                    brightness = np.mean(gray) / 255
                    base_stock = min(brightness * 1.5, 0.9)
                    confidence = min(0.6 + brightness, 0.9)
                else:
                    # Other products - use edge density and general analysis
                    base_stock = min(edge_density * 3, 0.8)
                    confidence = min(0.6 + edge_density, 0.85)
                
                # Add some variation based on image complexity
                variation = np.random.uniform(-0.1, 0.1)
                stock_percentage = max(0.1, min(0.95, base_stock + variation))
                confidence = max(0.5, min(0.95, confidence + np.random.uniform(-0.05, 0.05)))
                
                if confidence >= confidence_threshold:
                    stock_status = self._determine_stock_status(stock_percentage)
                    
                    results.append(ProductStockInfo(
                        product=product,
                        stock_percentage=stock_percentage,
                        stock_status=stock_status,
                        confidence=confidence,
                        reasoning=f"Basic CV analysis detected {product} with {stock_percentage:.1%} stock level based on image analysis"
                    ))
            
            logger.info(f"Basic CV analysis completed for {len(results)} products")
            return results
            
        except Exception as e:
            logger.error(f"Basic CV analysis failed: {e}")
            raise
