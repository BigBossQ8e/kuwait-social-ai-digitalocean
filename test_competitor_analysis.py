#!/usr/bin/env python3
"""
Test script for competitor analysis integration
"""

import os
import sys
import json
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app
from models import db, Client, Competitor
from models.competitor_analysis_models import CompetitorContent
from services.competitor_analysis_service import competitor_analysis_service

def test_competitor_analysis():
    """Test the competitor analysis service"""
    app = create_app()
    
    with app.app_context():
        print("Testing Competitor Analysis Integration...")
        print("-" * 50)
        
        # Get a test client
        client = Client.query.first()
        if not client:
            print("❌ No client found. Please create a client first.")
            return
        
        print(f"✅ Using client: {client.business_name}")
        
        # Create a test competitor
        competitor = Competitor.query.filter_by(
            instagram_handle='slider_station',
            client_id=client.id
        ).first()
        
        if not competitor:
            competitor = Competitor(
                client_id=client.id,
                name='Slider Station',
                instagram_handle='slider_station',
                business_type='casual',
                is_active=True
            )
            db.session.add(competitor)
            db.session.commit()
            print(f"✅ Created test competitor: {competitor.name}")
        else:
            print(f"✅ Found existing competitor: {competitor.name}")
        
        # Test 1: Analyze competitor content
        print("\n1. Testing content analysis...")
        try:
            analysis = competitor_analysis_service.analyze_competitor_content(
                competitor_id=competitor.id,
                days=30
            )
            print(f"✅ Content analysis completed:")
            print(f"   - Total posts: {analysis.get('total_posts', 0)}")
            print(f"   - Analysis period: {analysis.get('analysis_period', 'N/A')}")
            
            if 'content_types' in analysis:
                print("   - Content types analyzed")
            if 'posting_patterns' in analysis:
                print("   - Posting patterns identified")
            if 'recommendations' in analysis:
                print(f"   - {len(analysis['recommendations'])} recommendations generated")
        except Exception as e:
            print(f"❌ Content analysis failed: {str(e)}")
        
        # Test 2: Analyze sentiment
        print("\n2. Testing sentiment analysis...")
        try:
            sentiment = competitor_analysis_service.analyze_sentiment(
                competitor_id=competitor.id,
                days=30
            )
            print(f"✅ Sentiment analysis completed:")
            if 'average_sentiment_score' in sentiment:
                print(f"   - Average sentiment: {sentiment['average_sentiment_score']:.2f}")
            if 'sentiment_distribution' in sentiment:
                print(f"   - Positive: {sentiment['sentiment_distribution'].get('positive', 0):.1f}%")
                print(f"   - Negative: {sentiment['sentiment_distribution'].get('negative', 0):.1f}%")
                print(f"   - Neutral: {sentiment['sentiment_distribution'].get('neutral', 0):.1f}%")
        except Exception as e:
            print(f"❌ Sentiment analysis failed: {str(e)}")
        
        # Test 3: Track competitor ads
        print("\n3. Testing ad tracking...")
        try:
            ads = competitor_analysis_service.track_competitor_ads(
                competitor_id=competitor.id
            )
            print(f"✅ Ad tracking completed:")
            print(f"   - Total ads tracked: {ads.get('total_ads_tracked', 0)}")
            print(f"   - Active ads: {ads.get('active_ads', 0)}")
            if 'ad_frequency_per_month' in ads:
                print(f"   - Ad frequency: {ads['ad_frequency_per_month']} per month")
        except Exception as e:
            print(f"❌ Ad tracking failed: {str(e)}")
        
        # Test 4: Compare with client
        print("\n4. Testing client comparison...")
        try:
            comparison = competitor_analysis_service.compare_with_client(
                client_id=client.id,
                competitor_id=competitor.id,
                days=30
            )
            print(f"✅ Comparison completed:")
            print(f"   - Engagement gap: {comparison.engagement_gap:.2f}%")
            if comparison.key_insights:
                print(f"   - {len(comparison.key_insights)} insights generated")
            if comparison.recommendations:
                print(f"   - {len(comparison.recommendations)} recommendations")
        except Exception as e:
            print(f"❌ Comparison failed: {str(e)}")
        
        print("\n" + "-" * 50)
        print("Testing complete!")

if __name__ == "__main__":
    test_competitor_analysis()