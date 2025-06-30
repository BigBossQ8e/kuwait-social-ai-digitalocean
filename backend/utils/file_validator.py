"""
File validation utilities using python-magic for proper MIME type detection
"""

import os
import magic
from typing import Dict, Any, List, Optional
from werkzeug.datastructures import FileStorage
import hashlib
from datetime import datetime

class FileValidator:
    """Advanced file validation using python-magic"""
    
    def __init__(self):
        # Initialize magic for MIME type detection
        self.mime = magic.Magic(mime=True)
        self.file_magic = magic.Magic()
        
        # Define allowed MIME types for different file categories
        self.allowed_mime_types = {
            'image': [
                'image/jpeg',
                'image/png',
                'image/gif',
                'image/webp',
                'image/bmp'
            ],
            'video': [
                'video/mp4',
                'video/quicktime',  # .mov
                'video/x-msvideo',  # .avi
                'video/webm'
            ],
            'document': [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
                'text/plain'
            ],
            'audio': [
                'audio/mpeg',  # .mp3
                'audio/wav',
                'audio/ogg',
                'audio/webm'
            ]
        }
        
        # File size limits by type (in bytes)
        self.size_limits = {
            'image': 10 * 1024 * 1024,      # 10MB
            'video': 100 * 1024 * 1024,     # 100MB
            'document': 5 * 1024 * 1024,    # 5MB
            'audio': 20 * 1024 * 1024       # 20MB
        }
        
        # Dangerous file extensions to block
        self.blocked_extensions = {
            '.exe', '.bat', '.cmd', '.com', '.scr', '.vbs', '.js',
            '.jar', '.app', '.deb', '.rpm', '.dmg', '.pkg', '.run'
        }
    
    def validate_file(self, file: FileStorage, file_type: str = 'image') -> Dict[str, Any]:
        """
        Validate uploaded file for security and appropriateness
        
        Args:
            file: Werkzeug FileStorage object
            file_type: Expected file type ('image', 'video', 'document', 'audio')
            
        Returns:
            Dictionary with validation results
        """
        issues = []
        warnings = []
        info = {}
        
        # Check if file exists
        if not file or not file.filename:
            issues.append('No file provided')
            return self._create_response(False, issues, warnings, info)
        
        # Save current position and read file content for magic
        file.seek(0)
        file_content = file.read(2048)  # Read first 2KB for magic detection
        file.seek(0)  # Reset position
        
        # Detect MIME type using python-magic
        try:
            detected_mime = self.mime.from_buffer(file_content)
            file_description = self.file_magic.from_buffer(file_content)
            info['detected_mime'] = detected_mime
            info['file_description'] = file_description
        except Exception as e:
            issues.append(f'Failed to detect file type: {str(e)}')
            return self._create_response(False, issues, warnings, info)
        
        # Validate MIME type
        allowed_mimes = self.allowed_mime_types.get(file_type, [])
        if detected_mime not in allowed_mimes:
            issues.append(
                f'Invalid file type. Expected {file_type}, '
                f'detected: {detected_mime}'
            )
            info['allowed_types'] = allowed_mimes
        
        # Check file extension
        filename = file.filename.lower()
        extension = os.path.splitext(filename)[1]
        info['extension'] = extension
        
        # Block dangerous extensions
        if extension in self.blocked_extensions:
            issues.append(f'File extension {extension} is not allowed for security reasons')
        
        # Check filename for security issues
        if '..' in filename or '/' in filename or '\\' in filename:
            issues.append('Invalid filename - contains path traversal characters')
        
        # Validate filename length
        if len(filename) > 255:
            issues.append('Filename too long (max 255 characters)')
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset position
        info['file_size_bytes'] = file_size
        info['file_size_mb'] = round(file_size / (1024 * 1024), 2)
        
        size_limit = self.size_limits.get(file_type, 10 * 1024 * 1024)
        if file_size > size_limit:
            issues.append(
                f'File size ({info["file_size_mb"]}MB) exceeds limit '
                f'({round(size_limit / (1024 * 1024), 2)}MB)'
            )
        
        # Additional checks for specific file types
        if file_type == 'image' and not issues:
            image_info = self._validate_image_specific(file, detected_mime)
            info.update(image_info.get('info', {}))
            issues.extend(image_info.get('issues', []))
            warnings.extend(image_info.get('warnings', []))
        
        # Calculate file hash for duplicate detection
        file.seek(0)
        file_hash = hashlib.sha256(file.read()).hexdigest()
        file.seek(0)
        info['file_hash'] = file_hash
        
        # Check for malware signatures (basic check)
        if self._check_malware_signatures(file_content):
            issues.append('File contains suspicious content')
        
        return self._create_response(len(issues) == 0, issues, warnings, info)
    
    def _validate_image_specific(self, file: FileStorage, mime_type: str) -> Dict[str, Any]:
        """Additional validation specific to images"""
        from PIL import Image
        import io
        
        issues = []
        warnings = []
        info = {}
        
        try:
            # Open image with PIL
            file.seek(0)
            image = Image.open(io.BytesIO(file.read()))
            file.seek(0)
            
            # Get image info
            info['dimensions'] = f'{image.width}x{image.height}'
            info['mode'] = image.mode
            info['format'] = image.format
            
            # Check dimensions
            if image.width > 10000 or image.height > 10000:
                warnings.append('Image dimensions very large (>10000px)')
            
            if image.width < 100 or image.height < 100:
                warnings.append('Image dimensions very small (<100px)')
            
            # Check for animation in GIF
            if mime_type == 'image/gif':
                try:
                    image.seek(1)
                    info['is_animated'] = True
                except EOFError:
                    info['is_animated'] = False
            
            # Check aspect ratio for social media
            aspect_ratio = image.width / image.height
            if 0.8 <= aspect_ratio <= 1.91:
                info['social_media_ready'] = True
            else:
                warnings.append(
                    'Image aspect ratio not optimal for social media '
                    '(recommended: 0.8:1 to 1.91:1)'
                )
                info['social_media_ready'] = False
            
        except Exception as e:
            issues.append(f'Failed to process image: {str(e)}')
        
        return {
            'issues': issues,
            'warnings': warnings,
            'info': info
        }
    
    def _check_malware_signatures(self, content: bytes) -> bool:
        """Basic check for malware signatures"""
        # Simple signature check (in production, use proper antivirus)
        malware_signatures = [
            b'MZ\x90\x00',  # Windows executable
            b'\x7fELF',     # Linux executable
            b'#!/bin/sh',   # Shell script
            b'<script',     # JavaScript in disguise
            b'<?php',       # PHP code
        ]
        
        for signature in malware_signatures:
            if signature in content:
                return True
        
        return False
    
    def _create_response(
        self, 
        is_valid: bool, 
        issues: List[str], 
        warnings: List[str], 
        info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create standardized validation response"""
        return {
            'is_valid': is_valid,
            'issues': issues,
            'warnings': warnings,
            'info': info,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def validate_batch(
        self, 
        files: List[FileStorage], 
        file_type: str = 'image'
    ) -> Dict[str, Any]:
        """Validate multiple files at once"""
        results = []
        total_size = 0
        all_valid = True
        
        for file in files:
            result = self.validate_file(file, file_type)
            results.append({
                'filename': file.filename,
                'validation': result
            })
            
            if not result['is_valid']:
                all_valid = False
            
            total_size += result['info'].get('file_size_bytes', 0)
        
        return {
            'all_valid': all_valid,
            'total_files': len(files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'results': results
        }
    
    def get_mime_type(self, file_path: str) -> str:
        """Get MIME type of a file on disk"""
        try:
            return self.mime.from_file(file_path)
        except Exception as e:
            return f'error: {str(e)}'
    
    def is_safe_filename(self, filename: str) -> bool:
        """Check if filename is safe for storage"""
        # Remove any path components
        filename = os.path.basename(filename)
        
        # Check for special characters
        if not filename or filename.startswith('.'):
            return False
        
        # Allow only alphanumeric, dash, underscore, and dot
        import re
        if not re.match(r'^[\w\-\.]+$', filename):
            return False
        
        # Check extension
        extension = os.path.splitext(filename)[1].lower()
        if extension in self.blocked_extensions:
            return False
        
        return True


# Convenience function for use in routes
def validate_upload(file: FileStorage, file_type: str = 'image') -> Dict[str, Any]:
    """Convenience function to validate file uploads"""
    validator = FileValidator()
    return validator.validate_file(file, file_type)