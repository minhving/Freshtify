"""
File processing service for handling image and video uploads.
"""

import logging
import os
import aiofiles
from typing import Dict, Any, Optional
import cv2
import numpy as np
from PIL import Image
import hashlib
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

class FileProcessor:
    """Service for processing uploaded files."""
    
    def __init__(self):
        self.supported_image_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        self.supported_video_formats = ['.mp4', '.avi', '.mov', '.mkv']
    
    async def process_upload(self, file) -> Dict[str, Any]:
        """
        Process uploaded file and extract relevant data.
        """
        try:
            # Generate unique filename
            file_id = self._generate_file_id(file.filename)
            file_ext = os.path.splitext(file.filename)[1].lower()
            
            # Save file temporarily
            temp_path = await self._save_temp_file(file, file_id, file_ext)
            
            # Process based on file type
            if file_ext in self.supported_image_formats:
                processed_data = await self._process_image(temp_path)
            elif file_ext in self.supported_video_formats:
                processed_data = await self._process_video(temp_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            # Add metadata
            processed_data.update({
                "file_id": file_id,
                "original_filename": file.filename,
                "file_type": "image" if file_ext in self.supported_image_formats else "video",
                "file_size": os.path.getsize(temp_path),
                "processed_at": datetime.now().isoformat()
            })
            
            # Clean up temp file
            await self._cleanup_temp_file(temp_path)
            
            return processed_data
        
        except Exception as e:
            logger.error(f"File processing failed: {str(e)}")
            raise
    
    async def _save_temp_file(self, file, file_id: str, file_ext: str) -> str:
        """Save uploaded file temporarily."""
        temp_filename = f"{file_id}{file_ext}"
        temp_path = os.path.join(settings.UPLOAD_DIR, temp_filename)
        
        # Ensure upload directory exists
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Save file
        async with aiofiles.open(temp_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return temp_path
    
    async def _process_image(self, image_path: str) -> Dict[str, Any]:
        """Process image file and extract features."""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not load image")
            
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Get image properties
            height, width, channels = image.shape
            
            # Extract basic features
            features = {
                "image_array": image_rgb,
                "height": height,
                "width": width,
                "channels": channels,
                "aspect_ratio": width / height,
                "metadata": {
                    "format": "RGB",
                    "dtype": str(image_rgb.dtype),
                    "shape": image_rgb.shape
                }
            }
            
            # Extract additional features for stock estimation
            features.update(self._extract_image_features(image_rgb))
            
            return features
        
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            raise
    
    async def _process_video(self, video_path: str) -> Dict[str, Any]:
        """Process video file and extract key frames."""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError("Could not open video file")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Extract key frames (every 30 frames or at specific intervals)
            key_frames = []
            frame_interval = max(1, frame_count // 10)  # Extract up to 10 frames
            
            frame_idx = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % frame_interval == 0:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    key_frames.append({
                        "frame_number": frame_idx,
                        "timestamp": frame_idx / fps if fps > 0 else 0,
                        "image_array": frame_rgb
                    })
                
                frame_idx += 1
            
            cap.release()
            
            # Process the first key frame as primary image
            primary_frame = key_frames[0] if key_frames else None
            
            features = {
                "video_frames": key_frames,
                "primary_image": primary_frame["image_array"] if primary_frame else None,
                "fps": fps,
                "frame_count": frame_count,
                "duration": duration,
                "metadata": {
                    "type": "video",
                    "key_frames_extracted": len(key_frames)
                }
            }
            
            # Extract features from primary frame
            if primary_frame:
                features.update(self._extract_image_features(primary_frame["image_array"]))
            
            return features
        
        except Exception as e:
            logger.error(f"Video processing failed: {str(e)}")
            raise
    
    def _extract_image_features(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract features from image for stock estimation."""
        try:
            # Convert to different color spaces
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            
            # Calculate color statistics
            color_features = {
                "mean_rgb": np.mean(image, axis=(0, 1)).tolist(),
                "std_rgb": np.std(image, axis=(0, 1)).tolist(),
                "mean_hsv": np.mean(hsv, axis=(0, 1)).tolist(),
                "brightness": np.mean(cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)),
                "contrast": np.std(cv2.cvtColor(image, cv2.COLOR_RGB2GRAY))
            }
            
            # Edge detection for shelf structure analysis
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            # Texture analysis
            texture_features = {
                "edge_density": edge_density,
                "texture_variance": np.var(gray)
            }
            
            return {
                "color_features": color_features,
                "texture_features": texture_features,
                "image_quality": self._assess_image_quality(image)
            }
        
        except Exception as e:
            logger.warning(f"Feature extraction failed: {str(e)}")
            return {}
    
    def _assess_image_quality(self, image: np.ndarray) -> Dict[str, float]:
        """Assess image quality metrics."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Calculate Laplacian variance (sharpness)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Calculate brightness and contrast
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            return {
                "sharpness": float(laplacian_var),
                "brightness": float(brightness),
                "contrast": float(contrast),
                "quality_score": min(1.0, (laplacian_var / 1000) * (contrast / 100))
            }
        
        except Exception as e:
            logger.warning(f"Image quality assessment failed: {str(e)}")
            return {"quality_score": 0.5}
    
    def _generate_file_id(self, filename: str) -> str:
        """Generate unique file ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_obj = hashlib.md5(filename.encode())
        file_hash = hash_obj.hexdigest()[:8]
        return f"{timestamp}_{file_hash}"
    
    async def _cleanup_temp_file(self, file_path: str):
        """Clean up temporary file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {file_path}: {str(e)}")
    
    def validate_file(self, filename: str, file_size: int) -> bool:
        """Validate uploaded file."""
        # Check file extension
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            return False
        
        # Check file size
        if file_size > settings.MAX_FILE_SIZE:
            return False
        
        return True
