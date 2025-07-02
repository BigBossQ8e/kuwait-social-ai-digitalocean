"""
AI Prompt Management Models
"""
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from extensions import db


class AIPrompt(db.Model):
    """Store AI prompts for different services and use cases"""
    __tablename__ = 'ai_prompts'
    
    id = db.Column(db.Integer, primary_key=True)
    prompt_key = db.Column(db.String(100), unique=True, nullable=False)  # e.g., 'instagram_caption', 'content_ideas'
    service = db.Column(db.String(50), nullable=False)  # 'openai', 'anthropic', 'gemini'
    category = db.Column(db.String(50), nullable=False)  # 'content', 'analysis', 'translation'
    
    # Prompt content
    system_prompt = db.Column(db.Text)
    user_prompt_template = db.Column(db.Text, nullable=False)
    
    # Configuration
    model = db.Column(db.String(50))  # 'gpt-4', 'claude-3', etc.
    temperature = db.Column(db.Float, default=0.7)
    max_tokens = db.Column(db.Integer, default=500)
    parameters = db.Column(JSON)  # Additional parameters
    
    # Kuwaiti NLP Configuration
    enable_kuwaiti_nlp = db.Column(db.Boolean, default=True)
    dialect_processing = db.Column(db.String(50), default='auto')  # 'auto', 'kuwaiti', 'gulf', 'msa'
    kuwaiti_context = db.Column(JSON)  # Custom Kuwaiti terms, phrases, cultural context
    
    # Metadata
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    tags = db.Column(JSON)  # ['instagram', 'arabic', 'food']
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)
    
    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('admins.id'))
    
    # Relationships
    created_by = db.relationship('Admin', backref='created_prompts')
    versions = db.relationship('AIPromptVersion', backref='prompt', lazy='dynamic', 
                             cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'prompt_key': self.prompt_key,
            'service': self.service,
            'category': self.category,
            'name': self.name,
            'description': self.description,
            'system_prompt': self.system_prompt,
            'user_prompt_template': self.user_prompt_template,
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'parameters': self.parameters,
            'tags': self.tags,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AIPromptVersion(db.Model):
    """Version history for AI prompts"""
    __tablename__ = 'ai_prompt_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    prompt_id = db.Column(db.Integer, db.ForeignKey('ai_prompts.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    
    # Snapshot of prompt at this version
    system_prompt = db.Column(db.Text)
    user_prompt_template = db.Column(db.Text)
    model = db.Column(db.String(50))
    temperature = db.Column(db.Float)
    max_tokens = db.Column(db.Integer)
    parameters = db.Column(JSON)
    
    # Version metadata
    change_note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('admins.id'))
    
    # Relationships
    created_by = db.relationship('Admin', backref='prompt_versions')


class AIPromptTemplate(db.Model):
    """Pre-built prompt templates"""
    __tablename__ = 'ai_prompt_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    
    # Template content
    system_prompt = db.Column(db.Text)
    user_prompt_template = db.Column(db.Text, nullable=False)
    
    # Suggested configuration
    suggested_model = db.Column(db.String(50))
    suggested_temperature = db.Column(db.Float, default=0.7)
    suggested_max_tokens = db.Column(db.Integer, default=500)
    
    # Example usage
    example_input = db.Column(db.Text)
    example_output = db.Column(db.Text)
    
    # Metadata
    tags = db.Column(JSON)
    is_featured = db.Column(db.Boolean, default=False)
    usage_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'system_prompt': self.system_prompt,
            'user_prompt_template': self.user_prompt_template,
            'suggested_model': self.suggested_model,
            'suggested_temperature': self.suggested_temperature,
            'suggested_max_tokens': self.suggested_max_tokens,
            'example_input': self.example_input,
            'example_output': self.example_output,
            'tags': self.tags,
            'is_featured': self.is_featured,
            'usage_count': self.usage_count
        }