# API Validation Guide

This guide shows how to apply Marshmallow schema validation to all API endpoints that accept user input.

## Overview

All endpoints that accept user input (POST, PUT, PATCH) should use Marshmallow schemas for validation. This provides:
- Automatic input sanitization
- Type validation and conversion
- Consistent error messages
- Protection against malformed data
- Documentation of expected inputs

## Using the @validate_request Decorator

The `@validate_request` decorator in `utils/validators.py` makes it easy to apply schema validation:

```python
from utils.validators import validate_request
from schemas import YourSchema

@app.route('/endpoint', methods=['POST'])
@validate_request(YourSchema)
def your_endpoint(validated_data):
    # validated_data contains the clean, validated input
    return handle_request(validated_data)
```

## Endpoints Requiring Schema Updates

### 1. Auth Routes (`routes/auth.py`)

#### Forgot Password Endpoint
```python
from schemas import ForgotPasswordSchema

@auth_bp.route('/forgot-password', methods=['POST'])
@validate_request(ForgotPasswordSchema)
def forgot_password(validated_data):
    email = validated_data['email']  # Already validated and lowercase
    # ... rest of implementation
```

#### Reset Password Endpoint
```python
from schemas import ResetPasswordSchema

@auth_bp.route('/reset-password', methods=['POST'])
@validate_request(ResetPasswordSchema)
def reset_password(validated_data):
    token = validated_data['token']
    password = validated_data['password']
    # confirm_password already validated to match
    # ... rest of implementation
```

### 2. Client Routes (`routes/client.py`)

#### Update Post Endpoint
```python
from schemas import PostUpdateSchema

@client_bp.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
@validate_request(PostUpdateSchema)
def update_post(post_id, validated_data):
    # PostUpdateSchema already exists and validates all fields
    # ... rest of implementation
```

### 3. Content Routes (`routes/content.py`)

#### Validate Content Endpoint
```python
from schemas import ContentValidationSchema

@content_bp.route('/validate', methods=['POST'])
@jwt_required()
@validate_request(ContentValidationSchema)
def validate_content(validated_data):
    content = validated_data['content']
    content_type = validated_data['content_type']
    platform = validated_data['platform']
    scheduled_time = validated_data.get('scheduled_time')
    # ... rest of implementation
```

#### Enhance Content Endpoint
```python
from schemas import ContentEnhanceSchema

@content_bp.route('/enhance', methods=['POST'])
@jwt_required()
@validate_request(ContentEnhanceSchema)
def enhance_content(validated_data):
    content = validated_data['content']
    improvements = validated_data['improvements']  # Already de-duplicated
    platform = validated_data['platform']
    target_audience = validated_data['target_audience']
    # ... rest of implementation
```

## Schema Features

### 1. Automatic Type Conversion
```python
# Schema definition
scheduled_time = fields.DateTime(missing=None)

# Input: "2024-03-20T14:30:00"
# Output: datetime object
```

### 2. Default Values
```python
# Schema definition
platform = fields.Str(missing='instagram')

# If not provided, defaults to 'instagram'
```

### 3. Validation Rules
```python
# Length validation
content = fields.Str(validate=validate.Length(min=1, max=5000))

# Choice validation
platform = fields.Str(validate=validate.OneOf(['instagram', 'snapchat']))

# Custom validation
@validates('email')
def validate_email_format(self, value):
    # Custom logic here
```

### 4. Cross-Field Validation
```python
@validates_schema
def validate_passwords_match(self, data, **kwargs):
    if data.get('password') != data.get('confirm_password'):
        raise ValidationError('Passwords do not match')
```

## Enhanced Password Validation

The new password strength checker using zxcvbn is integrated into schemas:

```python
# In ResetPasswordSchema
@post_load
def enhance_password_validation(self, data, **kwargs):
    from utils.password_strength import validate_password_enhanced
    error = validate_password_enhanced(
        data['password'],
        username=data.get('username'),
        email=data.get('email')
    )
    if error:
        raise ValidationError(error, field_names=['password'])
```

## Error Response Format

When validation fails, the API returns a consistent error format:

```json
{
    "error": "Validation failed",
    "errors": {
        "email": ["Not a valid email address."],
        "password": ["Password must be at least 8 characters long"]
    }
}
```

## Best Practices

1. **Always validate user input** - Never trust client data
2. **Use appropriate field types** - Email for emails, DateTime for dates, etc.
3. **Set reasonable limits** - Max lengths prevent DoS attacks
4. **Provide clear error messages** - Help users fix their input
5. **Validate early** - Before any processing or database operations
6. **Sanitize for context** - Use bleach for HTML, different rules for usernames
7. **Document schemas** - Add docstrings explaining each field

## File Upload Validation

For file uploads, continue using the custom validator:

```python
from utils.validators import validate_file_upload

file = request.files.get('image')
validation_result = validate_file_upload(file)
if not validation_result['is_valid']:
    return jsonify({'error': validation_result['error']}), 400
```

## Testing Validation

Always test validation with:
1. Valid inputs
2. Missing required fields
3. Invalid field types
4. Values outside allowed ranges
5. Malicious inputs (XSS, SQL injection attempts)

## Migration Checklist

- [ ] Update auth.py forgot-password endpoint
- [ ] Update auth.py reset-password endpoint
- [ ] Update client.py PUT posts endpoint
- [ ] Update content.py validate endpoint
- [ ] Update content.py enhance endpoint
- [ ] Test all updated endpoints
- [ ] Update API documentation