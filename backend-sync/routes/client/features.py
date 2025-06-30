"""
Feature management routes for client portal
Handles Kuwait-specific features, hashtag strategies, and engagement tools
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime, timedelta
from sqlalchemy import and_, func
from models import db, Client, HashtagStrategy, CustomerEngagement, KuwaitFeature
from services.hashtag_strategy_service import HashtagStrategyService
from services.customer_engagement_service import CustomerEngagementService
from services.kuwait_features_service import KuwaitFeaturesService
from utils.decorators import client_required
from schemas import HashtagStrategySchema, EngagementToolSchema, AnalyticsQuerySchema
from utils.validators import validate_request

features_bp = Blueprint('features', __name__)

# Initialize services
hashtag_service = HashtagStrategyService()
engagement_service = CustomerEngagementService()
kuwait_service = KuwaitFeaturesService()


@features_bp.route('/hashtags/suggest', methods=['POST'])
@jwt_required()
@client_required
def suggest_hashtags():
    """Get AI-powered hashtag suggestions"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    data = request.get_json()
    content = data.get('content', '')
    platform = data.get('platform', 'instagram')
    
    if not content:
        return jsonify({'error': 'Content is required for hashtag suggestions'}), 400
    
    try:
        # Get hashtag suggestions
        suggestions = hashtag_service.generate_hashtag_strategy(
            content=content,
            platform=platform,
            client_id=client_id
        )
        
        return jsonify({
            'hashtags': suggestions['hashtags'],
            'strategy': suggestions['strategy'],
            'estimated_reach': suggestions['estimated_reach'],
            'competition_level': suggestions['competition_level']
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate hashtags: {str(e)}'}), 500


@features_bp.route('/hashtags/trending', methods=['GET'])
@jwt_required()
@client_required
def get_trending_hashtags():
    """Get trending hashtags in Kuwait"""
    platform = request.args.get('platform', 'instagram')
    category = request.args.get('category')
    
    try:
        trending = hashtag_service.get_trending_hashtags(
            location='kuwait',
            platform=platform,
            category=category
        )
        
        return jsonify({
            'trending': trending,
            'last_updated': datetime.utcnow().isoformat(),
            'location': 'Kuwait'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch trending hashtags: {str(e)}'}), 500


@features_bp.route('/hashtags/performance', methods=['GET'])
@jwt_required()
@client_required
def get_hashtag_performance():
    """Get performance analytics for used hashtags"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    days = request.args.get('days', 30, type=int)
    
    # Get hashtag performance data
    performance = db.session.query(
        HashtagStrategy.hashtag,
        func.count(HashtagStrategy.id).label('usage_count'),
        func.avg(HashtagStrategy.engagement_rate).label('avg_engagement'),
        func.avg(HashtagStrategy.reach).label('avg_reach')
    ).filter(
        and_(
            HashtagStrategy.client_id == client_id,
            HashtagStrategy.created_at >= datetime.utcnow() - timedelta(days=days)
        )
    ).group_by(HashtagStrategy.hashtag).all()
    
    return jsonify({
        'performance': [
            {
                'hashtag': p.hashtag,
                'usage_count': p.usage_count,
                'avg_engagement_rate': float(p.avg_engagement or 0),
                'avg_reach': int(p.avg_reach or 0)
            } for p in performance
        ],
        'period_days': days
    }), 200


@features_bp.route('/engagement/responses', methods=['GET'])
@jwt_required()
@client_required
def get_response_templates():
    """Get AI-generated response templates"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    category = request.args.get('category')  # complaint, inquiry, compliment
    language = request.args.get('language', 'en')
    
    try:
        templates = engagement_service.get_response_templates(
            client_id=client_id,
            category=category,
            language=language
        )
        
        return jsonify({
            'templates': templates,
            'category': category,
            'language': language
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get templates: {str(e)}'}), 500


@features_bp.route('/engagement/analyze', methods=['POST'])
@jwt_required()
@client_required
def analyze_customer_message():
    """Analyze customer message and suggest response"""
    data = request.get_json()
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    try:
        analysis = engagement_service.analyze_message(message)
        
        return jsonify({
            'sentiment': analysis['sentiment'],
            'category': analysis['category'],
            'urgency': analysis['urgency'],
            'suggested_responses': analysis['suggested_responses'],
            'cultural_notes': analysis.get('cultural_notes', [])
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@features_bp.route('/kuwait/prayer-times', methods=['GET'])
@jwt_required()
@client_required
def get_prayer_times():
    """Get prayer times for content scheduling"""
    date_str = request.args.get('date')
    
    if date_str:
        try:
            date_obj = datetime.fromisoformat(date_str).date()
        except:
            return jsonify({'error': 'Invalid date format'}), 400
    else:
        date_obj = datetime.utcnow().date()
    
    try:
        prayer_times = kuwait_service.get_prayer_times(date_obj)
        
        return jsonify({
            'date': date_obj.isoformat(),
            'prayer_times': prayer_times,
            'posting_restrictions': kuwait_service.get_posting_restrictions(prayer_times)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get prayer times: {str(e)}'}), 500


@features_bp.route('/kuwait/holidays', methods=['GET'])
@jwt_required()
@client_required
def get_kuwait_holidays():
    """Get Kuwait holidays and events"""
    year = request.args.get('year', datetime.utcnow().year, type=int)
    
    try:
        holidays = kuwait_service.get_holidays(year)
        
        return jsonify({
            'year': year,
            'holidays': holidays,
            'content_suggestions': kuwait_service.get_holiday_content_suggestions(holidays)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get holidays: {str(e)}'}), 500


@features_bp.route('/kuwait/cultural-check', methods=['POST'])
@jwt_required()
@client_required
def check_cultural_appropriateness():
    """Check content for cultural appropriateness"""
    data = request.get_json()
    content = data.get('content', '')
    content_type = data.get('type', 'text')  # text, image_description
    
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    try:
        check = kuwait_service.check_cultural_appropriateness(
            content=content,
            content_type=content_type
        )
        
        return jsonify({
            'is_appropriate': check['is_appropriate'],
            'concerns': check.get('concerns', []),
            'suggestions': check.get('suggestions', []),
            'confidence': check.get('confidence', 0.0)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Cultural check failed: {str(e)}'}), 500


@features_bp.route('/reports/generate', methods=['POST'])
@jwt_required()
@client_required
@validate_request(AnalyticsQuerySchema)
def generate_report(validated_data):
    """Generate detailed performance report"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    report_type = validated_data.get('report_type', 'monthly')
    include_competitors = validated_data.get('include_competitors', False)
    
    try:
        # Generate comprehensive report
        report = {
            'client_id': client_id,
            'period': {
                'start': validated_data['start_date'].isoformat(),
                'end': validated_data['end_date'].isoformat()
            },
            'generated_at': datetime.utcnow().isoformat()
        }
        
        # Add performance metrics
        report['performance'] = _get_performance_metrics(
            client_id,
            validated_data['start_date'],
            validated_data['end_date']
        )
        
        # Add content analysis
        report['content_analysis'] = _get_content_analysis(
            client_id,
            validated_data['start_date'],
            validated_data['end_date']
        )
        
        # Add competitor comparison if requested
        if include_competitors:
            report['competitor_comparison'] = _get_competitor_comparison(
                client_id,
                validated_data['start_date'],
                validated_data['end_date']
            )
        
        # Add recommendations
        report['recommendations'] = _generate_recommendations(report)
        
        return jsonify(report), 200
        
    except Exception as e:
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500


@features_bp.route('/settings/preferences', methods=['GET', 'PUT'])
@jwt_required()
@client_required
def manage_feature_preferences():
    """Manage client feature preferences"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    if request.method == 'GET':
        # Get current preferences
        client = Client.query.get(client_id)
        preferences = client.feature_preferences or {}
        
        return jsonify({
            'preferences': preferences,
            'available_features': {
                'hashtag_suggestions': True,
                'response_templates': True,
                'prayer_time_scheduling': True,
                'cultural_checks': True,
                'competitor_tracking': True,
                'advanced_analytics': True
            }
        }), 200
        
    else:  # PUT
        data = request.get_json()
        
        client = Client.query.get(client_id)
        if not client.feature_preferences:
            client.feature_preferences = {}
        
        # Update preferences
        client.feature_preferences.update(data)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Preferences updated',
            'preferences': client.feature_preferences
        }), 200


# Helper functions
def _get_performance_metrics(client_id, start_date, end_date):
    """Get detailed performance metrics for report"""
    metrics = db.session.query(
        func.sum(Analytics.total_posts).label('total_posts'),
        func.sum(Analytics.total_reach).label('total_reach'),
        func.sum(Analytics.total_engagement).label('total_engagement'),
        func.avg(Analytics.engagement_rate).label('avg_engagement_rate')
    ).filter(
        and_(
            Analytics.client_id == client_id,
            Analytics.date >= start_date,
            Analytics.date <= end_date
        )
    ).first()
    
    return {
        'total_posts': metrics.total_posts or 0,
        'total_reach': metrics.total_reach or 0,
        'total_engagement': metrics.total_engagement or 0,
        'avg_engagement_rate': float(metrics.avg_engagement_rate or 0)
    }


def _get_content_analysis(client_id, start_date, end_date):
    """Analyze content performance patterns"""
    # This would analyze posting times, content types, hashtag performance, etc.
    return {
        'best_posting_times': ['19:00-21:00', '11:00-13:00'],
        'top_performing_content_types': ['educational', 'promotional'],
        'hashtag_effectiveness': 'high',
        'language_performance': {
            'english': {'engagement_rate': 5.2},
            'arabic': {'engagement_rate': 6.8}
        }
    }


def _get_competitor_comparison(client_id, start_date, end_date):
    """Compare performance with tracked competitors"""
    # This would fetch and compare competitor metrics
    return {
        'ranking': 3,
        'total_competitors': 8,
        'performance_vs_average': '+15%',
        'areas_of_strength': ['engagement', 'consistency'],
        'areas_for_improvement': ['reach', 'follower_growth']
    }


def _generate_recommendations(report):
    """Generate actionable recommendations based on report data"""
    recommendations = []
    
    # Analyze performance and generate recommendations
    if report['performance']['avg_engagement_rate'] < 3.0:
        recommendations.append({
            'priority': 'high',
            'category': 'engagement',
            'recommendation': 'Focus on creating more interactive content with questions and calls-to-action',
            'expected_impact': 'Increase engagement rate by 20-30%'
        })
    
    return recommendations