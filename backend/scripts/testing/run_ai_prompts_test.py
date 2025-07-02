#!/usr/bin/env python3
"""
Minimal server to test AI Prompts functionality
"""
import os
import sys
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)

# Basic configuration
app.config['SECRET_KEY'] = 'test-secret-key'

# Import routes
from routes.test_admin import test_admin_bp
app.register_blueprint(test_admin_bp)

# Mock AI prompts API endpoints
@app.route('/api/admin/ai-prompts', methods=['GET'])
def get_ai_prompts():
    """Get all AI prompts"""
    prompts = [
        {
            'id': 1,
            'name': 'Instagram Caption Generator',
            'service': 'openai',
            'category': 'content',
            'user_prompt_template': 'Generate engaging Instagram captions for {business_type} in Kuwait. Consider local culture, trends, and include relevant hashtags...',
            'enable_kuwaiti_nlp': True,
            'dialect_processing': 'kuwaiti',
            'model': 'gpt-4',
            'temperature': 0.7,
            'max_tokens': 500,
            'updated_at': '2024-01-15T10:30:00Z'
        },
        {
            'id': 2,
            'name': 'Food Description Writer',
            'service': 'anthropic',
            'category': 'content',
            'user_prompt_template': 'Write appetizing descriptions for {dish_name} that appeal to Kuwaiti taste preferences. Mention ingredients, preparation method...',
            'enable_kuwaiti_nlp': True,
            'dialect_processing': 'auto',
            'model': 'claude-3-sonnet',
            'temperature': 0.8,
            'max_tokens': 300,
            'updated_at': '2024-01-10T14:20:00Z'
        },
        {
            'id': 3,
            'name': 'Competitor Analysis',
            'service': 'openai',
            'category': 'analysis',
            'user_prompt_template': 'Analyze competitor {competitor_name} social media strategy in Kuwait market. Focus on content themes, posting frequency...',
            'enable_kuwaiti_nlp': False,
            'dialect_processing': None,
            'model': 'gpt-4',
            'temperature': 0.5,
            'max_tokens': 1000,
            'updated_at': '2024-01-12T09:15:00Z'
        }
    ]
    
    return jsonify({
        'success': True,
        'prompts': prompts,
        'total': len(prompts)
    })

@app.route('/api/admin/ai-prompts', methods=['POST'])
def create_ai_prompt():
    """Create new AI prompt"""
    data = request.get_json()
    
    # Mock response
    new_prompt = {
        'id': 4,
        'success': True,
        'message': 'AI prompt created successfully',
        **data
    }
    
    return jsonify(new_prompt), 201

@app.route('/api/admin/ai-prompts/<int:prompt_id>', methods=['PUT'])
def update_ai_prompt(prompt_id):
    """Update AI prompt"""
    data = request.get_json()
    
    return jsonify({
        'success': True,
        'message': f'AI prompt {prompt_id} updated successfully',
        'prompt': {'id': prompt_id, **data}
    })

@app.route('/api/admin/ai-prompts/<int:prompt_id>', methods=['DELETE'])
def delete_ai_prompt(prompt_id):
    """Delete AI prompt"""
    return jsonify({
        'success': True,
        'message': f'AI prompt {prompt_id} deleted successfully'
    })

@app.route('/api/admin/ai-prompts/<int:prompt_id>/versions', methods=['GET'])
def get_prompt_versions(prompt_id):
    """Get version history"""
    versions = [
        {
            'id': 3,
            'version_number': 3,
            'created_at': '2024-01-15T10:30:00Z',
            'created_by': 'Admin',
            'change_note': 'Updated temperature and added Kuwaiti context'
        },
        {
            'id': 2,
            'version_number': 2,
            'created_at': '2024-01-10T14:20:00Z',
            'created_by': 'Admin',
            'change_note': 'Added hashtag suggestions'
        },
        {
            'id': 1,
            'version_number': 1,
            'created_at': '2024-01-05T08:00:00Z',
            'created_by': 'Admin',
            'change_note': 'Initial version'
        }
    ]
    
    return jsonify({
        'success': True,
        'versions': versions,
        'prompt_id': prompt_id
    })

@app.route('/api/admin/ai-prompt-templates', methods=['GET'])
def get_ai_prompt_templates():
    """Get prompt templates"""
    templates = [
        {
            'id': 1,
            'name': 'Kuwait Restaurant Post',
            'category': 'content',
            'description': 'Perfect for restaurant social media posts with Kuwaiti cultural context',
            'is_featured': True,
            'usage_count': 156
        },
        {
            'id': 2,
            'name': 'Retail Promotion Kuwait',
            'category': 'content',
            'description': 'Generate promotional content for retail businesses in Kuwait',
            'is_featured': True,
            'usage_count': 89
        },
        {
            'id': 3,
            'name': 'Engagement Analysis Kuwait',
            'category': 'analysis',
            'description': 'Analyze social media engagement for Kuwaiti audience',
            'is_featured': False,
            'usage_count': 67
        }
    ]
    
    return jsonify({
        'success': True,
        'templates': templates
    })

# Health check
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'AI Prompts Test Server'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting AI Prompts Test Server...")
    print("=" * 50)
    print("✅ AI Prompts UI: http://localhost:5001/admin-prompts")
    print("✅ API Endpoint: http://localhost:5001/api/admin/ai-prompts")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5001, debug=True)