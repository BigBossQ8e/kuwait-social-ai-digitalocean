"""
Competitor analysis routes for Kuwait Social AI F&B
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime, timedelta
from extensions import db
from models import Competitor
from models.competitor_analysis_models import (
    CompetitorContent, CompetitorSentiment, CompetitorAd,
    CompetitorStrategy, ContentComparison
)
from utils.decorators import client_required
from services.competitor_analysis_service import competitor_analysis_service

competitor_bp = Blueprint('competitor', __name__)

@competitor_bp.route('/analyze', methods=['POST'])
@jwt_required()
@client_required
def analyze_competitors():
    """Start competitor analysis for F&B business"""
    data = request.get_json()
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    your_handle = data.get('your_instagram')
    competitor_handles = data.get('competitor_handles', '').split(',')
    restaurant_type = data.get('restaurant_type', 'casual')
    
    if not your_handle:
        return jsonify({'error': 'Your Instagram handle is required'}), 400
    
    # Clean handles
    your_handle = your_handle.strip().replace('@', '')
    competitor_handles = [h.strip().replace('@', '') for h in competitor_handles if h.strip()]
    
    # Add default Kuwait F&B competitors if none provided
    if not competitor_handles:
        default_competitors = {
            'casual': ['slider_station', 'pick_kw', 'burgerboutique_kw'],
            'fastfood': ['kfc_kuwait', 'mcdonaldskuwait', 'burgerking_kw'],
            'cafe': ['cariboucoffeekw', 'starbuckskuwait', 'juicerykw'],
            'fine': ['nobu_kuwait', 'riccardokw', 'melenzane'],
            'delivery': ['talabat', 'deliveroo_kw', 'carriage_kw']
        }
        competitor_handles = default_competitors.get(restaurant_type, ['slider_station'])
    
    try:
        # Create or update competitors in database
        competitors = []
        for handle in competitor_handles[:3]:  # Limit to 3 competitors
            competitor = Competitor.query.filter_by(
                instagram_handle=handle,
                client_id=client_id
            ).first()
            
            if not competitor:
                competitor = Competitor(
                    client_id=client_id,
                    name=handle.replace('_', ' ').title(),
                    instagram_handle=handle,
                    business_type=restaurant_type,
                    is_active=True
                )
                db.session.add(competitor)
            
            competitors.append(competitor)
        
        db.session.commit()
        
        # Analyze competitors using the comprehensive service
        analysis_results = []
        for competitor in competitors:
            # Use the real analysis service (with mock data until scraper is implemented)
            analysis = competitor_analysis_service.analyze_competitor_content(
                competitor_id=competitor.id,
                days=30
            )
            
            # Add sentiment analysis
            sentiment = competitor_analysis_service.analyze_sentiment(
                competitor_id=competitor.id,
                days=30
            )
            
            # Format for frontend
            result = {
                'id': competitor.id,
                'name': competitor.name,
                'handle': f"@{competitor.instagram_handle}",
                'followers': _get_mock_followers(competitor.instagram_handle),  # Still mock until scraper
                'avg_likes': _get_mock_engagement(competitor.instagram_handle),
                'recent_posts': analysis.get('total_posts', 0),
                'best_times': _extract_best_times(analysis),
                'top_content': _extract_top_content(analysis),
                'insights': _generate_insights(analysis, sentiment),
                'engagement_rate': analysis.get('performance', {}).get('average_metrics', {}).get('engagement_rate', 0),
                'content_analysis': analysis.get('content_types', {}),
                'sentiment_score': sentiment.get('average_sentiment_score', 0) if sentiment else 0
            }
            analysis_results.append(result)
        
        # Create comparison with client
        if competitors:
            comparison = competitor_analysis_service.compare_with_client(
                client_id=client_id,
                competitor_id=competitors[0].id,
                days=30
            )
        
        return jsonify({
            'success': True,
            'competitors': analysis_results,
            'insights': {
                'optimal_posting_time': _get_optimal_time(analysis_results),
                'trending_content': _get_trending_content(analysis_results),
                'avg_engagement': _format_avg_engagement(analysis_results)
            },
            'best_practices': _get_fb_best_practices(restaurant_type)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@competitor_bp.route('/insights/<int:competitor_id>', methods=['GET'])
@jwt_required()
@client_required
def get_competitor_insights(competitor_id):
    """Get detailed insights for a specific competitor"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    competitor = Competitor.query.filter_by(
        id=competitor_id,
        client_id=client_id
    ).first()
    
    if not competitor:
        return jsonify({'error': 'Competitor not found'}), 404
    
    # Get recent content analysis
    recent_content = CompetitorContent.query.filter_by(
        competitor_id=competitor_id
    ).order_by(CompetitorContent.posted_at.desc()).limit(20).all()
    
    # Analyze patterns
    content_analysis = {
        'posting_frequency': _analyze_posting_frequency(recent_content),
        'best_performing': _get_best_performing(recent_content),
        'content_themes': _analyze_content_themes(recent_content),
        'hashtag_strategy': _analyze_hashtags(recent_content),
        'engagement_patterns': _analyze_engagement(recent_content)
    }
    
    # Get strategies
    strategies = CompetitorStrategy.query.filter_by(
        competitor_id=competitor_id
    ).order_by(CompetitorStrategy.effectiveness_score.desc()).all()
    
    return jsonify({
        'competitor': {
            'name': competitor.name,
            'handle': f"@{competitor.instagram_handle}",
            'business_type': competitor.business_type
        },
        'content_analysis': content_analysis,
        'strategies': [{
            'name': s.strategy_name,
            'description': s.description,
            'effectiveness': s.effectiveness_score,
            'examples': s.examples
        } for s in strategies],
        'recommendations': _generate_recommendations(content_analysis, competitor.business_type)
    }), 200

@competitor_bp.route('/trending', methods=['GET'])
@jwt_required()
@client_required
def get_trending_content():
    """Get trending F&B content in Kuwait"""
    platform = request.args.get('platform', 'instagram')
    
    trending = {
        'dishes': [
            {'name': 'Slider Boxes', 'posts': 1250, 'growth': '+15%'},
            {'name': 'Acai Bowls', 'posts': 890, 'growth': '+22%'},
            {'name': 'Kunafa Desserts', 'posts': 780, 'growth': '+8%'},
            {'name': 'Wagyu Burgers', 'posts': 650, 'growth': '+30%'}
        ],
        'hashtags': [
            {'tag': '#KuwaitFoodie', 'usage': 125000, 'engagement': '4.2%'},
            {'tag': '#Q8Food', 'usage': 98000, 'engagement': '3.8%'},
            {'tag': '#KuwaitRestaurants', 'usage': 76000, 'engagement': '3.5%'},
            {'tag': '#RamadanKuwait', 'usage': 45000, 'engagement': '5.1%'}
        ],
        'content_types': [
            {'type': 'Food Reels', 'engagement': '6.2%', 'tip': 'Show cooking process'},
            {'type': 'Customer Reviews', 'engagement': '4.8%', 'tip': 'Feature real testimonials'},
            {'type': 'Behind the Scenes', 'engagement': '4.5%', 'tip': 'Show your kitchen team'},
            {'type': 'Limited Offers', 'engagement': '4.1%', 'tip': 'Create urgency'}
        ],
        'posting_times': {
            'breakfast': {'time': '7:30 AM', 'engagement': '3.2%'},
            'lunch': {'time': '12:30 PM', 'engagement': '5.8%'},
            'dinner': {'time': '7:30 PM', 'engagement': '6.5%'},
            'late_night': {'time': '10:00 PM', 'engagement': '4.9%'}
        }
    }
    
    return jsonify(trending), 200

# Helper functions
def _get_mock_followers(handle):
    """Get mock follower count based on handle"""
    followers_map = {
        'slider_station': 125000,
        'pick_kw': 89000,
        'melenzane': 67000,
        'burgerboutique_kw': 45000,
        'cariboucoffeekw': 156000,
        'starbuckskuwait': 234000
    }
    return followers_map.get(handle, 25000)

def _get_mock_engagement(handle):
    """Get mock average engagement"""
    engagement_map = {
        'slider_station': 2500,
        'pick_kw': 1800,
        'melenzane': 1200,
        'burgerboutique_kw': 900,
        'cariboucoffeekw': 3200,
        'starbuckskuwait': 4500
    }
    return engagement_map.get(handle, 500)

def _get_mock_posts(handle):
    """Get mock recent posts data"""
    return [
        {
            'type': 'reel',
            'caption': 'New menu item launch!',
            'likes': 3200,
            'comments': 145,
            'posted': '2 days ago'
        },
        {
            'type': 'carousel',
            'caption': 'Weekend special offers',
            'likes': 2100,
            'comments': 89,
            'posted': '4 days ago'
        }
    ]

def _get_mock_posting_times(handle):
    """Get mock best posting times"""
    times_map = {
        'slider_station': ['12:30 PM', '8:00 PM'],
        'pick_kw': ['1:00 PM', '7:30 PM'],
        'melenzane': ['11:30 AM', '6:00 PM'],
        'cariboucoffeekw': ['7:00 AM', '3:00 PM']
    }
    return times_map.get(handle, ['12:00 PM', '7:00 PM'])

def _get_mock_content_types(handle):
    """Get mock top content types"""
    content_map = {
        'slider_station': 'Limited time offers, Behind the scenes',
        'pick_kw': 'New menu launches, Customer photos',
        'melenzane': 'Chef recommendations, Seasonal menus',
        'cariboucoffeekw': 'Morning coffee shots, Seasonal drinks'
    }
    return content_map.get(handle, 'Food photos, Special offers')

def _get_mock_insights(handle, restaurant_type):
    """Get mock competitor insights"""
    insights_map = {
        'slider_station': "Posts with 🔥 emoji get 40% more engagement",
        'pick_kw': "Video content performs 3x better than photos",
        'melenzane': "Italian language posts increase authenticity",
        'cariboucoffeekw': "Morning posts get 2x more reach"
    }
    
    general_insights = {
        'casual': "Family-oriented content performs best",
        'fastfood': "Speed and convenience messaging works",
        'cafe': "Aesthetic photos drive engagement",
        'fine': "Emphasize quality and experience",
        'delivery': "Show packaging and freshness"
    }
    
    return insights_map.get(handle, general_insights.get(restaurant_type, "Quality food photos drive engagement"))

def _get_fb_best_practices(restaurant_type):
    """Get F&B best practices for Kuwait market"""
    return {
        'content_mix': {
            'food_photos': '40%',
            'behind_scenes': '20%',
            'customer_content': '20%',
            'offers': '20%'
        },
        'kuwait_specific': [
            'Include Arabic captions for wider reach',
            'Post Iftar/Suhoor specials during Ramadan',
            'Avoid posting during prayer times',
            'Feature local ingredients and dishes',
            'Highlight family-friendly options'
        ],
        'engagement_tips': [
            'Ask questions in captions',
            'Run polls in stories',
            'Share customer reviews',
            'Show food preparation process',
            'Create FOMO with limited offers'
        ]
    }

def _analyze_posting_frequency(content):
    """Analyze posting frequency patterns"""
    if not content:
        return {'average': 0, 'pattern': 'No data'}
    
    # Calculate average posts per week
    date_range = (content[0].posted_at - content[-1].posted_at).days
    weeks = max(date_range / 7, 1)
    avg_per_week = len(content) / weeks
    
    return {
        'average_per_week': round(avg_per_week, 1),
        'pattern': 'Consistent' if avg_per_week >= 5 else 'Moderate'
    }

def _get_best_performing(content):
    """Get best performing content"""
    if not content:
        return []
    
    sorted_content = sorted(content, key=lambda x: x.engagement_rate, reverse=True)
    return [{
        'type': c.content_type,
        'caption_preview': c.caption[:50] if c.caption else '',
        'engagement_rate': c.engagement_rate,
        'likes': c.likes
    } for c in sorted_content[:3]]

def _analyze_content_themes(content):
    """Analyze content themes"""
    themes = {}
    for c in content:
        if c.content_category:
            themes[c.content_category] = themes.get(c.content_category, 0) + 1
    
    total = sum(themes.values())
    return {k: f"{(v/total)*100:.1f}%" for k, v in themes.items()}

def _analyze_hashtags(content):
    """Analyze hashtag strategy"""
    all_hashtags = []
    for c in content:
        if c.hashtags:
            all_hashtags.extend(c.hashtags)
    
    # Count frequency
    hashtag_counts = {}
    for tag in all_hashtags:
        hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
    
    # Get top hashtags
    top_tags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        'average_per_post': len(all_hashtags) / len(content) if content else 0,
        'top_hashtags': [{'tag': tag, 'usage': count} for tag, count in top_tags]
    }

def _analyze_engagement(content):
    """Analyze engagement patterns"""
    if not content:
        return {}
    
    by_type = {}
    for c in content:
        if c.content_type:
            if c.content_type not in by_type:
                by_type[c.content_type] = []
            by_type[c.content_type].append(c.engagement_rate)
    
    avg_by_type = {k: sum(v)/len(v) for k, v in by_type.items()}
    
    return {
        'by_content_type': avg_by_type,
        'overall_average': sum(c.engagement_rate for c in content) / len(content)
    }

def _generate_recommendations(analysis, business_type):
    """Generate actionable recommendations"""
    recommendations = []
    
    # Posting frequency
    if analysis['posting_frequency']['average_per_week'] < 5:
        recommendations.append({
            'category': 'Posting Frequency',
            'suggestion': 'Increase posting to at least 5 times per week',
            'impact': 'High'
        })
    
    # Content mix
    if 'content_themes' in analysis:
        themes = analysis['content_themes']
        if 'promotion' in themes and float(themes['promotion'].rstrip('%')) > 40:
            recommendations.append({
                'category': 'Content Mix',
                'suggestion': 'Balance promotional content with engaging stories',
                'impact': 'Medium'
            })
    
    # Hashtags
    if analysis['hashtag_strategy']['average_per_post'] < 10:
        recommendations.append({
            'category': 'Hashtags',
            'suggestion': 'Use 10-15 relevant hashtags per post',
            'impact': 'Medium'
        })
    
    return recommendations

def _extract_best_times(analysis):
    """Extract best posting times from analysis"""
    if not analysis or 'posting_patterns' not in analysis:
        return ['12:00 PM', '7:00 PM']
    
    patterns = analysis['posting_patterns']
    best_times = []
    
    # Get best performing times
    if 'best_performing_times' in patterns:
        for time_data in patterns['best_performing_times'][:2]:
            hour = time_data.get('hour', 12)
            # Convert 24h to 12h format
            if hour == 0:
                time_str = '12:00 AM'
            elif hour < 12:
                time_str = f'{hour}:00 AM'
            elif hour == 12:
                time_str = '12:00 PM'
            else:
                time_str = f'{hour-12}:00 PM'
            best_times.append(time_str)
    
    return best_times if best_times else ['12:00 PM', '7:00 PM']

def _extract_top_content(analysis):
    """Extract top content types from analysis"""
    if not analysis or 'content_types' not in analysis:
        return 'Food photos, Special offers'
    
    content_types = analysis['content_types']
    
    # Sort by engagement rate
    sorted_types = sorted(
        content_types.items(),
        key=lambda x: x[1].get('avg_engagement_rate', 0),
        reverse=True
    )
    
    # Get top 2 content types
    top_types = []
    for content_type, _ in sorted_types[:2]:
        # Format content type name
        formatted_type = content_type.replace('_', ' ').title()
        top_types.append(formatted_type)
    
    return ', '.join(top_types) if top_types else 'Food photos, Special offers'

def _generate_insights(analysis, sentiment):
    """Generate insights from analysis and sentiment data"""
    insights = []
    
    # Content performance insight
    if analysis and 'performance' in analysis:
        avg_engagement = analysis['performance'].get('average_metrics', {}).get('engagement_rate', 0)
        if avg_engagement > 5:
            insights.append(f"High engagement rate of {avg_engagement:.1f}% indicates strong content strategy")
        elif avg_engagement < 2:
            insights.append("Low engagement suggests need for content strategy improvement")
    
    # Sentiment insight
    if sentiment and 'average_sentiment_score' in sentiment:
        score = sentiment['average_sentiment_score']
        if score > 0.5:
            insights.append("Positive brand sentiment - customers love this brand")
        elif score < -0.2:
            insights.append("Negative sentiment detected - monitor customer complaints")
    
    # Posting pattern insight
    if analysis and 'posting_patterns' in analysis:
        posts_per_day = analysis['posting_patterns'].get('posts_per_day', 0)
        if posts_per_day > 2:
            insights.append(f"Very active with {posts_per_day:.1f} posts per day")
        elif posts_per_day < 0.5:
            insights.append("Infrequent posting may limit reach")
    
    # Strategy insight
    if analysis and 'identified_strategies' in analysis:
        strategies = analysis['identified_strategies']
        if strategies:
            first_strategy = strategies[0]
            insights.append(f"Using {first_strategy['name']} strategy")
    
    return insights[0] if insights else "Quality content drives engagement"

def _get_optimal_time(analysis_results):
    """Get optimal posting time from all competitor analysis"""
    all_times = {}
    
    for result in analysis_results:
        if 'best_times' in result and result['best_times']:
            for time in result['best_times']:
                all_times[time] = all_times.get(time, 0) + 1
    
    if all_times:
        # Return most common time
        return max(all_times.items(), key=lambda x: x[1])[0]
    
    return '7:30 PM'  # Default Kuwait dinner time

def _get_trending_content(analysis_results):
    """Get trending content types from competitor analysis"""
    content_types = {}
    
    for result in analysis_results:
        if 'content_analysis' in result:
            for content_type, stats in result['content_analysis'].items():
                if content_type not in content_types:
                    content_types[content_type] = {
                        'count': 0,
                        'avg_engagement': 0
                    }
                content_types[content_type]['count'] += stats.get('count', 0)
                content_types[content_type]['avg_engagement'] += stats.get('avg_engagement_rate', 0)
    
    # Calculate averages and sort by engagement
    trending = []
    for content_type, data in content_types.items():
        if data['count'] > 0:
            avg_engagement = data['avg_engagement'] / len(analysis_results)
            trending.append({
                'type': content_type.replace('_', ' ').title(),
                'engagement': f"{avg_engagement:.1f}%"
            })
    
    # Sort by engagement rate
    trending.sort(key=lambda x: float(x['engagement'].rstrip('%')), reverse=True)
    
    return trending[:3]  # Return top 3

def _format_avg_engagement(analysis_results):
    """Format average engagement across all competitors"""
    total_engagement = 0
    count = 0
    
    for result in analysis_results:
        if 'engagement_rate' in result:
            total_engagement += result['engagement_rate']
            count += 1
    
    if count > 0:
        avg = total_engagement / count
        return f"{avg:.1f}%"
    
    return "3.5%"  # Default