from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import and_
from models import User, Translation, TranslationHistory
from extensions import db
import json
from datetime import datetime

translations_bp = Blueprint('translations', __name__)

@translations_bp.route('/translations', methods=['GET'])
def get_translations():
    """Get all translations for a specific locale or all locales"""
    locale = request.args.get('locale')
    category = request.args.get('category')
    
    query = Translation.query
    
    if locale:
        query = query.filter_by(locale=locale)
    if category:
        query = query.filter_by(category=category)
    
    translations = query.all()
    
    # Format response for easy consumption by frontend
    if locale:
        # Return as nested object for single locale
        result = {}
        for trans in translations:
            keys = trans.key.split('.')
            current = result
            for i, key in enumerate(keys[:-1]):
                if key not in current:
                    current[key] = {}
                current = current[key]
            current[keys[-1]] = trans.value
        return jsonify(result)
    else:
        # Return all translations grouped by locale
        result = {}
        for trans in translations:
            if trans.locale not in result:
                result[trans.locale] = {}
            
            keys = trans.key.split('.')
            current = result[trans.locale]
            for i, key in enumerate(keys[:-1]):
                if key not in current:
                    current[key] = {}
                current = current[key]
            current[keys[-1]] = trans.value
            
        return jsonify(result)


@translations_bp.route('/translations/list', methods=['GET'])
@jwt_required()
def list_translations():
    """Get translations in list format for admin panel"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get all translations
    translations = Translation.query.all()
    
    # Group by category
    categorized = {}
    for trans in translations:
        category = trans.category or 'uncategorized'
        if category not in categorized:
            categorized[category] = []
        
        categorized[category].append({
            'id': trans.id,
            'key': trans.key,
            'en': '',  # Will be filled below
            'ar': '',  # Will be filled below
            'category': category
        })
    
    # Fill in values for each locale
    for trans in translations:
        category = trans.category or 'uncategorized'
        for item in categorized[category]:
            if item['key'] == trans.key:
                item[trans.locale] = trans.value
    
    # Convert to list format expected by frontend
    result = []
    for category, items in categorized.items():
        # Remove duplicates (same key appearing multiple times)
        unique_items = {}
        for item in items:
            if item['key'] not in unique_items:
                unique_items[item['key']] = item
        
        result.append({
            'name': category,
            'translations': list(unique_items.values())
        })
    
    return jsonify(result)


@translations_bp.route('/translations', methods=['POST'])
@jwt_required()
def create_translation():
    """Create a new translation"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['key', 'locale', 'value']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if translation already exists
    existing = Translation.query.filter_by(
        key=data['key'],
        locale=data['locale']
    ).first()
    
    if existing:
        return jsonify({'error': 'Translation already exists'}), 409
    
    # Create new translation
    translation = Translation(
        key=data['key'],
        locale=data['locale'],
        value=data['value'],
        category=data.get('category'),
        created_by=current_user_id
    )
    
    db.session.add(translation)
    db.session.commit()
    
    return jsonify(translation.to_dict()), 201


@translations_bp.route('/translations/<int:translation_id>', methods=['PUT'])
@jwt_required()
def update_translation(translation_id):
    """Update an existing translation"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    translation = Translation.query.get(translation_id)
    if not translation:
        return jsonify({'error': 'Translation not found'}), 404
    
    data = request.get_json()
    old_value = translation.value
    new_value = data.get('value', translation.value)
    
    # Create history entry if value changed
    if old_value != new_value:
        history = TranslationHistory(
            translation_id=translation_id,
            old_value=old_value,
            new_value=new_value,
            changed_by=current_user_id
        )
        db.session.add(history)
    
    # Update translation
    translation.value = new_value
    if 'category' in data:
        translation.category = data['category']
    
    db.session.commit()
    
    return jsonify(translation.to_dict())


@translations_bp.route('/translations/bulk', methods=['PUT'])
@jwt_required()
def bulk_update_translations():
    """Update multiple translations at once"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    updates = data.get('updates', [])
    
    updated_count = 0
    errors = []
    
    for update in updates:
        try:
            # Find translation by key and locale
            translation = Translation.query.filter_by(
                key=update['key'],
                locale=update['locale']
            ).first()
            
            if not translation:
                # Create new translation if it doesn't exist
                translation = Translation(
                    key=update['key'],
                    locale=update['locale'],
                    value=update['value'],
                    category=update.get('category'),
                    created_by=current_user_id
                )
                db.session.add(translation)
            else:
                # Update existing translation
                old_value = translation.value
                if old_value != update['value']:
                    history = TranslationHistory(
                        translation_id=translation.id,
                        old_value=old_value,
                        new_value=update['value'],
                        changed_by=current_user_id
                    )
                    db.session.add(history)
                    translation.value = update['value']
            
            updated_count += 1
            
        except Exception as e:
            errors.append({
                'key': update.get('key'),
                'locale': update.get('locale'),
                'error': str(e)
            })
    
    db.session.commit()
    
    return jsonify({
        'updated': updated_count,
        'errors': errors
    })


@translations_bp.route('/translations/<int:translation_id>', methods=['DELETE'])
@jwt_required()
def delete_translation(translation_id):
    """Delete a translation"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    translation = Translation.query.get(translation_id)
    if not translation:
        return jsonify({'error': 'Translation not found'}), 404
    
    db.session.delete(translation)
    db.session.commit()
    
    return '', 204


@translations_bp.route('/translations/export', methods=['GET'])
@jwt_required()
def export_translations():
    """Export all translations as JSON"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    translations = Translation.query.all()
    
    # Group by locale
    result = {}
    for trans in translations:
        if trans.locale not in result:
            result[trans.locale] = {}
        
        keys = trans.key.split('.')
        current = result[trans.locale]
        for i, key in enumerate(keys[:-1]):
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = trans.value
    
    return jsonify(result)


@translations_bp.route('/translations/import', methods=['POST'])
@jwt_required()
def import_translations():
    """Import translations from JSON"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    imported_count = 0
    errors = []
    
    def process_nested(obj, prefix='', locale='en', category='imported'):
        nonlocal imported_count, errors
        
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                # Nested object
                process_nested(value, full_key, locale, key if not prefix else category)
            else:
                # Leaf value
                try:
                    # Check if translation exists
                    existing = Translation.query.filter_by(
                        key=full_key,
                        locale=locale
                    ).first()
                    
                    if existing:
                        # Update existing
                        if existing.value != str(value):
                            history = TranslationHistory(
                                translation_id=existing.id,
                                old_value=existing.value,
                                new_value=str(value),
                                changed_by=current_user_id
                            )
                            db.session.add(history)
                            existing.value = str(value)
                    else:
                        # Create new
                        translation = Translation(
                            key=full_key,
                            locale=locale,
                            value=str(value),
                            category=category,
                            created_by=current_user_id
                        )
                        db.session.add(translation)
                    
                    imported_count += 1
                    
                except Exception as e:
                    errors.append({
                        'key': full_key,
                        'locale': locale,
                        'error': str(e)
                    })
    
    # Process each locale
    for locale, translations in data.items():
        if isinstance(translations, dict):
            process_nested(translations, '', locale)
    
    db.session.commit()
    
    return jsonify({
        'imported': imported_count,
        'errors': errors
    })


@translations_bp.route('/translations/history/<int:translation_id>', methods=['GET'])
@jwt_required()
def get_translation_history(translation_id):
    """Get history for a specific translation"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    history = TranslationHistory.query.filter_by(
        translation_id=translation_id
    ).order_by(TranslationHistory.changed_at.desc()).all()
    
    return jsonify([h.to_dict() for h in history])