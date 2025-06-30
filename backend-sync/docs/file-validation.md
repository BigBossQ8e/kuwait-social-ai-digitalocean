# File Validation with python-magic

## Overview

Kuwait Social AI uses `python-magic` for robust file validation, providing proper MIME type detection beyond simple file extension checking. This ensures security and prevents malicious file uploads.

## Installation

### macOS
```bash
# Install libmagic (required by python-magic)
brew install libmagic

# Install python-magic
pip install python-magic==0.4.27
```

### Ubuntu/Debian
```bash
# Install libmagic
sudo apt-get install libmagic1

# Install python-magic
pip install python-magic==0.4.27
```

### CentOS/RHEL/Fedora
```bash
# Install libmagic
sudo yum install file-libs

# Install python-magic
pip install python-magic==0.4.27
```

### Windows
```bash
# python-magic-bin includes the required DLLs
pip install python-magic-bin==0.4.14
```

## Features

### 1. MIME Type Detection
- Uses file content analysis, not just extensions
- Detects actual file type regardless of extension
- Prevents disguised malicious files

### 2. File Categories Supported
- **Images**: JPEG, PNG, GIF, WebP, BMP
- **Videos**: MP4, MOV, AVI, WebM
- **Documents**: PDF, DOC, DOCX, TXT
- **Audio**: MP3, WAV, OGG

### 3. Security Features
- Blocks executable files (.exe, .bat, .sh, etc.)
- Detects malware signatures
- Prevents path traversal attacks
- File size limits by type

### 4. Social Media Optimization
- Checks image dimensions for social platforms
- Validates aspect ratios
- Detects animated GIFs
- Provides optimization suggestions

## Usage

### Basic File Validation
```python
from utils.file_validator import FileValidator

validator = FileValidator()
result = validator.validate_file(uploaded_file, file_type='image')

if result['is_valid']:
    # Process file
    print(f"File type: {result['info']['detected_mime']}")
    print(f"File size: {result['info']['file_size_mb']}MB")
else:
    # Handle validation errors
    for issue in result['issues']:
        print(f"Error: {issue}")
```

### Batch Validation
```python
files = request.files.getlist('images')
result = validator.validate_batch(files, file_type='image')

if result['all_valid']:
    print(f"All {result['total_files']} files are valid")
else:
    for file_result in result['results']:
        if not file_result['validation']['is_valid']:
            print(f"File {file_result['filename']} has issues")
```

### In Routes
```python
from utils.validators import validate_file_upload

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    
    validation = validate_file_upload(file)
    if not validation['is_valid']:
        return jsonify({
            'error': 'File validation failed',
            'issues': validation['issues']
        }), 400
    
    # Process valid file
    return jsonify({'success': True})
```

## Validation Response Structure

```json
{
    "is_valid": true,
    "issues": [],
    "warnings": ["Image dimensions very large (>10000px)"],
    "info": {
        "detected_mime": "image/jpeg",
        "file_description": "JPEG image data, EXIF standard",
        "extension": ".jpg",
        "file_size_bytes": 2048576,
        "file_size_mb": 2.0,
        "file_hash": "sha256_hash_here",
        "dimensions": "1920x1080",
        "mode": "RGB",
        "format": "JPEG",
        "is_animated": false,
        "social_media_ready": true
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## Configuration

### Size Limits
```python
# Default limits by file type
size_limits = {
    'image': 10 * 1024 * 1024,      # 10MB
    'video': 100 * 1024 * 1024,     # 100MB
    'document': 5 * 1024 * 1024,    # 5MB
    'audio': 20 * 1024 * 1024       # 20MB
}
```

### Blocked Extensions
```python
blocked_extensions = {
    '.exe', '.bat', '.cmd', '.com', '.scr', '.vbs', '.js',
    '.jar', '.app', '.deb', '.rpm', '.dmg', '.pkg', '.run'
}
```

## Error Handling

Common validation errors:
1. **Invalid MIME type**: File content doesn't match expected type
2. **File too large**: Exceeds size limit for file type
3. **Blocked extension**: Security risk file types
4. **Malware detected**: File contains suspicious signatures

## Testing

```python
# Test with mock file
from werkzeug.datastructures import FileStorage
import io

# Create mock image file
mock_file = FileStorage(
    stream=io.BytesIO(b'fake image data'),
    filename='test.jpg',
    content_type='image/jpeg'
)

result = validator.validate_file(mock_file, 'image')
assert not result['is_valid']  # Should fail - not real JPEG
```

## Troubleshooting

### "Failed to detect file type"
- Ensure libmagic is installed on your system
- Check that python-magic can find the magic database

### "ImportError: failed to find libmagic"
- Install system dependencies (see Installation section)
- On Windows, use python-magic-bin instead

### Performance Issues
- For large files, validation reads only first 2KB for type detection
- Consider async processing for batch uploads
- Implement caching for duplicate file detection using file hash