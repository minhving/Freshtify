"""
Pydantic models for API request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class StockLevel(str, Enum):
    """Stock level status enumeration."""
    LOW = "low"
    NORMAL = "normal"
    OVERSTOCKED = "overstocked"

class ProductType(str, Enum):
    """Supported product types."""
    BANANA = "banana"
    BROCCOLI = "broccoli"
    AVOCADO = "avocado"
    TOMATO = "tomato"
    ONION = "onion"

class StockEstimationRequest(BaseModel):
    """Request model for stock estimation."""
    model_type: str = Field(default="qwen-vl", description="AI model to use for estimation")
    products: Optional[List[ProductType]] = Field(default=None, description="Specific products to analyze")
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")

class ProductStockInfo(BaseModel):
    """Information about a product's stock level."""
    product: str  # Changed from ProductType to str to allow any product name
    stock_percentage: float = Field(ge=0.0, le=1.0, description="Stock level as percentage (0-1)")
    stock_status: StockLevel
    confidence: float = Field(ge=0.0, le=1.0, description="Model confidence in the estimation")
    bounding_box: Optional[Dict[str, float]] = Field(default=None, description="Bounding box coordinates")
    reasoning: Optional[str] = Field(default=None, description="Model's reasoning for the estimation")

class StockEstimationResponse(BaseModel):
    """Response model for stock estimation."""
    success: bool
    message: str
    processing_time: float = Field(description="Time taken for processing in seconds")
    timestamp: datetime = Field(default_factory=datetime.now)
    results: List[ProductStockInfo]
    model_used: str
    image_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadata about the processed image")

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str
    models_loaded: List[str]
    gpu_available: bool

class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    error: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ModelInfo(BaseModel):
    """Information about available AI models."""
    name: str
    type: str  # "vision-language", "segmentation", "depth-estimation"
    description: str
    supported_products: List[ProductType]
    requires_gpu: bool
    estimated_processing_time: float  # in seconds
