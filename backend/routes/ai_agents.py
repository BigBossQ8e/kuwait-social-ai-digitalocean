"""
AI Agent-powered routes for advanced content generation and analytics
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
import logging

from models import db, User, Client
from services import get_ai_service
from utils.decorators import client_required

logger = logging.getLogger(__name__)

ai_agents_bp = Blueprint('ai_agents', __name__, url_prefix='/api/ai/agents')

@ai_agents_bp.route('/campaign/create', methods=['POST'])
@jwt_required()
def create_campaign():
    """
    Create a complete campaign using AI agents
    
    Expected JSON payload:
    {
        "campaign_type": "ramadan" | "product_launch" | "seasonal",
        "restaurant_info": {
            "name": "Restaurant Name",
            "cuisine_type": "Lebanese",
            "area": "Salmiya"
        },
        "campaign_details": {
            "name": "Summer Special Campaign",
            "duration_days": 14,
            "budget": 500,
            "goals": ["Increase sales", "Build awareness"]
        },
        "special_requirements": ["Include delivery options", "Family focus"]
    }
    """
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role', 'client')
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        campaign_type = data.get('campaign_type')
        if not campaign_type:
            return jsonify({'error': 'Campaign type is required'}), 400
        
        # Get restaurant info
        restaurant_info = data.get('restaurant_info', {})
        if not restaurant_info.get('name'):
            # Try to get from user's business
            if user_role == 'client':
                client = Client.query.filter_by(user_id=current_user_id).first()
                if client and client.business:
                    restaurant_info = {
                        'name': client.business.name,
                        'cuisine_type': client.business.category or 'Restaurant',
                        'area': client.business.location or 'Kuwait'
                    }
        
        campaign_details = data.get('campaign_details', {})
        
        # Get AI service
        ai_service = get_ai_service()
        
        # Check if agents are available
        if not hasattr(ai_service, 'agents_enabled') or not ai_service.agents_enabled:
            return jsonify({
                'error': 'AI Agents are not available',
                'message': 'Please use standard content generation endpoints'
            }), 503
        
        # Generate campaign based on type
        if campaign_type == 'ramadan':
            result = ai_service.campaign_crew.create_ramadan_campaign(
                restaurant_info=restaurant_info,
                budget=campaign_details.get('budget'),
                duration_days=campaign_details.get('duration_days', 30)
            )
        elif campaign_type == 'product_launch':
            product_info = campaign_details.get('product', {
                'name': 'New Product',
                'type': 'dish'
            })
            result = ai_service.campaign_crew.create_new_launch_campaign(
                restaurant_info=restaurant_info,
                product_info=product_info,
                campaign_duration=campaign_details.get('duration_days', 14)
            )
        elif campaign_type == 'seasonal':
            result = ai_service.campaign_crew.create_seasonal_campaign(
                restaurant_info=restaurant_info,
                season=campaign_details.get('season', 'Summer'),
                special_dates=campaign_details.get('special_dates', [])
            )
        else:
            return jsonify({'error': 'Invalid campaign type'}), 400
        
        # Log campaign creation
        logger.info(f"Campaign created for user {current_user_id}, type: {campaign_type}")
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        return jsonify({'error': 'Failed to create campaign', 'message': str(e)}), 500


@ai_agents_bp.route('/content/weekly', methods=['POST'])
@jwt_required()
def create_weekly_content():
    """
    Create a week's worth of content using AI agents
    
    Expected JSON payload:
    {
        "restaurant_info": {
            "name": "Restaurant Name",
            "cuisine_type": "Italian",
            "area": "Kuwait City"
        },
        "week_theme": "Summer Specials",
        "special_requirements": ["Focus on lunch deals", "Include delivery"]
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get restaurant info
        restaurant_info = data.get('restaurant_info', {})
        week_theme = data.get('week_theme')
        
        # Get AI service
        ai_service = get_ai_service()
        
        # Check agents availability
        if not hasattr(ai_service, 'agents_enabled') or not ai_service.agents_enabled:
            return jsonify({
                'error': 'AI Agents are not available',
                'message': 'Please use standard content generation endpoints'
            }), 503
        
        # Generate weekly content
        result = ai_service.content_crew.create_weekly_content(
            restaurant_info=restaurant_info,
            week_theme=week_theme
        )
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error creating weekly content: {str(e)}")
        return jsonify({'error': 'Failed to create weekly content', 'message': str(e)}), 500


@ai_agents_bp.route('/analytics/campaign', methods=['POST'])
@jwt_required()
def analyze_campaign_performance():
    """
    Analyze campaign performance using AI agents
    
    Expected JSON payload:
    {
        "restaurant_info": {
            "name": "Restaurant Name"
        },
        "campaign_data": {
            "name": "Ramadan Campaign 2024",
            "duration": "30 days",
            "platform_data": {
                "instagram": {"posts": 30, "reach": 50000},
                "tiktok": {"posts": 15, "reach": 25000}
            }
        },
        "comparison_period": "Previous month"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        restaurant_info = data.get('restaurant_info', {})
        campaign_data = data.get('campaign_data', {})
        comparison_period = data.get('comparison_period')
        
        # Get AI service
        ai_service = get_ai_service()
        
        # Check agents availability
        if not hasattr(ai_service, 'agents_enabled') or not ai_service.agents_enabled:
            return jsonify({
                'error': 'AI Agents are not available',
                'message': 'Analytics features require agent framework'
            }), 503
        
        # Analyze campaign
        result = ai_service.analytics_crew.analyze_campaign_performance(
            restaurant_info=restaurant_info,
            campaign_data=campaign_data,
            comparison_period=comparison_period
        )
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error analyzing campaign: {str(e)}")
        return jsonify({'error': 'Failed to analyze campaign', 'message': str(e)}), 500


@ai_agents_bp.route('/analytics/competitors', methods=['POST'])
@jwt_required()
def analyze_competitors():
    """
    Analyze competitive landscape using AI agents
    
    Expected JSON payload:
    {
        "restaurant_info": {
            "name": "My Restaurant",
            "cuisine_type": "Burger"
        },
        "competitors": ["Burger Boutique", "Slider Station"],
        "time_period": 30
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        restaurant_info = data.get('restaurant_info', {})
        competitors = data.get('competitors', [])
        time_period = data.get('time_period', 30)
        
        if not competitors:
            return jsonify({'error': 'At least one competitor is required'}), 400
        
        # Get AI service
        ai_service = get_ai_service()
        
        # Use analyze_competitors method
        result = ai_service.analyze_competitors(
            restaurant_info=restaurant_info,
            competitors=competitors,
            time_period=time_period
        )
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error analyzing competitors: {str(e)}")
        return jsonify({'error': 'Failed to analyze competitors', 'message': str(e)}), 500


@ai_agents_bp.route('/analytics/monthly', methods=['GET'])
@jwt_required()
def get_monthly_insights():
    """
    Get comprehensive monthly performance insights
    
    Query parameters:
    - month: Month name (e.g., "January")
    - year: Year (e.g., 2024)
    """
    try:
        month = request.args.get('month')
        year = request.args.get('year', type=int)
        
        if not month:
            # Default to previous month
            from datetime import date
            today = date.today()
            month = today.strftime('%B')
            year = year or today.year
        
        # Get user's restaurant info
        current_user_id = get_jwt_identity()
        client = Client.query.filter_by(user_id=current_user_id).first()
        
        restaurant_info = {
            'name': 'Restaurant'
        }
        
        if client and client.business:
            restaurant_info = {
                'name': client.business.name,
                'cuisine_type': client.business.category or 'Restaurant'
            }
        
        # Get AI service
        ai_service = get_ai_service()
        
        # Get monthly insights
        result = ai_service.get_monthly_insights(
            restaurant_info=restaurant_info,
            month=month,
            year=year
        )
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting monthly insights: {str(e)}")
        return jsonify({'error': 'Failed to get monthly insights', 'message': str(e)}), 500


@ai_agents_bp.route('/status', methods=['GET'])
@jwt_required()
def get_agent_status():
    """
    Check if AI agents are available and working
    """
    try:
        # Get AI service
        ai_service = get_ai_service()
        
        # Check agent status
        agents_available = hasattr(ai_service, 'agents_enabled') and ai_service.agents_enabled
        
        if agents_available:
            # Get list of available crews
            available_crews = []
            if hasattr(ai_service, 'content_crew'):
                available_crews.append('content_creation')
            if hasattr(ai_service, 'campaign_crew'):
                available_crews.append('campaign_management')
            if hasattr(ai_service, 'analytics_crew'):
                available_crews.append('analytics_insights')
            
            return jsonify({
                'success': True,
                'data': {
                    'agents_enabled': True,
                    'available_crews': available_crews,
                    'capabilities': {
                        'content_creation': {
                            'single_post': True,
                            'weekly_content': True,
                            'campaign_content': True
                        },
                        'campaign_management': {
                            'ramadan_campaign': True,
                            'product_launch': True,
                            'seasonal_campaign': True
                        },
                        'analytics': {
                            'campaign_analysis': True,
                            'competitor_analysis': True,
                            'monthly_insights': True
                        }
                    },
                    'message': 'AI Agents are fully operational'
                }
            }), 200
        else:
            return jsonify({
                'success': True,
                'data': {
                    'agents_enabled': False,
                    'available_crews': [],
                    'capabilities': {},
                    'message': 'AI Agents are not available. Using standard AI generation.'
                }
            }), 200
            
    except Exception as e:
        logger.error(f"Error checking agent status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to check agent status',
            'message': str(e)
        }), 500


@ai_agents_bp.route('/capabilities', methods=['GET'])
def get_agent_capabilities():
    """
    Get detailed information about agent capabilities
    No authentication required - public endpoint
    """
    try:
        capabilities = {
            'content_creation': {
                'name': 'Content Creation Crew',
                'description': 'Multi-agent team for creating optimized social media content',
                'agents': [
                    {
                        'name': 'Market Researcher',
                        'role': 'Analyzes trends and competitor strategies'
                    },
                    {
                        'name': 'Content Creator',
                        'role': 'Generates engaging content for Kuwait market'
                    },
                    {
                        'name': 'Arabic Specialist',
                        'role': 'Translates and localizes content'
                    },
                    {
                        'name': 'Cultural Compliance',
                        'role': 'Ensures cultural appropriateness'
                    },
                    {
                        'name': 'Timing Expert',
                        'role': 'Optimizes posting schedules'
                    }
                ],
                'use_cases': [
                    'Single post creation with full optimization',
                    'Weekly content calendar generation',
                    'Campaign content creation'
                ]
            },
            'campaign_management': {
                'name': 'Campaign Management Crew',
                'description': 'Orchestrates comprehensive marketing campaigns',
                'campaign_types': [
                    {
                        'type': 'ramadan',
                        'description': '30-day Ramadan campaign with iftar/suhoor focus',
                        'duration': '30 days'
                    },
                    {
                        'type': 'product_launch',
                        'description': 'New product/menu item launch campaign',
                        'duration': '14 days'
                    },
                    {
                        'type': 'seasonal',
                        'description': 'Seasonal campaigns (Summer, Winter, National Day)',
                        'duration': 'Flexible'
                    }
                ]
            },
            'analytics_insights': {
                'name': 'Analytics Insights Crew',
                'description': 'Analyzes performance and generates actionable insights',
                'capabilities': [
                    'Campaign performance analysis',
                    'Competitive landscape analysis',
                    'Monthly performance reviews',
                    'ROI calculations',
                    'Trend identification'
                ]
            }
        }
        
        return jsonify({
            'success': True,
            'data': capabilities
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting capabilities: {str(e)}")
        return jsonify({'error': 'Failed to get capabilities', 'message': str(e)}), 500