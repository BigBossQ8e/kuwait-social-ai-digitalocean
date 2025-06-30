"""
Hashtag Strategy Service for Kuwait Social AI
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import Counter
import numpy as np
from sqlalchemy import func, desc
import logging

from models import db
from models.hashtag_models import (
    HashtagGroup, HashtagPerformance, CompetitorHashtag,
    HashtagRecommendation, HashtagTrend
)
from exceptions import KuwaitSocialAIException


class HashtagStrategyService:
    """Service for hashtag strategy and analytics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.max_hashtags = {
            'instagram': 30,
            'snapchat': 100
        }
        
        # Kuwait-specific trending hashtags (to be updated regularly)
        self.kuwait_base_hashtags = [
            '#Kuwait', '#الكويت', '#Q8', '#KuwaitCity',
            '#Kuwait_Instagram', '#KuwaitBusiness', '#KuwaitLife'
        ]
    
    def create_hashtag_group(
        self, 
        client_id: int, 
        name: str, 
        hashtags: List[str], 
        category: str = None,
        description: str = None
    ) -> HashtagGroup:
        """Create a new hashtag group"""
        # Validate hashtags
        cleaned_hashtags = self._clean_hashtags(hashtags)
        
        # Check for existing group with same name
        existing = HashtagGroup.query.filter_by(
            client_id=client_id, 
            name=name
        ).first()
        
        if existing:
            raise ValueError(f"Hashtag group '{name}' already exists")
        
        # Create new group
        group = HashtagGroup(
            client_id=client_id,
            name=name,
            description=description,
            hashtags=cleaned_hashtags,
            category=category
        )
        
        db.session.add(group)
        db.session.commit()
        
        return group
    
    def analyze_hashtag_performance(
        self, 
        client_id: int, 
        days: int = 30
    ) -> Dict[str, any]:
        """Analyze hashtag performance over specified period"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all hashtag performance records
        performances = HashtagPerformance.query.filter(
            HashtagPerformance.client_id == client_id,
            HashtagPerformance.measured_at >= since_date
        ).all()
        
        if not performances:
            return {
                'top_performing': [],
                'worst_performing': [],
                'trending_up': [],
                'trending_down': [],
                'recommendations': []
            }
        
        # Aggregate by hashtag
        hashtag_stats = {}
        for perf in performances:
            if perf.hashtag not in hashtag_stats:
                hashtag_stats[perf.hashtag] = {
                    'total_reach': 0,
                    'total_engagement': 0,
                    'uses': 0,
                    'avg_engagement_rate': []
                }
            
            stats = hashtag_stats[perf.hashtag]
            stats['total_reach'] += perf.reach or 0
            stats['total_engagement'] += perf.engagement or 0
            stats['uses'] += 1
            if perf.engagement_rate:
                stats['avg_engagement_rate'].append(perf.engagement_rate)
        
        # Calculate final metrics
        for hashtag, stats in hashtag_stats.items():
            if stats['avg_engagement_rate']:
                stats['avg_engagement_rate'] = np.mean(stats['avg_engagement_rate'])
            else:
                stats['avg_engagement_rate'] = 0
        
        # Sort and categorize
        sorted_by_engagement = sorted(
            hashtag_stats.items(),
            key=lambda x: x[1]['avg_engagement_rate'],
            reverse=True
        )
        
        return {
            'top_performing': sorted_by_engagement[:10],
            'worst_performing': sorted_by_engagement[-10:] if len(sorted_by_engagement) > 10 else [],
            'trending_up': self._identify_trending_hashtags(performances, 'up'),
            'trending_down': self._identify_trending_hashtags(performances, 'down'),
            'recommendations': self._generate_recommendations(client_id, hashtag_stats)
        }
    
    def analyze_competitor_hashtags(
        self, 
        competitor_id: int,
        include_performance: bool = True
    ) -> Dict[str, any]:
        """Analyze hashtags used by a specific competitor"""
        competitor_hashtags = CompetitorHashtag.query.filter_by(
            competitor_id=competitor_id
        ).order_by(
            desc(CompetitorHashtag.avg_engagement)
        ).all()
        
        if not competitor_hashtags:
            return {
                'total_unique_hashtags': 0,
                'top_hashtags': [],
                'trending_hashtags': [],
                'exclusive_hashtags': []
            }
        
        # Analyze hashtag usage
        hashtag_data = []
        for ch in competitor_hashtags:
            data = {
                'hashtag': ch.hashtag,
                'usage_count': ch.usage_count,
                'avg_engagement': ch.avg_engagement,
                'is_trending': ch.is_trending,
                'trend_score': ch.trend_score
            }
            
            if include_performance and ch.best_performing_post:
                data['best_post'] = ch.best_performing_post
            
            hashtag_data.append(data)
        
        # Find exclusive hashtags (not commonly used)
        exclusive = self._find_exclusive_hashtags(competitor_hashtags)
        
        return {
            'total_unique_hashtags': len(competitor_hashtags),
            'top_hashtags': hashtag_data[:20],
            'trending_hashtags': [h for h in hashtag_data if h['is_trending']][:10],
            'exclusive_hashtags': exclusive,
            'usage_patterns': self._analyze_usage_patterns(competitor_hashtags)
        }
    
    def get_trending_hashtags(
        self,
        category: str = None,
        limit: int = 20
    ) -> List[Dict[str, any]]:
        """Get currently trending hashtags in Kuwait"""
        query = HashtagTrend.query
        
        if category:
            query = query.filter_by(category=category)
        
        # Filter for currently relevant hashtags
        now = datetime.utcnow()
        query = query.filter(
            db.or_(
                HashtagTrend.is_seasonal == False,
                db.and_(
                    HashtagTrend.is_seasonal == True,
                    HashtagTrend.season_start <= now.date(),
                    HashtagTrend.season_end >= now.date()
                )
            )
        )
        
        trends = query.order_by(
            desc(HashtagTrend.popularity_score)
        ).limit(limit).all()
        
        return [{
            'hashtag': trend.hashtag,
            'score': trend.popularity_score,
            'growth_rate': trend.growth_rate,
            'category': trend.category,
            'peak_time': trend.peak_time.strftime('%H:%M') if trend.peak_time else None,
            'is_seasonal': trend.is_seasonal,
            'avg_engagement': trend.avg_engagement
        } for trend in trends]
    
    def generate_smart_recommendations(
        self,
        client_id: int,
        content_type: str,
        caption: str = None,
        competitor_analysis: bool = True
    ) -> List[Dict[str, any]]:
        """Generate smart hashtag recommendations using AI and analytics"""
        recommendations = []
        
        # 1. Analyze client's historical performance
        client_top_hashtags = self._get_client_top_performers(client_id)
        
        # 2. Get trending hashtags
        trending = self.get_trending_hashtags(limit=50)
        
        # 3. Analyze competitors if requested
        competitor_hashtags = []
        if competitor_analysis:
            competitor_hashtags = self._get_competitor_insights(client_id)
        
        # 4. Generate contextual hashtags based on caption
        contextual = []
        if caption:
            contextual = self._extract_contextual_hashtags(caption)
        
        # 5. Combine and score recommendations
        all_hashtags = {}
        
        # Add client's top performers (high weight)
        for hashtag, stats in client_top_hashtags:
            all_hashtags[hashtag] = {
                'hashtag': hashtag,
                'score': stats['avg_engagement_rate'] * 0.4,  # 40% weight
                'reason': 'Historically performs well for your content',
                'category': 'proven_performer'
            }
        
        # Add trending hashtags (medium weight)
        for trend in trending:
            hashtag = trend['hashtag']
            if hashtag not in all_hashtags:
                all_hashtags[hashtag] = {
                    'hashtag': hashtag,
                    'score': 0,
                    'reason': '',
                    'category': 'trending'
                }
            all_hashtags[hashtag]['score'] += trend['score'] * 0.3  # 30% weight
            all_hashtags[hashtag]['reason'] = f"Trending in Kuwait (score: {trend['score']:.0f})"
        
        # Add competitor insights (medium weight)
        for comp_tag in competitor_hashtags:
            hashtag = comp_tag['hashtag']
            if hashtag not in all_hashtags:
                all_hashtags[hashtag] = {
                    'hashtag': hashtag,
                    'score': 0,
                    'reason': '',
                    'category': 'competitor'
                }
            all_hashtags[hashtag]['score'] += comp_tag['effectiveness'] * 0.2  # 20% weight
            all_hashtags[hashtag]['reason'] += f" Used by successful competitors"
        
        # Add contextual hashtags (low weight)
        for hashtag in contextual:
            if hashtag not in all_hashtags:
                all_hashtags[hashtag] = {
                    'hashtag': hashtag,
                    'score': 10,  # Base score
                    'reason': 'Relevant to your content',
                    'category': 'contextual'
                }
        
        # Sort by score and return top recommendations
        sorted_recommendations = sorted(
            all_hashtags.values(),
            key=lambda x: x['score'],
            reverse=True
        )
        
        # Store recommendations in database
        for rec in sorted_recommendations[:30]:
            db_rec = HashtagRecommendation(
                client_id=client_id,
                hashtag=rec['hashtag'],
                reason=rec['reason'],
                score=rec['score'],
                category=rec['category']
            )
            db.session.add(db_rec)
        
        db.session.commit()
        
        return sorted_recommendations[:30]
    
    def track_hashtag_performance(
        self,
        post_id: int,
        hashtags: List[str],
        metrics: Dict[str, int]
    ):
        """Track performance metrics for hashtags used in a post"""
        for hashtag in hashtags:
            perf = HashtagPerformance(
                hashtag=hashtag,
                post_id=post_id,
                client_id=metrics.get('client_id'),
                impressions=metrics.get('impressions', 0),
                reach=metrics.get('reach', 0),
                engagement=metrics.get('engagement', 0),
                clicks=metrics.get('clicks', 0),
                saves=metrics.get('saves', 0),
                platform=metrics.get('platform'),
                posted_at=metrics.get('posted_at')
            )
            perf.calculate_engagement_rate()
            db.session.add(perf)
        
        db.session.commit()
    
    def _clean_hashtags(self, hashtags: List[str]) -> List[str]:
        """Clean and validate hashtags"""
        cleaned = []
        for tag in hashtags:
            # Ensure hashtag starts with #
            if not tag.startswith('#'):
                tag = '#' + tag
            
            # Remove spaces and special characters
            tag = re.sub(r'[^\w#\u0600-\u06FF]', '', tag)
            
            # Skip empty or invalid hashtags
            if len(tag) > 1 and tag != '#':
                cleaned.append(tag)
        
        return list(set(cleaned))  # Remove duplicates
    
    def _identify_trending_hashtags(
        self, 
        performances: List[HashtagPerformance],
        direction: str = 'up'
    ) -> List[Tuple[str, float]]:
        """Identify hashtags trending up or down"""
        # Group performances by week
        weekly_data = {}
        for perf in performances:
            week = perf.measured_at.isocalendar()[1]
            hashtag = perf.hashtag
            
            if hashtag not in weekly_data:
                weekly_data[hashtag] = {}
            
            if week not in weekly_data[hashtag]:
                weekly_data[hashtag][week] = []
            
            weekly_data[hashtag][week].append(perf.engagement_rate or 0)
        
        # Calculate trends
        trends = []
        for hashtag, weeks in weekly_data.items():
            if len(weeks) < 2:
                continue
            
            # Get average engagement per week
            week_avgs = []
            for week in sorted(weeks.keys()):
                week_avgs.append(np.mean(weeks[week]))
            
            # Calculate trend (simple linear regression slope)
            if len(week_avgs) >= 2:
                x = np.arange(len(week_avgs))
                slope = np.polyfit(x, week_avgs, 1)[0]
                
                if (direction == 'up' and slope > 0) or (direction == 'down' and slope < 0):
                    trends.append((hashtag, abs(slope)))
        
        # Sort by trend strength
        trends.sort(key=lambda x: x[1], reverse=True)
        return trends[:10]
    
    def _generate_recommendations(
        self,
        client_id: int,
        current_hashtags: Dict[str, Dict]
    ) -> List[str]:
        """Generate hashtag recommendations based on performance"""
        recommendations = []
        
        # Recommend high-performing hashtags not frequently used
        for hashtag, stats in current_hashtags.items():
            if stats['uses'] < 5 and stats['avg_engagement_rate'] > 5:
                recommendations.append(f"Use {hashtag} more often - high engagement rate")
        
        # Recommend trending Kuwait hashtags
        trending = self.get_trending_hashtags(limit=5)
        for trend in trending:
            if trend['hashtag'] not in current_hashtags:
                recommendations.append(
                    f"Try {trend['hashtag']} - trending in Kuwait (score: {trend['score']:.0f})"
                )
        
        return recommendations[:10]
    
    def _find_exclusive_hashtags(
        self,
        competitor_hashtags: List[CompetitorHashtag]
    ) -> List[str]:
        """Find hashtags that are exclusive/unique to this competitor"""
        # This would ideally check against a broader dataset
        # For now, return hashtags with low usage count
        exclusive = []
        for ch in competitor_hashtags:
            if ch.usage_count <= 3:  # Used in 3 or fewer posts
                exclusive.append(ch.hashtag)
        
        return exclusive[:10]
    
    def _analyze_usage_patterns(
        self,
        competitor_hashtags: List[CompetitorHashtag]
    ) -> Dict[str, any]:
        """Analyze patterns in competitor hashtag usage"""
        total_hashtags = len(competitor_hashtags)
        
        # Category distribution (simplified)
        categories = {
            'brand': 0,
            'location': 0,
            'product': 0,
            'generic': 0,
            'arabic': 0
        }
        
        for ch in competitor_hashtags:
            hashtag = ch.hashtag.lower()
            if 'kuwait' in hashtag or 'q8' in hashtag:
                categories['location'] += 1
            elif any(c in 'اأإآؤئءبتثجحخدذرزسشصضطظعغفقكلمنهوي' for c in hashtag):
                categories['arabic'] += 1
            else:
                categories['generic'] += 1
        
        return {
            'total_unique': total_hashtags,
            'category_distribution': categories,
            'avg_hashtags_per_post': sum(ch.usage_count for ch in competitor_hashtags) / total_hashtags
        }
    
    def _get_client_top_performers(
        self,
        client_id: int,
        limit: int = 20
    ) -> List[Tuple[str, Dict]]:
        """Get client's top performing hashtags"""
        # Implementation would query HashtagPerformance
        # For now, return empty list
        return []
    
    def _get_competitor_insights(
        self,
        client_id: int
    ) -> List[Dict[str, any]]:
        """Get hashtag insights from competitors"""
        # Implementation would analyze competitor hashtags
        # For now, return empty list
        return []
    
    def _extract_contextual_hashtags(
        self,
        caption: str
    ) -> List[str]:
        """Extract relevant hashtags from caption context"""
        # Simple implementation - extract important words
        words = re.findall(r'\b\w+\b', caption.lower())
        
        # Filter for relevant terms
        relevant_terms = []
        for word in words:
            if len(word) > 4:  # Skip short words
                relevant_terms.append(f'#{word}')
        
        return relevant_terms[:10]


# Note: No singleton instance created here
# Use get_hashtag_strategy_service() from services.container instead