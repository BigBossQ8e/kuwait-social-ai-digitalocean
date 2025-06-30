# OpenAI API Migration Guide

## Overview

The OpenAI Python library has been updated to use a client-based approach. The old method of calling `openai.ChatCompletion.create()` is deprecated and has been replaced with a new client-based API.

## Changes Made

### 1. Import Statement
**Old:**
```python
import openai
```

**New:**
```python
from openai import OpenAI
```

### 2. Client Initialization
**Old:**
```python
openai.api_key = self.api_key
```

**New:**
```python
self.client = OpenAI(api_key=self.api_key)
```

### 3. API Calls
**Old:**
```python
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[...],
    max_tokens=500,
    temperature=0.7
)
```

**New:**
```python
response = self.client.chat.completions.create(
    model="gpt-4",
    messages=[...],
    max_tokens=500,
    temperature=0.7
)
```

### 4. Error Handling
**Old:**
```python
except openai.error.OpenAIError as e:
    # Handle OpenAI errors
```

**New:**
```python
except Exception as e:
    if hasattr(e, '__class__') and 'openai' in str(e.__class__):
        # Handle OpenAI errors
```

## Files Updated

1. **content_generator.py**
   - Updated all OpenAI API calls to use the new client approach
   - Modified error handling to work with the new exception structure
   - Changed Vision API calls to use the client

## Benefits

1. **Better Type Safety**: The new client provides better type hints and IDE support
2. **Cleaner API**: More intuitive method names and structure
3. **Future Compatibility**: Ensures compatibility with future OpenAI library updates
4. **Improved Error Handling**: More consistent error types and messages

## Testing

After updating, test the following endpoints:

```bash
# Test content generation
curl -X POST http://localhost:5000/api/content/generate \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test content generation"}'

# Test image caption generation
curl -X POST http://localhost:5000/api/content/generate-from-image \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/image.jpg"}'

# Test Arabic translation
curl -X POST http://localhost:5000/api/content/generate \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test content", "include_arabic": true}'
```

## Rollback Plan

If issues arise, you can temporarily pin the OpenAI library to an older version:

```bash
pip install openai==0.28.1
```

However, this is not recommended as the old API will eventually be deprecated.