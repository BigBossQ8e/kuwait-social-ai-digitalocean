"""
Competitor management routes for client portal
Handles competitor tracking and analysis
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime, timedelta
from sqlalchemy import and_, func
from models import db, Competitor, CompetitorAnalysis
from services.competitor_analysis_service import CompetitorAnalysisService
from utils.decorators import client_required
from schemas import CompetitorAddSchema, PaginationSchema
from utils.validators import validate_request

competitors_bp = Blueprint('competitors', __name__)

# Initialize competitor analysis service
competitor_service = CompetitorAnalysisService()


@competitors_bp.route('', methods=['GET'])
@jwt_required()
@client_required
@validate_request(PaginationSchema)
def get_competitors(validated_data):
    """Get list of tracked competitors"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    # Extract pagination
    page = validated_data.get('page', 1)
    per_page = validated_data.get('per_page', 20)
    
    # Get competitors with latest analysis using optimized query
    competitors = Competitor.query.filter_by(
        client_id=client_id,
        is_active=True
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    # Get all competitor IDs for batch analysis lookup
    competitor_ids = [c.id for c in competitors.items]
    
    # Get latest analysis for all competitors in a single query
    latest_analyses = {}
    if competitor_ids:
        # Subquery to get the latest analysis date for each competitor
        latest_dates_subq = db.session.query(
            CompetitorAnalysis.competitor_id,
            func.max(CompetitorAnalysis.analysis_date).label('latest_date')
        ).filter(
            CompetitorAnalysis.competitor_id.in_(competitor_ids)
        ).group_by(CompetitorAnalysis.competitor_id).subquery()
        
        # Join to get the full latest analysis records
        latest_analyses_query = db.session.query(CompetitorAnalysis).join(
            latest_dates_subq,
            and_(
                CompetitorAnalysis.competitor_id == latest_dates_subq.c.competitor_id,
                CompetitorAnalysis.analysis_date == latest_dates_subq.c.latest_date
            )
        ).all()
        
        # Create lookup dictionary
        latest_analyses = {analysis.competitor_id: analysis for analysis in latest_analyses_query}
    
    # Build response data
    competitor_data = []
    for competitor in competitors.items:
        data = competitor.to_dict()
        latest_analysis = latest_analyses.get(competitor.id)
        
        if latest_analysis:
            data['latest_analysis'] = {
                'date': latest_analysis.analysis_date.isoformat(),
                'followers': latest_analysis.followers_count,
                'engagement_rate': latest_analysis.engagement_rate,
                'posts_count': latest_analysis.posts_count
            }
        competitor_data.append(data)
    
    return jsonify({
        'competitors': competitor_data,
        'pagination': {
            'page': competitors.page,
            'per_page': competitors.per_page,
            'total': competitors.total,
            'pages': competitors.pages
        }
    }), 200


@competitors_bp.route('', methods=['POST'])
@jwt_required()
@client_required
@validate_request(CompetitorAddSchema)
def add_competitor(validated_data):
    """Add a new competitor to track"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    # Check if competitor already exists
    existing = Competitor.query.filter_by(
        client_id=client_id,
        username=validated_data['username'],
        platform=validated_data['platform']
    ).first()
    
    if existing:
        if not existing.is_active:
            # Reactivate if inactive
            existing.is_active = True
            db.session.commit()
            return jsonify({
                'message': 'Competitor reactivated',
                'competitor': existing.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Competitor already being tracked'}), 400
    
    # Create new competitor
    competitor = Competitor(
        client_id=client_id,
        name=validated_data['name'],
        username=validated_data['username'],
        platform=validated_data['platform'],
        notes=validated_data.get('notes'),
        is_active=True
    )
    
    db.session.add(competitor)
    db.session.commit()
    
    # Trigger initial analysis
    try:
        analysis = competitor_service.analyze_competitor(competitor.id)
        return jsonify({
            'competitor': competitor.to_dict(),
            'initial_analysis': {
                'followers': analysis.followers_count,
                'engagement_rate': analysis.engagement_rate,
                'posts_count': analysis.posts_count
            }
        }), 201
    except Exception as e:
        # Still return success even if analysis fails
        return jsonify({
            'competitor': competitor.to_dict(),
            'analysis_error': str(e)
        }), 201


@competitors_bp.route('/<int:competitor_id>', methods=['GET'])
@jwt_required()
@client_required
def get_competitor_details(competitor_id):
    """Get detailed competitor analysis"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    # Get competitor
    competitor = Competitor.query.filter_by(
        id=competitor_id,
        client_id=client_id
    ).first()
    
    if not competitor:
        return jsonify({'error': 'Competitor not found'}), 404
    
    # Get analysis history
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    analyses = CompetitorAnalysis.query.filter(
        and_(
            CompetitorAnalysis.competitor_id == competitor_id,
            CompetitorAnalysis.analysis_date >= start_date
        )
    ).order_by(CompetitorAnalysis.analysis_date.desc()).all()
    
    # Get latest analysis details
    latest = analyses[0] if analyses else None
    
    return jsonify({
        'competitor': competitor.to_dict(),
        'current_metrics': {
            'followers': latest.followers_count if latest else 0,
            'following': latest.following_count if latest else 0,
            'posts': latest.posts_count if latest else 0,
            'engagement_rate': latest.engagement_rate if latest else 0,
            'avg_likes': latest.avg_likes_per_post if latest else 0,
            'avg_comments': latest.avg_comments_per_post if latest else 0
        } if latest else None,
        'history': [
            {
                'date': a.analysis_date.isoformat(),
                'followers': a.followers_count,
                'engagement_rate': a.engagement_rate,
                'posts': a.posts_count
            } for a in analyses
        ],
        'insights': {
            'posting_frequency': latest.posting_frequency if latest else None,
            'best_posting_times': latest.best_posting_times if latest else [],
            'top_hashtags': latest.top_hashtags if latest else [],
            'content_themes': latest.content_themes if latest else []
        } if latest else None
    }), 200


@competitors_bp.route('/<int:competitor_id>', methods=['PUT'])
@jwt_required()
@client_required
def update_competitor(competitor_id):
    """Update competitor information"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    competitor = Competitor.query.filter_by(
        id=competitor_id,
        client_id=client_id
    ).first()
    
    if not competitor:
        return jsonify({'error': 'Competitor not found'}), 404
    
    data = request.get_json()
    
    # Update fields
    if 'name' in data:
        competitor.name = data['name']
    if 'notes' in data:
        competitor.notes = data['notes']
    if 'is_active' in data:
        competitor.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify(competitor.to_dict()), 200


@competitors_bp.route('/<int:competitor_id>', methods=['DELETE'])
@jwt_required()
@client_required
def remove_competitor(competitor_id):
    """Remove competitor from tracking"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    competitor = Competitor.query.filter_by(
        id=competitor_id,
        client_id=client_id
    ).first()
    
    if not competitor:
        return jsonify({'error': 'Competitor not found'}), 404
    
    # Soft delete - just deactivate
    competitor.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Competitor removed from tracking'}), 200


@competitors_bp.route('/<int:competitor_id>/analyze', methods=['POST'])
@jwt_required()
@client_required
def trigger_competitor_analysis(competitor_id):
    """Manually trigger competitor analysis"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    competitor = Competitor.query.filter_by(
        id=competitor_id,
        client_id=client_id
    ).first()
    
    if not competitor:
        return jsonify({'error': 'Competitor not found'}), 404
    
    try:
        # Run analysis
        analysis = competitor_service.analyze_competitor(competitor_id)
        
        return jsonify({
            'message': 'Analysis completed',
            'results': {
                'followers': analysis.followers_count,
                'engagement_rate': analysis.engagement_rate,
                'posts_analyzed': analysis.posts_count,
                'top_hashtags': analysis.top_hashtags[:10] if analysis.top_hashtags else []
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Analysis failed: {str(e)}'
        }), 500


@competitors_bp.route('/compare', methods=['POST'])
@jwt_required()
@client_required
def compare_competitors():
    """Compare multiple competitors"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    data = request.get_json()
    competitor_ids = data.get('competitor_ids', [])
    
    if len(competitor_ids) < 2 or len(competitor_ids) > 5:
        return jsonify({'error': 'Please select 2-5 competitors to compare'}), 400
    
    # Get competitors
    competitors = Competitor.query.filter(
        and_(
            Competitor.id.in_(competitor_ids),
            Competitor.client_id == client_id
        )
    ).all()
    
    if len(competitors) != len(competitor_ids):
        return jsonify({'error': 'Some competitors not found'}), 404
    
    # Get latest analysis for all competitors in a single optimized query
    competitor_ids = [c.id for c in competitors]
    
    # Subquery to get the latest analysis date for each competitor
    latest_dates_subq = db.session.query(
        CompetitorAnalysis.competitor_id,
        func.max(CompetitorAnalysis.analysis_date).label('latest_date')
    ).filter(
        CompetitorAnalysis.competitor_id.in_(competitor_ids)
    ).group_by(CompetitorAnalysis.competitor_id).subquery()
    
    # Join to get the full latest analysis records
    latest_analyses_query = db.session.query(CompetitorAnalysis).join(
        latest_dates_subq,
        and_(
            CompetitorAnalysis.competitor_id == latest_dates_subq.c.competitor_id,
            CompetitorAnalysis.analysis_date == latest_dates_subq.c.latest_date
        )
    ).all()
    
    # Create lookup dictionary for fast access
    latest_analyses = {analysis.competitor_id: analysis for analysis in latest_analyses_query}
    
    # Build comparison data
    comparison_data = []
    for competitor in competitors:
        latest = latest_analyses.get(competitor.id)
        
        if latest:
            comparison_data.append({
                'competitor': {
                    'id': competitor.id,
                    'name': competitor.name,
                    'username': competitor.username,
                    'platform': competitor.platform
                },
                'metrics': {
                    'followers': latest.followers_count,
                    'engagement_rate': latest.engagement_rate,
                    'avg_likes': latest.avg_likes_per_post,
                    'avg_comments': latest.avg_comments_per_post,
                    'posts_per_week': latest.posting_frequency.get('posts_per_week', 0) if latest.posting_frequency else 0
                },
                'analysis_date': latest.analysis_date.isoformat()
            })
    
    # Calculate averages
    if comparison_data:
        avg_followers = sum(c['metrics']['followers'] for c in comparison_data) / len(comparison_data)
        avg_engagement = sum(c['metrics']['engagement_rate'] for c in comparison_data) / len(comparison_data)
        
        averages = {
            'followers': avg_followers,
            'engagement_rate': avg_engagement
        }
    else:
        averages = None
    
    return jsonify({
        'comparison': comparison_data,
        'averages': averages
    }), 200