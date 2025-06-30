# Error Handling Guide

## Overview

Kuwait Social AI implements comprehensive error handling across both backend and frontend to provide a better user experience.

## Backend Error Handling

### Translation Library Update

**Previous Issue**: Using `googletrans==4.0.0-rc1` (release candidate)
**Solution**: Switched to `deep-translator==1.11.4` for better stability

```python
# Old
from googletrans import Translator
translator = Translator()
result = translator.translate(text, src='en', dest='ar')

# New
from deep_translator import GoogleTranslator
translator = GoogleTranslator(source='en', target='ar')
result = translator.translate(text)
```

### Benefits of deep-translator
1. **More Stable**: Production-ready, not a release candidate
2. **Better Error Handling**: Clearer error messages
3. **Multiple Providers**: Supports Google, Microsoft, Yandex, etc.
4. **Batch Translation**: Can translate multiple texts efficiently
5. **Language Detection**: Built-in language detection

## Frontend Error Handling

### API Client Implementation

Created a comprehensive API client (`api.js`) with:

1. **Automatic Error Parsing**
```javascript
async handleResponse(response) {
    if (!response.ok) {
        const errorData = await response.json();
        const error = new Error(errorData.error || 'Request failed');
        error.status = response.status;
        error.data = errorData;
        throw error;
    }
    return await response.json();
}
```

2. **User-Friendly Error Messages**
```javascript
handleError(error) {
    // Network errors
    if (error.message === 'Failed to fetch') {
        error.userMessage = 'Network error. Please check your internet connection.';
        return;
    }
    
    // Specific error codes
    switch (error.data.error_code) {
        case 'RATE_LIMIT_EXCEEDED':
            error.userMessage = 'Too many requests. Please wait a moment and try again.';
            break;
        case 'CONTENT_MODERATION_FAILED':
            error.userMessage = 'Content violates community guidelines. Please revise and try again.';
            break;
        // ... more cases
    }
}
```

3. **Automatic Token Refresh**
```javascript
if (response.status === 401) {
    const refreshed = await this.refreshToken();
    if (!refreshed) {
        this.handleAuthError();
        throw new Error('Session expired. Please log in again.');
    }
}
```

### Error Display Improvements

1. **Notification System**
   - Success, error, warning, and info notifications
   - Auto-dismiss after 5 seconds
   - User can manually close

2. **Input Validation Feedback**
   - Visual error states with shake animation
   - Field highlighting for validation errors
   - Inline error messages

3. **Partial Success Handling**
```javascript
// Check for partial failures
if (data.translation_error) {
    showNotification('Content generated but Arabic translation unavailable', 'warning');
}
if (data.hashtag_error) {
    showNotification('Using default hashtags due to generation error', 'warning');
}
```

## Error Types and User Messages

### Network Errors
- **Error**: Network failure
- **User Message**: "Network error. Please check your internet connection."
- **Action**: Show retry button

### Validation Errors (400)
- **Error**: Invalid input
- **User Message**: Specific validation message
- **Action**: Highlight invalid fields

### Authentication Errors (401)
- **Error**: Token expired
- **User Message**: "Session expired. Please log in again."
- **Action**: Show login modal

### Permission Errors (403)
- **Error**: Insufficient permissions
- **User Message**: "You don't have permission to perform this action."
- **Action**: Show upgrade prompt if applicable

### Rate Limit Errors (429)
- **Error**: Too many requests
- **User Message**: "Too many requests. Please wait a moment and try again."
- **Action**: Show countdown timer

### Server Errors (500+)
- **Error**: Internal server error
- **User Message**: "Service temporarily unavailable. Please try again later."
- **Action**: Show support contact

## Best Practices

### Backend
1. **Always return structured errors**
```python
return jsonify({
    'error': 'Human-readable message',
    'error_code': 'SPECIFIC_ERROR_CODE',
    'details': {
        'field': 'Additional context'
    }
}), status_code
```

2. **Log errors with context**
```python
logger.error(
    f"Translation failed for user {user_id}",
    extra={
        'user_id': user_id,
        'source_lang': 'en',
        'target_lang': 'ar',
        'text_length': len(text)
    }
)
```

3. **Graceful degradation**
```python
try:
    content['caption_ar'] = translate_to_arabic(text)
except TranslationException as e:
    content['caption_ar'] = None
    content['translation_error'] = e.to_dict()
    # Continue processing - don't fail entire request
```

### Frontend
1. **Always catch API errors**
```javascript
try {
    const data = await api.post('/endpoint', payload);
    // Handle success
} catch (error) {
    showNotification(error.userMessage || 'An error occurred', 'error');
}
```

2. **Provide feedback for all actions**
```javascript
// Show loader
showLoader('Processing...');

try {
    // Perform action
    showNotification('Success!', 'success');
} catch (error) {
    showNotification(error.userMessage, 'error');
} finally {
    hideLoader();
}
```

3. **Progressive enhancement**
```javascript
// Check for partial success
if (data.success) {
    // Show main result
    if (data.warnings) {
        // Show warnings separately
    }
}
```

## Testing Error Scenarios

### Backend Testing
```python
# Test translation fallback
def test_translation_fallback():
    with patch('deep_translator.GoogleTranslator.translate', side_effect=Exception):
        result = content_generator.generate_content('Test', include_arabic=True)
        assert result['caption_ar'] is None
        assert 'translation_error' in result
```

### Frontend Testing
```javascript
// Simulate network error
const mockFetch = jest.fn(() => Promise.reject(new Error('Failed to fetch')));
global.fetch = mockFetch;

// Test error display
await generateContent();
expect(showNotification).toHaveBeenCalledWith(
    'Network error. Please check your internet connection.',
    'error'
);
```

## Error Monitoring

### Logging Strategy
1. **Error Levels**
   - ERROR: System errors requiring attention
   - WARNING: Degraded functionality (e.g., translation unavailable)
   - INFO: Normal operations

2. **What to Log**
   - Error type and message
   - User context (ID, action)
   - Request details (endpoint, parameters)
   - Stack trace for unexpected errors

3. **What NOT to Log**
   - Passwords or sensitive data
   - Full request/response bodies
   - Personal information

### Metrics to Track
1. Error rate by type
2. Most common error codes
3. Error trends over time
4. Service availability (uptime)
5. API response times

## User Communication Guidelines

### Error Message Principles
1. **Be Clear**: Explain what went wrong in simple terms
2. **Be Helpful**: Suggest what the user can do
3. **Be Honest**: Don't hide issues or blame the user
4. **Be Brief**: Keep messages concise

### Examples
❌ Bad: "Error 500: Internal Server Error"
✅ Good: "Something went wrong on our end. Please try again."

❌ Bad: "Invalid input"
✅ Good: "Please enter a valid email address"

❌ Bad: "TRANSLATION_SERVICE_UNAVAILABLE"
✅ Good: "Arabic translation is temporarily unavailable. Your content has been saved in English."