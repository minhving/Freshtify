"""
Utility helper functions for the AI Stock Level Estimation API.
"""

import os
import logging
from typing import Dict, Any, List, Optional
import numpy as np
from PIL import Image
import cv2

logger = logging.getLogger(__name__)

def ensure_directory_exists(directory_path: str) -> None:
    """Ensure directory exists, create if it doesn't."""
    try:
        os.makedirs(directory_path, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create directory {directory_path}: {str(e)}")
        raise

def validate_image_format(image_path: str) -> bool:
    """Validate if file is a supported image format."""
    supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    file_ext = os.path.splitext(image_path)[1].lower()
    return file_ext in supported_formats

def validate_video_format(video_path: str) -> bool:
    """Validate if file is a supported video format."""
    supported_formats = ['.mp4', '.avi', '.mov', '.mkv']
    file_ext = os.path.splitext(video_path)[1].lower()
    return file_ext in supported_formats

def resize_image_if_needed(image: np.ndarray, max_size: int = 1024) -> np.ndarray:
    """Resize image if it's too large while maintaining aspect ratio."""
    height, width = image.shape[:2]
    
    if max(height, width) <= max_size:
        return image
    
    # Calculate new dimensions
    if height > width:
        new_height = max_size
        new_width = int(width * max_size / height)
    else:
        new_width = max_size
        new_height = int(height * max_size / width)
    
    # Resize image
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height}")
    return resized

def normalize_image(image: np.ndarray) -> np.ndarray:
    """Normalize image to 0-1 range."""
    if image.dtype == np.uint8:
        return image.astype(np.float32) / 255.0
    return image.astype(np.float32)

def denormalize_image(image: np.ndarray) -> np.ndarray:
    """Convert normalized image back to 0-255 range."""
    if image.max() <= 1.0:
        return (image * 255).astype(np.uint8)
    return image.astype(np.uint8)

def calculate_image_similarity(img1: np.ndarray, img2: np.ndarray) -> float:
    """Calculate similarity between two images using structural similarity."""
    try:
        from skimage.metrics import structural_similarity as ssim
        
        # Convert to grayscale if needed
        if len(img1.shape) == 3:
            img1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
        if len(img2.shape) == 3:
            img2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)
        
        # Resize images to same size
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        
        # Calculate SSIM
        similarity = ssim(img1, img2)
        return float(similarity)
    
    except ImportError:
        logger.warning("scikit-image not available, using basic correlation")
        # Fallback to basic correlation
        img1_flat = img1.flatten().astype(np.float32)
        img2_flat = img2.flatten().astype(np.float32)
        
        if len(img1_flat) != len(img2_flat):
            return 0.0
        
        correlation = np.corrcoef(img1_flat, img2_flat)[0, 1]
        return float(correlation) if not np.isnan(correlation) else 0.0

def extract_color_histogram(image: np.ndarray, bins: int = 32) -> Dict[str, np.ndarray]:
    """Extract color histograms from image."""
    histograms = {}
    
    # RGB histograms
    for i, color in enumerate(['red', 'green', 'blue']):
        hist, _ = np.histogram(image[:, :, i], bins=bins, range=(0, 256))
        histograms[color] = hist.astype(np.float32) / hist.sum()
    
    # HSV histograms
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    for i, color in enumerate(['hue', 'saturation', 'value']):
        hist, _ = np.histogram(hsv[:, :, i], bins=bins, range=(0, 256))
        histograms[f"hsv_{color}"] = hist.astype(np.float32) / hist.sum()
    
    return histograms

def detect_shelf_lines(image: np.ndarray) -> List[Dict[str, Any]]:
    """Detect horizontal lines that might represent shelf edges."""
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Detect lines using Hough transform
        lines = cv2.HoughLinesP(
            edges, 
            rho=1, 
            theta=np.pi/180, 
            threshold=100,
            minLineLength=100,
            maxLineGap=10
        )
        
        if lines is None:
            return []
        
        # Filter for horizontal lines
        horizontal_lines = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            
            # Consider lines within ±15 degrees of horizontal as shelf lines
            if abs(angle) < 15 or abs(angle - 180) < 15:
                horizontal_lines.append({
                    "start": (x1, y1),
                    "end": (x2, y2),
                    "angle": angle,
                    "length": np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                })
        
        return horizontal_lines
    
    except Exception as e:
        logger.warning(f"Shelf line detection failed: {str(e)}")
        return []

def calculate_stock_density(image: np.ndarray, region: Optional[Dict[str, int]] = None) -> float:
    """Calculate stock density in a region of the image."""
    try:
        if region:
            x, y, w, h = region['x'], region['y'], region['width'], region['height']
            roi = image[y:y+h, x:x+w]
        else:
            roi = image
        
        # Convert to grayscale
        gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
        
        # Apply threshold to detect objects
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Calculate density as ratio of white pixels (objects) to total pixels
        total_pixels = thresh.size
        object_pixels = np.sum(thresh > 0)
        density = object_pixels / total_pixels
        
        return float(density)
    
    except Exception as e:
        logger.warning(f"Stock density calculation failed: {str(e)}")
        return 0.0

def format_processing_time(seconds: float) -> str:
    """Format processing time in a human-readable format."""
    if seconds < 1:
        return f"{seconds*1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"

def create_response_metadata(
    processing_time: float,
    model_used: str,
    image_shape: Optional[tuple] = None,
    additional_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create standardized response metadata."""
    metadata = {
        "processing_time": processing_time,
        "processing_time_formatted": format_processing_time(processing_time),
        "model_used": model_used,
        "timestamp": None  # Will be set by the calling function
    }
    
    if image_shape:
        metadata["image_dimensions"] = {
            "height": image_shape[0],
            "width": image_shape[1],
            "channels": image_shape[2] if len(image_shape) > 2 else 1
        }
    
    if additional_info:
        metadata.update(additional_info)
    
    return metadata
