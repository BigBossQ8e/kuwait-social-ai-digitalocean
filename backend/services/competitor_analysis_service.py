"""
Enhanced Competitor Analysis Service for Kuwait Social AI
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import Counter
import numpy as np
from sqlalchemy import func, desc
import logging

from models import db
from models.competitor_analysis_models import (
    CompetitorContent, CompetitorSentiment, CompetitorAd,
    CompetitorStrategy, ContentComparison
)
from services.content_generator import ContentGenerator
from exceptions import KuwaitSocialAIException


class CompetitorAnalysisService:
    """Advanced competitor analysis service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.content_generator = ContentGenerator()
        
        # Content categories
        self.content_categories = [
            'product_showcase', 'promotion', 'educational', 
            'user_generated', 'behind_scenes', 'announcement',
            'seasonal', 'cultural', 'testimonial'
        ]
        
        # Sentiment emotions
        self.emotions = [
            'joy', 'trust', 'fear', 'surprise', 
            'sadness', 'disgust', 'anger', 'anticipation'
        ]
    
    def analyze_competitor_content(
        self,
        competitor_id: int,
        days: int = 30
    ) -> Dict[str, any]:
        """Comprehensive competitor content analysis"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Get competitor content
        content = CompetitorContent.query.filter(
            CompetitorContent.competitor_id == competitor_id,
            CompetitorContent.posted_at >= since_date
        ).all()
        
        if not content:
            return {
                'error': 'No content found for analysis',
                'competitor_id': competitor_id
            }
        
        # Analyze content types
        content_type_analysis = self._analyze_content_types(content)
        
        # Analyze posting patterns
        posting_patterns = self._analyze_posting_patterns(content)
        
        # Analyze performance
        performance_analysis = self._analyze_performance(content)
        
        # Analyze visual style
        visual_analysis = self._analyze_visual_style(content)
        
        # Identify strategies
        strategies = self._identify_strategies(content)
        
        return {
            'competitor_id': competitor_id,
            'analysis_period': f'{days} days',
            'total_posts': len(content),
            'content_types': content_type_analysis,
            'posting_patterns': posting_patterns,
            'performance': performance_analysis,
            'visual_style': visual_analysis,
            'identified_strategies': strategies,
            'recommendations': self._generate_recommendations(
                content_type_analysis, 
                performance_analysis, 
                strategies
            )
        }
    
    def analyze_sentiment(
        self,
        competitor_id: int,
        days: int = 30
    ) -> Dict[str, any]:
        """Analyze sentiment in competitor's comments"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Get sentiment data
        sentiments = db.session.query(CompetitorSentiment).join(
            CompetitorContent
        ).filter(
            CompetitorContent.competitor_id == competitor_id,
            CompetitorSentiment.analyzed_at >= since_date
        ).all()
        
        if not sentiments:
            return {
                'error': 'No sentiment data available',
                'competitor_id': competitor_id
            }
        
        # Overall sentiment distribution
        sentiment_dist = Counter([s.sentiment for s in sentiments])
        total = len(sentiments)
        
        # Emotion analysis
        emotion_scores = {}
        for emotion in self.emotions:
            scores = []
            for s in sentiments:
                if s.emotions and emotion in s.emotions:
                    scores.append(s.emotions[emotion])
            if scores:
                emotion_scores[emotion] = np.mean(scores)
        
        # Topic analysis
        topics = {}
        for s in sentiments:
            if s.topics:
                for topic in s.topics:
                    topics[topic] = topics.get(topic, 0) + 1
        
        # Common complaints and praises
        complaints = [s for s in sentiments if s.is_complaint]
        praises = [s for s in sentiments if s.is_praise]
        
        return {
            'competitor_id': competitor_id,
            'total_comments_analyzed': total,
            'sentiment_distribution': {
                'positive': (sentiment_dist.get('positive', 0) / total) * 100,
                'negative': (sentiment_dist.get('negative', 0) / total) * 100,
                'neutral': (sentiment_dist.get('neutral', 0) / total) * 100
            },
            'average_sentiment_score': np.mean([s.sentiment_score for s in sentiments]),
            'dominant_emotions': sorted(
                emotion_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3],
            'top_topics': sorted(
                topics.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10],
            'complaint_rate': (len(complaints) / total) * 100,
            'praise_rate': (len(praises) / total) * 100,
            'common_complaints': self._extract_common_themes(complaints),
            'common_praises': self._extract_common_themes(praises),
            'language_distribution': self._analyze_language_distribution(sentiments)
        }
    
    def track_competitor_ads(
        self,
        competitor_id: int
    ) -> Dict[str, any]:
        """Track and analyze competitor advertising"""
        # Get active ads
        active_ads = CompetitorAd.query.filter_by(
            competitor_id=competitor_id,
            is_active=True
        ).all()
        
        # Get historical ads
        all_ads = CompetitorAd.query.filter_by(
            competitor_id=competitor_id
        ).all()
        
        if not all_ads:
            return {
                'error': 'No advertising data available',
                'competitor_id': competitor_id
            }
        
        # Analyze ad types
        ad_types = Counter([ad.ad_type for ad in all_ads])
        
        # Analyze objectives
        objectives = Counter([ad.ad_objective for ad in all_ads])
        
        # Analyze CTAs
        ctas = Counter([ad.call_to_action for ad in all_ads])
        
        # Analyze offers
        offers = []
        for ad in all_ads:
            if ad.offer_type:
                offers.append({
                    'type': ad.offer_type,
                    'ad_id': ad.id,
                    'first_seen': ad.first_seen,
                    'is_active': ad.is_active
                })
        
        # Calculate ad frequency
        ad_frequency = len(all_ads) / max(1, (
            (datetime.utcnow() - min(ad.first_seen for ad in all_ads)).days / 30
        ))
        
        return {
            'competitor_id': competitor_id,
            'total_ads_tracked': len(all_ads),
            'active_ads': len(active_ads),
            'ad_types': dict(ad_types),
            'objectives': dict(objectives),
            'top_ctas': dict(ctas.most_common(5)),
            'offers_used': offers,
            'ad_frequency_per_month': round(ad_frequency, 1),
            'active_campaigns': self._analyze_active_campaigns(active_ads),
            'seasonal_patterns': self._analyze_seasonal_ad_patterns(all_ads)
        }
    
    def compare_with_client(
        self,
        client_id: int,
        competitor_id: int,
        days: int = 30
    ) -> ContentComparison:
        """Create detailed comparison between client and competitor"""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        # Get or create comparison
        comparison = ContentComparison.query.filter_by(
            client_id=client_id,
            competitor_id=competitor_id,
            period_start=start_date,
            period_end=end_date
        ).first()
        
        if not comparison:
            comparison = ContentComparison(
                client_id=client_id,
                competitor_id=competitor_id,
                period_start=start_date,
                period_end=end_date
            )
            db.session.add(comparison)
        
        # Analyze client content (would need client content model)
        # For now, using placeholder data
        client_metrics = self._get_client_metrics(client_id, start_date, end_date)
        
        # Analyze competitor content
        competitor_metrics = self._get_competitor_metrics(competitor_id, start_date, end_date)
        
        # Calculate gaps
        comparison.engagement_gap = (
            client_metrics['avg_engagement'] - competitor_metrics['avg_engagement']
        )
        
        # Generate insights
        insights = self._generate_comparison_insights(client_metrics, competitor_metrics)
        comparison.key_insights = insights
        
        # Generate recommendations
        recommendations = self._generate_comparison_recommendations(
            client_metrics, 
            competitor_metrics, 
            insights
        )
        comparison.recommendations = recommendations
        
        db.session.commit()
        
        return comparison
    
    def _analyze_content_types(self, content: List[CompetitorContent]) -> Dict:
        """Analyze distribution of content types"""
        type_counts = Counter([c.content_type for c in content])
        total = len(content)
        
        type_performance = {}
        for content_type in type_counts:
            type_content = [c for c in content if c.content_type == content_type]
            avg_engagement = np.mean([c.engagement_rate for c in type_content])
            type_performance[content_type] = {
                'count': type_counts[content_type],
                'percentage': (type_counts[content_type] / total) * 100,
                'avg_engagement_rate': avg_engagement
            }
        
        return type_performance
    
    def _analyze_posting_patterns(self, content: List[CompetitorContent]) -> Dict:
        """Analyze when competitor posts"""
        # Day analysis
        day_counts = Counter([c.posted_day for c in content])
        
        # Hour analysis
        hour_counts = Counter([c.posted_hour for c in content])
        
        # Best performing times
        best_times = []
        for c in sorted(content, key=lambda x: x.engagement_rate, reverse=True)[:10]:
            best_times.append({
                'day': c.posted_day,
                'hour': c.posted_hour,
                'engagement_rate': c.engagement_rate
            })
        
        # Posting frequency
        date_range = (max(c.posted_at for c in content) - min(c.posted_at for c in content)).days
        posts_per_day = len(content) / max(1, date_range)
        
        return {
            'posts_by_day': dict(day_counts),
            'posts_by_hour': dict(hour_counts),
            'best_performing_times': best_times,
            'posts_per_day': round(posts_per_day, 2),
            'most_active_day': max(day_counts, key=day_counts.get),
            'most_active_hour': max(hour_counts, key=hour_counts.get)
        }
    
    def _analyze_performance(self, content: List[CompetitorContent]) -> Dict:
        """Analyze content performance metrics"""
        # Calculate averages
        avg_likes = np.mean([c.likes for c in content])
        avg_comments = np.mean([c.comments for c in content])
        avg_shares = np.mean([c.shares for c in content])
        avg_engagement_rate = np.mean([c.engagement_rate for c in content])
        
        # Find top performers
        top_posts = sorted(content, key=lambda x: x.engagement_rate, reverse=True)[:5]
        
        # Virality analysis
        viral_posts = [c for c in content if c.virality_score > 80]
        
        return {
            'average_metrics': {
                'likes': round(avg_likes, 0),
                'comments': round(avg_comments, 0),
                'shares': round(avg_shares, 0),
                'engagement_rate': round(avg_engagement_rate, 2)
            },
            'top_posts': [{
                'id': p.id,
                'type': p.content_type,
                'engagement_rate': p.engagement_rate,
                'posted_at': p.posted_at.isoformat()
            } for p in top_posts],
            'viral_posts_count': len(viral_posts),
            'viral_rate': (len(viral_posts) / len(content)) * 100
        }
    
    def _analyze_visual_style(self, content: List[CompetitorContent]) -> Dict:
        """Analyze visual branding and style"""
        # Color analysis
        all_colors = []
        for c in content:
            if c.dominant_colors:
                all_colors.extend(c.dominant_colors)
        
        color_counts = Counter(all_colors)
        
        # Content elements
        contains_text_pct = (
            len([c for c in content if c.contains_text]) / len(content)
        ) * 100
        contains_people_pct = (
            len([c for c in content if c.contains_people]) / len(content)
        ) * 100
        contains_product_pct = (
            len([c for c in content if c.contains_product]) / len(content)
        ) * 100
        
        return {
            'dominant_colors': dict(color_counts.most_common(5)),
            'visual_elements': {
                'contains_text': round(contains_text_pct, 1),
                'contains_people': round(contains_people_pct, 1),
                'contains_product': round(contains_product_pct, 1)
            },
            'brand_consistency': self._calculate_brand_consistency(content)
        }
    
    def _identify_strategies(self, content: List[CompetitorContent]) -> List[Dict]:
        """Identify competitor strategies from content patterns"""
        strategies = []
        
        # Check for product launch strategy
        product_posts = [c for c in content if c.content_category == 'product_launch']
        if len(product_posts) >= 3:
            strategies.append({
                'type': 'product_focus',
                'name': 'Frequent Product Launches',
                'confidence': 85,
                'description': 'Competitor regularly introduces new products',
                'frequency': f'{len(product_posts)} launches in period'
            })
        
        # Check for promotion strategy
        promo_posts = [c for c in content if c.content_category == 'promotion']
        if len(promo_posts) / len(content) > 0.3:
            strategies.append({
                'type': 'promotional',
                'name': 'Heavy Promotional Strategy',
                'confidence': 90,
                'description': 'Over 30% of content is promotional',
                'impact': 'May lead to follower fatigue'
            })
        
        # Check for UGC strategy
        ugc_posts = [c for c in content if c.content_category == 'user_generated']
        if len(ugc_posts) / len(content) > 0.2:
            strategies.append({
                'type': 'community',
                'name': 'User-Generated Content Focus',
                'confidence': 80,
                'description': 'Leverages customer content for authenticity',
                'effectiveness': 'High - builds trust and community'
            })
        
        return strategies
    
    def _generate_recommendations(
        self,
        content_analysis: Dict,
        performance: Dict,
        strategies: List[Dict]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Content type recommendations
        best_performing_type = max(
            content_analysis.items(),
            key=lambda x: x[1]['avg_engagement_rate']
        )[0]
        recommendations.append(
            f"Focus on {best_performing_type} content - competitor sees "
            f"{content_analysis[best_performing_type]['avg_engagement_rate']:.1f}% engagement"
        )
        
        # Performance recommendations
        if performance['viral_rate'] > 5:
            recommendations.append(
                "Study competitor's viral content strategy - "
                f"{performance['viral_rate']:.1f}% of posts go viral"
            )
        
        # Counter-strategy recommendations
        for strategy in strategies:
            if strategy['type'] == 'promotional':
                recommendations.append(
                    "Differentiate with value-driven content to counter "
                    "competitor's heavy promotional approach"
                )
            elif strategy['type'] == 'community':
                recommendations.append(
                    "Develop UGC campaign to match competitor's "
                    "community engagement strategy"
                )
        
        return recommendations
    
    def _extract_common_themes(self, sentiments: List[CompetitorSentiment]) -> List[str]:
        """Extract common themes from sentiments"""
        themes = []
        
        # Aggregate topics
        all_topics = []
        for s in sentiments:
            if s.topics:
                all_topics.extend(s.topics)
        
        # Get top themes
        topic_counts = Counter(all_topics)
        for topic, count in topic_counts.most_common(5):
            themes.append(f"{topic} ({count} mentions)")
        
        return themes
    
    def _analyze_language_distribution(self, sentiments: List[CompetitorSentiment]) -> Dict:
        """Analyze language distribution in comments"""
        total = len(sentiments)
        arabic_count = len([s for s in sentiments if s.is_arabic])
        
        return {
            'arabic': (arabic_count / total) * 100,
            'english': ((total - arabic_count) / total) * 100
        }
    
    def _analyze_active_campaigns(self, ads: List[CompetitorAd]) -> List[Dict]:
        """Analyze currently active ad campaigns"""
        campaigns = []
        
        for ad in ads:
            campaign = {
                'ad_type': ad.ad_type,
                'objective': ad.ad_objective,
                'cta': ad.call_to_action,
                'running_days': (datetime.utcnow() - ad.first_seen).days,
                'offer': ad.offer_type
            }
            campaigns.append(campaign)
        
        return campaigns
    
    def _analyze_seasonal_ad_patterns(self, ads: List[CompetitorAd]) -> Dict:
        """Analyze seasonal patterns in advertising"""
        # Group by month
        monthly_ads = {}
        for ad in ads:
            month = ad.first_seen.strftime('%B')
            if month not in monthly_ads:
                monthly_ads[month] = 0
            monthly_ads[month] += 1
        
        return monthly_ads
    
    def _calculate_brand_consistency(self, content: List[CompetitorContent]) -> float:
        """Calculate visual brand consistency score"""
        # Simple implementation - check color consistency
        if not content:
            return 0.0
        
        color_lists = [c.dominant_colors for c in content if c.dominant_colors]
        if not color_lists:
            return 0.0
        
        # Check how often the same colors appear
        all_colors = []
        for colors in color_lists:
            all_colors.extend(colors[:3])  # Top 3 colors
        
        color_counts = Counter(all_colors)
        if color_counts:
            # If top color appears in >50% of posts, high consistency
            top_color_count = color_counts.most_common(1)[0][1]
            consistency = (top_color_count / len(color_lists)) * 100
            return min(consistency * 2, 100)  # Scale up and cap at 100
        
        return 0.0
    
    def _get_client_metrics(self, client_id: int, start_date, end_date) -> Dict:
        """Get client metrics for comparison (placeholder)"""
        # This would fetch actual client metrics
        return {
            'post_count': 25,
            'avg_engagement': 4.5,
            'avg_reach': 5000,
            'content_types': {'photo': 60, 'video': 30, 'carousel': 10},
            'posting_times': {'morning': 40, 'afternoon': 35, 'evening': 25}
        }
    
    def _get_competitor_metrics(self, competitor_id: int, start_date, end_date) -> Dict:
        """Get competitor metrics for comparison"""
        content = CompetitorContent.query.filter(
            CompetitorContent.competitor_id == competitor_id,
            CompetitorContent.posted_at >= start_date,
            CompetitorContent.posted_at <= end_date
        ).all()
        
        if not content:
            return {
                'post_count': 0,
                'avg_engagement': 0,
                'avg_reach': 0,
                'content_types': {},
                'posting_times': {}
            }
        
        return {
            'post_count': len(content),
            'avg_engagement': np.mean([c.engagement_rate for c in content]),
            'avg_reach': np.mean([c.reach for c in content]),
            'content_types': dict(Counter([c.content_type for c in content])),
            'posting_times': self._categorize_posting_times(content)
        }
    
    def _categorize_posting_times(self, content: List[CompetitorContent]) -> Dict:
        """Categorize posting times into morning, afternoon, evening"""
        times = {'morning': 0, 'afternoon': 0, 'evening': 0}
        
        for c in content:
            hour = c.posted_hour
            if 6 <= hour < 12:
                times['morning'] += 1
            elif 12 <= hour < 18:
                times['afternoon'] += 1
            else:
                times['evening'] += 1
        
        return times
    
    def _generate_comparison_insights(self, client_metrics: Dict, competitor_metrics: Dict) -> List[str]:
        """Generate insights from comparison"""
        insights = []
        
        # Posting frequency
        if competitor_metrics['post_count'] > client_metrics['post_count'] * 1.5:
            insights.append(
                f"Competitor posts {competitor_metrics['post_count']/client_metrics['post_count']:.1f}x "
                "more frequently"
            )
        
        # Engagement comparison
        if competitor_metrics['avg_engagement'] > client_metrics['avg_engagement']:
            insights.append(
                f"Competitor has {competitor_metrics['avg_engagement']-client_metrics['avg_engagement']:.1f}% "
                "higher engagement rate"
            )
        
        return insights
    
    def _generate_comparison_recommendations(
        self,
        client_metrics: Dict,
        competitor_metrics: Dict,
        insights: List[str]
    ) -> List[str]:
        """Generate recommendations from comparison"""
        recommendations = []
        
        # Content type recommendations
        competitor_best = max(
            competitor_metrics['content_types'].items(),
            key=lambda x: x[1]
        )[0] if competitor_metrics['content_types'] else None
        
        if competitor_best:
            recommendations.append(
                f"Increase {competitor_best} content - competitor sees success with this format"
            )
        
        # Posting time recommendations
        competitor_peak = max(
            competitor_metrics['posting_times'].items(),
            key=lambda x: x[1]
        )[0] if competitor_metrics['posting_times'] else None
        
        if competitor_peak:
            recommendations.append(
                f"Test posting during {competitor_peak} hours when competitor is most active"
            )
        
        return recommendations


# Note: No singleton instance created here
# Use get_competitor_analysis_service() from services.container instead