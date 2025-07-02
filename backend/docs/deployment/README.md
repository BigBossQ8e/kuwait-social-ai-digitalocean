# Kuwait Social AI - Backend

## System Requirements

### Python Dependencies
All Python dependencies are listed in `requirements.txt`. Key dependencies include:
- `python-magic==0.4.27` - For secure file type validation (requires libmagic)
- `openai>=1.0.0` - For AI content generation
- `Pillow==10.0.1` - For image processing

### System Dependencies
Before installing Python packages, ensure these system dependencies are installed:

#### macOS
```bash
brew install libmagic postgresql redis
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install libmagic1 postgresql redis-server
```

#### CentOS/RHEL
```bash
sudo yum install file-libs postgresql redis
```

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd kuwait-social-ai-hosting/application/backend

# Install system dependencies (see above)

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
flask db init
flask db migrate
flask db upgrade
```

## Error Handling Implementation

The backend now includes comprehensive error handling with meaningful error messages for users.

### Key Features

1. **Custom Exception Hierarchy**
   - Base `KuwaitSocialAIException` for all custom exceptions
   - Specific exceptions for different error scenarios
   - Each exception includes error codes and detailed information

2. **Translation Error Handling**
   - Graceful fallback when translation services fail
   - Returns partial results instead of failing completely
   - Logs attempted services for debugging

3. **Structured Error Responses**
   ```json
   {
     "error": "Failed to translate from en to ar",
     "error_code": "TRANSLATION_FAILED",
     "details": {
       "source_language": "en",
       "target_language": "ar",
       "attempted_services": ["Google Translate", "OpenAI GPT-4"],
       "original_text_length": 150
     }
   }
   ```

4. **Service-Specific Exceptions**
   - `TranslationException` - Translation failures
   - `AIServiceException` - AI service unavailability
   - `ImageProcessingException` - Image processing errors
   - `ContentModerationException` - Content violations
   - `KuwaitComplianceException` - Kuwait-specific compliance issues

### Error Handling Flow

1. **Service Layer**: Throws specific exceptions with context
2. **Route Layer**: Catches and logs exceptions
3. **Error Handlers**: Formats exceptions as JSON responses
4. **Client**: Receives structured error information

### Example Usage

```python
# In service
if not translation_result:
    raise TranslationException(
        source_lang='en',
        target_lang='ar',
        original_text=text,
        attempted_services=['Google Translate', 'OpenAI']
    )

# In route
try:
    content = content_generator.generate_content(...)
except TranslationException as e:
    # Log error
    logger.error(f"Translation failed: {e}")
    # Return user-friendly error
    return jsonify({
        'error': 'Arabic translation temporarily unavailable',
        'error_code': e.error_code,
        'content': content_without_arabic
    }), 206  # Partial content
```

### Benefits

1. **Better User Experience**
   - Users receive clear, actionable error messages
   - Partial results when possible (e.g., English content without Arabic)
   - Suggested alternatives or next steps

2. **Improved Debugging**
   - Detailed error logging with context
   - Service attempt tracking
   - Request IDs for support

3. **Graceful Degradation**
   - Services continue working even when some features fail
   - Fallback options for critical features
   - Non-blocking errors for optional features
   - Translation failures don't block content generation
   - Hashtag generation failures provide default hashtags

### Testing Error Scenarios

```bash
# Test translation failure
curl -X POST http://localhost:5000/api/content/generate \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test content", "include_arabic": true}'

# Response when translation fails:
{
  "success": true,
  "content": {
    "caption_en": "Generated content...",
    "caption_ar": null,
    "hashtags": ["#Kuwait", "#Q8", "#Business"],
    "translation_error": {
      "message": "Arabic translation unavailable",
      "details": {
        "error": "Failed to translate from en to ar",
        "error_code": "TRANSLATION_FAILED",
        "attempted_services": ["Google Translate", "OpenAI GPT-4"]
      }
    },
    "metadata": {
      "generated_at": "2024-01-15T10:30:00",
      "platform": "instagram",
      "ai_model": "gpt-4",
      "tone": "professional"
    }
  }
}

# Response when hashtag generation also fails:
{
  "success": true,
  "content": {
    "caption_en": "Generated content...",
    "caption_ar": null,
    "hashtags": ["#Kuwait", "#الكويت", "#Q8"],
    "translation_error": {
      "message": "Arabic translation unavailable",
      "details": {...}
    },
    "hashtag_error": {
      "message": "Using default hashtags",
      "reason": "API timeout"
    },
    "metadata": {...}
  }
}
```

## Platform Configuration

The application now uses a centralized configuration system to manage platform-specific settings, removing hardcoded values from the codebase.

### Configuration Management

1. **Configuration File**: Platform settings can be customized via a JSON file
   ```bash
   # Copy the example configuration
   cp config/platform_settings.json.example config/platform_settings.json
   
   # Edit the configuration as needed
   nano config/platform_settings.json
   ```

2. **Environment Variable**: Set the configuration file path
   ```bash
   export PLATFORM_CONFIG_FILE=/path/to/platform_settings.json
   ```

3. **Dynamic Updates**: Platform limits and settings can be updated without changing code
   - Instagram/Snapchat character limits
   - Hashtag counts
   - Image dimensions
   - Prayer times
   - Cultural guidelines

### Configuration Structure

The configuration includes:
- **Platform Limits**: Character counts, hashtag limits, media dimensions
- **Kuwait Settings**: Timezone, business hours, prayer times
- **Moderation Settings**: Inappropriate terms, cultural guidelines
- **Trending Hashtags**: Category-specific hashtags

### Usage in Code

```python
from config.platform_config import PlatformConfig

# Get platform limit
caption_limit = PlatformConfig.get_platform_limit('instagram', 'caption_max_length')

# Check prayer time
is_prayer, prayer_name = PlatformConfig.is_prayer_time()

# Get optimal posting times
posting_times = PlatformConfig.get_optimal_posting_time('weekend')
```