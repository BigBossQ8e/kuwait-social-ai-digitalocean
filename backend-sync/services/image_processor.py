"""
Image Processing Service for Kuwait Social AI
"""

import os
import io
import logging
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np
from typing import Dict, Tuple, Optional
import requests
from werkzeug.utils import secure_filename
import hashlib
from datetime import datetime
from exceptions import (
    ImageProcessingException, InvalidImageException, 
    ImageSizeException, ContentModerationException
)
from config.platform_config import PlatformConfig

class ImageProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.upload_folder = os.getenv('UPLOAD_FOLDER', '/tmp/uploads')
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.supported_formats = ['JPEG', 'PNG', 'GIF', 'WEBP']
        
        # Load configuration
        self.config = PlatformConfig
        
        # Get platform dimensions from config
        self.platform_dimensions = {}
        for platform in ['instagram', 'snapchat', 'tiktok', 'twitter']:
            formats = self.config.get_platform_limit(platform, 'formats', {})
            if formats:
                self.platform_dimensions[platform] = {
                    fmt_name: (fmt_data['width'], fmt_data['height'])
                    for fmt_name, fmt_data in formats.items()
                }
        
        # Ensure upload folder exists
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def process_image(
        self, 
        image_source: str, 
        enhance: bool = True,
        resize_for: str = 'instagram',
        format_type: str = 'square',
        quality: int = 90
    ) -> Dict:
        """Process image with enhancement and platform optimization"""
        
        try:
            # Load image
            if isinstance(image_source, str) and image_source.startswith('http'):
                image = self._download_image(image_source)
            else:
                image = self._load_image(image_source)
            
            # Validate image
            self._validate_image(image)
            
            # Apply enhancements if requested
            if enhance:
                image = self._enhance_image(image)
            
            # Resize for platform
            if resize_for and resize_for in self.platform_dimensions:
                dimensions = self.platform_dimensions[resize_for].get(
                    format_type, 
                    self.platform_dimensions[resize_for]['square']
                )
                image = self._resize_for_platform(image, dimensions)
            
            # Generate filename
            filename = self._generate_filename(image.format)
            filepath = os.path.join(self.upload_folder, filename)
            
            # Save processed image
            self._save_image(image, filepath, quality)
            
            # Generate thumbnail
            thumbnail_path = self._create_thumbnail(image, filename)
            
            # Get image metadata
            metadata = self._extract_metadata(image, filepath)
            
            return {
                'success': True,
                'url': f'/uploads/{filename}',
                'filepath': filepath,
                'thumbnail_url': f'/uploads/thumbnails/{os.path.basename(thumbnail_path)}',
                'dimensions': metadata['dimensions'],
                'format': metadata['format'],
                'file_size': metadata['file_size'],
                'enhancements_applied': enhance,
                'platform_optimized': resize_for
            }
            
        except (ImageProcessingException, InvalidImageException, ImageSizeException) as e:
            # Re-raise known exceptions
            raise e
        except Exception as e:
            self.logger.error(f"Unexpected error in image processing: {str(e)}")
            raise ImageProcessingException(
                "Failed to process image",
                details={'error': str(e)}
            )
    
    def _download_image(self, url: str) -> Image.Image:
        """Download image from URL"""
        try:
            response = requests.get(url, timeout=10, stream=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                raise InvalidImageException(
                    reason=f"URL does not point to an image (content-type: {content_type})"
                )
            
            # Check file size
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.max_file_size:
                raise ImageSizeException(
                    current_size=int(content_length) / (1024 * 1024),
                    max_size=self.max_file_size / (1024 * 1024)
                )
            
            # Load image
            return Image.open(io.BytesIO(response.content))
            
        except requests.RequestException as e:
            raise ImageProcessingException(
                f"Failed to download image from URL",
                details={'url': url, 'error': str(e)}
            )
    
    def _load_image(self, filepath: str) -> Image.Image:
        """Load image from file"""
        try:
            return Image.open(filepath)
        except IOError as e:
            raise InvalidImageException(
                reason=f"Cannot open image file: {str(e)}"
            )
    
    def _validate_image(self, image: Image.Image):
        """Validate image format and properties"""
        # Check format
        if image.format not in self.supported_formats:
            raise InvalidImageException(
                reason=f"Unsupported image format: {image.format}",
                supported_formats=self.supported_formats
            )
        
        # Check mode
        if image.mode not in ['RGB', 'RGBA', 'L']:
            try:
                # Try to convert to RGB
                image = image.convert('RGB')
            except Exception as e:
                raise InvalidImageException(
                    reason=f"Cannot process image mode: {image.mode}"
                )
        
        # Check dimensions
        width, height = image.size
        if width < 100 or height < 100:
            raise InvalidImageException(
                reason=f"Image too small: {width}x{height}. Minimum size is 100x100"
            )
        
        if width > 10000 or height > 10000:
            raise InvalidImageException(
                reason=f"Image too large: {width}x{height}. Maximum dimension is 10000px"
            )
    
    def _enhance_image(self, image: Image.Image) -> Image.Image:
        """Apply AI-based enhancements to image"""
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Auto-adjust brightness
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.1)  # Slight brightness increase
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)  # Moderate contrast increase
            
            # Enhance color saturation
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.15)  # Slight saturation increase
            
            # Apply slight sharpening
            image = image.filter(ImageFilter.SHARPEN)
            
            # Optional: Apply Instagram-like filter
            # This is a simplified version - in production, use more sophisticated filters
            image = self._apply_kuwait_filter(image)
            
            return image
            
        except Exception as e:
            self.logger.warning(f"Enhancement failed, returning original: {str(e)}")
            return image
    
    def _apply_kuwait_filter(self, image: Image.Image) -> Image.Image:
        """Apply Kuwait-themed filter (warm, vibrant colors)"""
        try:
            # Create a warm overlay
            overlay = Image.new('RGB', image.size, (255, 245, 220))  # Warm beige
            
            # Blend with original
            return Image.blend(image, overlay, 0.1)  # 10% blend
        except:
            return image
    
    def _resize_for_platform(
        self, 
        image: Image.Image, 
        target_dimensions: Tuple[int, int]
    ) -> Image.Image:
        """Resize image for specific platform requirements"""
        target_width, target_height = target_dimensions
        
        # Calculate aspect ratios
        img_ratio = image.width / image.height
        target_ratio = target_width / target_height
        
        if abs(img_ratio - target_ratio) < 0.01:
            # Same aspect ratio, just resize
            return image.resize(target_dimensions, Image.Resampling.LANCZOS)
        else:
            # Different aspect ratio, crop and resize
            # First, resize to fit one dimension
            if img_ratio > target_ratio:
                # Image is wider, fit height
                new_width = int(target_height * img_ratio)
                image = image.resize((new_width, target_height), Image.Resampling.LANCZOS)
            else:
                # Image is taller, fit width
                new_height = int(target_width / img_ratio)
                image = image.resize((target_width, new_height), Image.Resampling.LANCZOS)
            
            # Center crop to target dimensions
            left = (image.width - target_width) // 2
            top = (image.height - target_height) // 2
            right = left + target_width
            bottom = top + target_height
            
            return image.crop((left, top, right, bottom))
    
    def _generate_filename(self, format: str) -> str:
        """Generate unique filename"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_str = hashlib.md5(os.urandom(16)).hexdigest()[:8]
        extension = format.lower() if format else 'jpg'
        return f"kuwait_social_{timestamp}_{random_str}.{extension}"
    
    def _save_image(self, image: Image.Image, filepath: str, quality: int):
        """Save image with optimization"""
        try:
            # Convert to RGB if saving as JPEG
            if filepath.lower().endswith('.jpg') or filepath.lower().endswith('.jpeg'):
                if image.mode in ('RGBA', 'LA', 'P'):
                    # Create white background
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = background
            
            # Save with optimization
            image.save(filepath, quality=quality, optimize=True)
            
            # Check final file size
            file_size = os.path.getsize(filepath)
            if file_size > self.max_file_size:
                os.remove(filepath)
                raise ImageSizeException(
                    current_size=file_size / (1024 * 1024),
                    max_size=self.max_file_size / (1024 * 1024)
                )
                
        except IOError as e:
            raise ImageProcessingException(
                f"Failed to save image",
                details={'filepath': filepath, 'error': str(e)}
            )
    
    def _create_thumbnail(self, image: Image.Image, original_filename: str) -> str:
        """Create thumbnail version"""
        thumbnail_dir = os.path.join(self.upload_folder, 'thumbnails')
        os.makedirs(thumbnail_dir, exist_ok=True)
        
        # Create thumbnail
        thumbnail = image.copy()
        thumbnail.thumbnail((300, 300), Image.Resampling.LANCZOS)
        
        # Save thumbnail
        thumb_filename = f"thumb_{original_filename}"
        thumb_path = os.path.join(thumbnail_dir, thumb_filename)
        thumbnail.save(thumb_path, quality=85, optimize=True)
        
        return thumb_path
    
    def _extract_metadata(self, image: Image.Image, filepath: str) -> Dict:
        """Extract image metadata"""
        return {
            'dimensions': {
                'width': image.width,
                'height': image.height
            },
            'format': image.format,
            'mode': image.mode,
            'file_size': os.path.getsize(filepath),
            'has_transparency': image.mode in ('RGBA', 'LA', 'PA')
        }
    
    def validate_image_content(self, image_path: str) -> Dict:
        """Validate image content for appropriateness (placeholder)"""
        # In production, integrate with content moderation API
        # For now, return success
        return {
            'is_appropriate': True,
            'confidence': 0.95,
            'warnings': []
        }
    
    def create_text_overlay(
        self, 
        image_path: str, 
        text: str, 
        position: str = 'bottom',
        font_size: int = 40
    ) -> str:
        """Add text overlay to image"""
        try:
            image = Image.open(image_path)
            
            # This is a simplified version
            # In production, use proper fonts and positioning
            
            # For now, just return the original path
            # Implement actual text overlay when needed
            return image_path
            
        except Exception as e:
            self.logger.error(f"Failed to add text overlay: {str(e)}")
            raise ImageProcessingException(
                "Failed to add text overlay",
                details={'error': str(e)}
            )