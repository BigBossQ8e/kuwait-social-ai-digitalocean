# Updated UserRegistrationSchema to include requested_plan

from marshmallow import Schema, fields, validate, validates, ValidationError
from .schemas import validate_kuwait_phone, validate_password_strength

class UserRegistrationSchema(Schema):
    """Schema for user registration with plan selection"""
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(
        required=True,
        validate=[validate.Length(min=8, max=128), validate_password_strength],
        load_only=True
    )
    company_name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=200),
        error_messages={'required': 'Company name is required'}
    )
    contact_name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=200)
    )
    phone = fields.Str(
        required=True,
        validate=validate_kuwait_phone
    )
    address = fields.Str(
        missing='',
        validate=validate.Length(max=500)
    )
    requested_plan = fields.Str(
        missing='professional',
        validate=validate.OneOf(['basic', 'professional', 'premium']),
        error_messages={'validator_failed': 'Invalid plan selected'}
    )
    
    @validates('email')
    def validate_email_domain(self, value):
        """Additional email validation"""
        # Block disposable email domains
        disposable_domains = ['tempmail.com', 'throwaway.email', '10minutemail.com']
        domain = value.split('@')[1].lower()
        if domain in disposable_domains:
            raise ValidationError('Please use a permanent email address')
        return value