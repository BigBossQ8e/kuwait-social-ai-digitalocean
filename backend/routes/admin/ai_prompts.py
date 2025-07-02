"""
AI Prompt Management Admin Routes
"""
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.ai_prompts import AIPrompt, AIPromptVersion, AIPromptTemplate
from utils.decorators import admin_required, audit_log
from services.kuwaiti_nlp_service import KuwaitiNLPService
import json

ai_prompts_bp = Blueprint('admin_ai_prompts', __name__)

# Default Kuwaiti NLP patterns
DEFAULT_KUWAITI_CONTEXT = {
    "greetings": {
        "هلا": "Welcome/Hello",
        "حياك": "Welcome (formal)",
        "شلونك": "How are you",
        "شخبارك": "How are you doing"
    },
    "food_terms": {
        "مجبوس": "Traditional rice dish",
        "هريس": "Wheat and meat porridge",
        "مطبق": "Stuffed pastry",
        "كرك": "Karak tea",
        "درابيل": "Traditional sweet"
    },
    "expressions": {
        "وايد": "Very/Much",
        "زين": "Good",
        "چذي": "Like this",
        "شنو": "What",
        "ليش": "Why"
    },
    "places": {
        "الأفنيوز": "The Avenues Mall",
        "السالمية": "Salmiya",
        "حولي": "Hawalli",
        "الجهراء": "Jahra"
    }
}

@ai_prompts_bp.route('/api/admin/ai-prompts', methods=['GET'])
@jwt_required()
@admin_required
def get_prompts():
    """Get all AI prompts"""
    try:
        category = request.args.get('category')
        service = request.args.get('service')
        is_active = request.args.get('is_active', type=bool)
        
        query = AIPrompt.query
        
        if category:
            query = query.filter_by(category=category)
        if service:
            query = query.filter_by(service=service)
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        prompts = query.order_by(AIPrompt.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'prompts': [prompt.to_dict() for prompt in prompts],
            'total': len(prompts)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_prompts_bp.route('/api/admin/ai-prompts/<int:prompt_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_prompt(prompt_id):
    """Get a specific AI prompt with version history"""
    try:
        prompt = AIPrompt.query.get_or_404(prompt_id)
        versions = AIPromptVersion.query.filter_by(prompt_id=prompt_id)\
            .order_by(AIPromptVersion.version_number.desc())\
            .limit(10).all()
        
        return jsonify({
            'success': True,
            'prompt': prompt.to_dict(),
            'versions': [
                {
                    'id': v.id,
                    'version_number': v.version_number,
                    'change_note': v.change_note,
                    'created_at': v.created_at.isoformat(),
                    'created_by': v.created_by.full_name if v.created_by else None
                } for v in versions
            ]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_prompts_bp.route('/api/admin/ai-prompts', methods=['POST'])
@jwt_required()
@admin_required
@audit_log('ai_prompt_create')
def create_prompt():
    """Create a new AI prompt"""
    try:
        data = request.get_json()
        admin_id = get_jwt_identity()
        
        # Validate required fields
        required = ['prompt_key', 'service', 'category', 'name', 'user_prompt_template']
        for field in required:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Check if prompt_key already exists
        existing = AIPrompt.query.filter_by(prompt_key=data['prompt_key']).first()
        if existing:
            return jsonify({
                'success': False,
                'error': 'Prompt key already exists'
            }), 400
        
        # Set default Kuwaiti context if not provided
        if data.get('enable_kuwaiti_nlp', True) and not data.get('kuwaiti_context'):
            data['kuwaiti_context'] = DEFAULT_KUWAITI_CONTEXT
        
        # Create prompt
        prompt = AIPrompt(
            prompt_key=data['prompt_key'],
            service=data['service'],
            category=data['category'],
            name=data['name'],
            description=data.get('description'),
            system_prompt=data.get('system_prompt'),
            user_prompt_template=data['user_prompt_template'],
            model=data.get('model'),
            temperature=data.get('temperature', 0.7),
            max_tokens=data.get('max_tokens', 500),
            parameters=data.get('parameters', {}),
            enable_kuwaiti_nlp=data.get('enable_kuwaiti_nlp', True),
            dialect_processing=data.get('dialect_processing', 'auto'),
            kuwaiti_context=data.get('kuwaiti_context', DEFAULT_KUWAITI_CONTEXT),
            tags=data.get('tags', []),
            is_active=data.get('is_active', True),
            is_default=data.get('is_default', False),
            created_by_id=admin_id
        )
        
        db.session.add(prompt)
        
        # Create initial version
        version = AIPromptVersion(
            prompt=prompt,
            version_number=1,
            system_prompt=prompt.system_prompt,
            user_prompt_template=prompt.user_prompt_template,
            model=prompt.model,
            temperature=prompt.temperature,
            max_tokens=prompt.max_tokens,
            parameters=prompt.parameters,
            change_note='Initial version',
            created_by_id=admin_id
        )
        
        db.session.add(version)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'prompt': prompt.to_dict(),
            'message': 'AI prompt created successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_prompts_bp.route('/api/admin/ai-prompts/<int:prompt_id>', methods=['PUT'])
@jwt_required()
@admin_required
@audit_log('ai_prompt_update')
def update_prompt(prompt_id):
    """Update an AI prompt"""
    try:
        data = request.get_json()
        admin_id = get_jwt_identity()
        
        prompt = AIPrompt.query.get_or_404(prompt_id)
        
        # Track what changed for version history
        changes = []
        
        # Update fields
        for field in ['name', 'description', 'service', 'category', 'model', 
                     'temperature', 'max_tokens', 'parameters', 'tags', 
                     'is_active', 'is_default', 'enable_kuwaiti_nlp', 
                     'dialect_processing', 'kuwaiti_context']:
            if field in data and getattr(prompt, field) != data[field]:
                changes.append(field)
                setattr(prompt, field, data[field])
        
        # Update prompts if changed
        prompt_changed = False
        if 'system_prompt' in data and prompt.system_prompt != data['system_prompt']:
            prompt.system_prompt = data['system_prompt']
            prompt_changed = True
            changes.append('system_prompt')
        
        if 'user_prompt_template' in data and prompt.user_prompt_template != data['user_prompt_template']:
            prompt.user_prompt_template = data['user_prompt_template']
            prompt_changed = True
            changes.append('user_prompt_template')
        
        # Create new version if prompts changed
        if prompt_changed or changes:
            # Get latest version number
            latest_version = AIPromptVersion.query.filter_by(prompt_id=prompt_id)\
                .order_by(AIPromptVersion.version_number.desc()).first()
            
            new_version_number = (latest_version.version_number + 1) if latest_version else 1
            
            version = AIPromptVersion(
                prompt_id=prompt_id,
                version_number=new_version_number,
                system_prompt=prompt.system_prompt,
                user_prompt_template=prompt.user_prompt_template,
                model=prompt.model,
                temperature=prompt.temperature,
                max_tokens=prompt.max_tokens,
                parameters=prompt.parameters,
                change_note=data.get('change_note', f'Updated: {", ".join(changes)}'),
                created_by_id=admin_id
            )
            
            db.session.add(version)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'prompt': prompt.to_dict(),
            'message': 'AI prompt updated successfully',
            'changes': changes
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_prompts_bp.route('/api/admin/ai-prompts/<int:prompt_id>/test', methods=['POST'])
@jwt_required()
@admin_required
def test_prompt(prompt_id):
    """Test an AI prompt with sample input"""
    try:
        data = request.get_json()
        test_input = data.get('test_input', '')
        
        prompt = AIPrompt.query.get_or_404(prompt_id)
        
        # Apply Kuwaiti NLP if enabled
        if prompt.enable_kuwaiti_nlp and test_input:
            nlp_service = KuwaitiNLPService()
            processed_input = nlp_service.process_text(
                test_input,
                dialect=prompt.dialect_processing,
                custom_context=prompt.kuwaiti_context
            )
        else:
            processed_input = test_input
        
        # Format the prompt with test input
        formatted_prompt = prompt.user_prompt_template.format(
            input=processed_input,
            original_input=test_input
        )
        
        # Here you would normally call the AI service
        # For now, return the formatted prompt
        
        return jsonify({
            'success': True,
            'test_result': {
                'original_input': test_input,
                'processed_input': processed_input,
                'formatted_prompt': formatted_prompt,
                'system_prompt': prompt.system_prompt,
                'model': prompt.model,
                'temperature': prompt.temperature,
                'kuwaiti_nlp_applied': prompt.enable_kuwaiti_nlp
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_prompts_bp.route('/api/admin/ai-prompts/<int:prompt_id>/rollback/<int:version_id>', methods=['POST'])
@jwt_required()
@admin_required
@audit_log('ai_prompt_rollback')
def rollback_prompt(prompt_id, version_id):
    """Rollback a prompt to a previous version"""
    try:
        admin_id = get_jwt_identity()
        
        prompt = AIPrompt.query.get_or_404(prompt_id)
        version = AIPromptVersion.query.filter_by(
            id=version_id, 
            prompt_id=prompt_id
        ).first_or_404()
        
        # Create new version with rollback data
        latest_version = AIPromptVersion.query.filter_by(prompt_id=prompt_id)\
            .order_by(AIPromptVersion.version_number.desc()).first()
        
        new_version_number = (latest_version.version_number + 1) if latest_version else 1
        
        # Update prompt with version data
        prompt.system_prompt = version.system_prompt
        prompt.user_prompt_template = version.user_prompt_template
        prompt.model = version.model
        prompt.temperature = version.temperature
        prompt.max_tokens = version.max_tokens
        prompt.parameters = version.parameters
        
        # Create rollback version record
        rollback_version = AIPromptVersion(
            prompt_id=prompt_id,
            version_number=new_version_number,
            system_prompt=version.system_prompt,
            user_prompt_template=version.user_prompt_template,
            model=version.model,
            temperature=version.temperature,
            max_tokens=version.max_tokens,
            parameters=version.parameters,
            change_note=f'Rolled back to version {version.version_number}',
            created_by_id=admin_id
        )
        
        db.session.add(rollback_version)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'prompt': prompt.to_dict(),
            'message': f'Successfully rolled back to version {version.version_number}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_prompts_bp.route('/api/admin/ai-prompts/templates', methods=['GET'])
@jwt_required()
@admin_required
def get_templates():
    """Get AI prompt templates"""
    try:
        category = request.args.get('category')
        featured_only = request.args.get('featured_only', type=bool)
        
        query = AIPromptTemplate.query
        
        if category:
            query = query.filter_by(category=category)
        if featured_only:
            query = query.filter_by(is_featured=True)
        
        templates = query.order_by(
            AIPromptTemplate.is_featured.desc(),
            AIPromptTemplate.usage_count.desc()
        ).all()
        
        return jsonify({
            'success': True,
            'templates': [template.to_dict() for template in templates],
            'total': len(templates)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_prompts_bp.route('/api/admin/ai-prompts/templates/<int:template_id>/use', methods=['POST'])
@jwt_required()
@admin_required
def use_template(template_id):
    """Create a prompt from a template"""
    try:
        data = request.get_json()
        admin_id = get_jwt_identity()
        
        template = AIPromptTemplate.query.get_or_404(template_id)
        
        # Increment usage count
        template.usage_count += 1
        
        # Create new prompt from template
        prompt = AIPrompt(
            prompt_key=data['prompt_key'],
            service=data.get('service', 'openai'),
            category=template.category,
            name=data.get('name', template.name),
            description=template.description,
            system_prompt=template.system_prompt,
            user_prompt_template=template.user_prompt_template,
            model=template.suggested_model,
            temperature=template.suggested_temperature,
            max_tokens=template.suggested_max_tokens,
            parameters={},
            enable_kuwaiti_nlp=True,
            dialect_processing='auto',
            kuwaiti_context=DEFAULT_KUWAITI_CONTEXT,
            tags=template.tags or [],
            is_active=True,
            created_by_id=admin_id
        )
        
        db.session.add(prompt)
        
        # Create initial version
        version = AIPromptVersion(
            prompt=prompt,
            version_number=1,
            system_prompt=prompt.system_prompt,
            user_prompt_template=prompt.user_prompt_template,
            model=prompt.model,
            temperature=prompt.temperature,
            max_tokens=prompt.max_tokens,
            parameters=prompt.parameters,
            change_note=f'Created from template: {template.name}',
            created_by_id=admin_id
        )
        
        db.session.add(version)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'prompt': prompt.to_dict(),
            'message': 'Prompt created from template successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500