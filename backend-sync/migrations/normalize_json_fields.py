"""
Normalize JSON fields into proper relational tables

This migration converts JSON columns into normalized relational tables for better
query performance and data integrity.

Revision ID: normalize_json_fields_001
Revises: add_missing_indexes_001
Create Date: 2025-01-25
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import json
from datetime import datetime

# Revision identifiers
revision = 'normalize_json_fields_001'
down_revision = 'add_missing_indexes_001'
branch_labels = None
depends_on = None


def upgrade():
    """Create normalized tables for JSON data"""
    
    # 1. Create normalized tables for CompetitorAnalysis data
    
    # Top Hashtags table
    op.create_table(
        'competitor_top_hashtags',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('competitor_id', sa.Integer(), sa.ForeignKey('competitors.id'), nullable=False),
        sa.Column('hashtag', sa.String(100), nullable=False),
        sa.Column('usage_count', sa.Integer(), default=0),
        sa.Column('avg_engagement', sa.Float(), default=0.0),
        sa.Column('rank', sa.Integer()),
        sa.Column('analysis_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow)
    )
    
    # Create indexes for competitor_top_hashtags
    op.create_index('ix_competitor_top_hashtags_competitor_id', 'competitor_top_hashtags', ['competitor_id'])
    op.create_index('ix_competitor_top_hashtags_hashtag', 'competitor_top_hashtags', ['hashtag'])
    op.create_index('ix_competitor_top_hashtags_analysis_date', 'competitor_top_hashtags', ['analysis_date'])
    op.create_index('ix_competitor_top_hashtags_comp_date', 'competitor_top_hashtags', ['competitor_id', 'analysis_date'])
    
    # Top Posts table
    op.create_table(
        'competitor_top_posts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('competitor_id', sa.Integer(), sa.ForeignKey('competitors.id'), nullable=False),
        sa.Column('post_id', sa.String(100), nullable=False),
        sa.Column('platform', sa.String(20), nullable=False),
        sa.Column('content_type', sa.String(50)),
        sa.Column('caption', sa.Text()),
        sa.Column('media_url', sa.String(500)),
        sa.Column('likes', sa.Integer(), default=0),
        sa.Column('comments', sa.Integer(), default=0),
        sa.Column('shares', sa.Integer(), default=0),
        sa.Column('engagement_rate', sa.Float(), default=0.0),
        sa.Column('posted_at', sa.DateTime()),
        sa.Column('rank', sa.Integer()),
        sa.Column('analysis_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow)
    )
    
    # Create indexes for competitor_top_posts
    op.create_index('ix_competitor_top_posts_competitor_id', 'competitor_top_posts', ['competitor_id'])
    op.create_index('ix_competitor_top_posts_post_id', 'competitor_top_posts', ['post_id'])
    op.create_index('ix_competitor_top_posts_platform', 'competitor_top_posts', ['platform'])
    op.create_index('ix_competitor_top_posts_analysis_date', 'competitor_top_posts', ['analysis_date'])
    op.create_index('ix_competitor_top_posts_engagement_rate', 'competitor_top_posts', ['engagement_rate'])
    
    # Audience Demographics table
    op.create_table(
        'competitor_audience_demographics',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('competitor_id', sa.Integer(), sa.ForeignKey('competitors.id'), nullable=False),
        sa.Column('demographic_type', sa.String(50), nullable=False),  # age_group, gender, location, interest
        sa.Column('demographic_value', sa.String(100), nullable=False),
        sa.Column('percentage', sa.Float(), default=0.0),
        sa.Column('count', sa.Integer(), default=0),
        sa.Column('analysis_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow)
    )
    
    # Create indexes for competitor_audience_demographics
    op.create_index('ix_competitor_audience_demographics_competitor_id', 'competitor_audience_demographics', ['competitor_id'])
    op.create_index('ix_competitor_audience_demographics_type', 'competitor_audience_demographics', ['demographic_type'])
    op.create_index('ix_competitor_audience_demographics_analysis_date', 'competitor_audience_demographics', ['analysis_date'])
    
    # 2. Create normalized tables for HashtagStrategy data
    
    # Trending Hashtags table
    op.create_table(
        'trending_hashtags',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('client_id', sa.Integer(), sa.ForeignKey('clients.id'), nullable=False),
        sa.Column('hashtag', sa.String(100), nullable=False),
        sa.Column('trend_score', sa.Float(), default=0.0),
        sa.Column('growth_rate', sa.Float(), default=0.0),
        sa.Column('category', sa.String(50)),  # kuwait, ramadan, national_day, etc.
        sa.Column('avg_engagement', sa.Float(), default=0.0),
        sa.Column('post_count', sa.Integer(), default=0),
        sa.Column('is_seasonal', sa.Boolean(), default=False),
        sa.Column('peak_time', sa.Time()),
        sa.Column('valid_from', sa.DateTime(), nullable=False),
        sa.Column('valid_until', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow)
    )
    
    # Create indexes for trending_hashtags
    op.create_index('ix_trending_hashtags_client_id', 'trending_hashtags', ['client_id'])
    op.create_index('ix_trending_hashtags_hashtag', 'trending_hashtags', ['hashtag'])
    op.create_index('ix_trending_hashtags_trend_score', 'trending_hashtags', ['trend_score'])
    op.create_index('ix_trending_hashtags_category', 'trending_hashtags', ['category'])
    op.create_index('ix_trending_hashtags_valid_dates', 'trending_hashtags', ['valid_from', 'valid_until'])
    
    # Recommended Hashtag Combinations table
    op.create_table(
        'hashtag_combinations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('client_id', sa.Integer(), sa.ForeignKey('clients.id'), nullable=False),
        sa.Column('combination_name', sa.String(200)),
        sa.Column('content_type', sa.String(50)),  # product, promotion, cultural, etc.
        sa.Column('expected_reach', sa.Integer(), default=0),
        sa.Column('expected_engagement_rate', sa.Float(), default=0.0),
        sa.Column('confidence_score', sa.Float(), default=0.0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('valid_from', sa.DateTime(), nullable=False),
        sa.Column('valid_until', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('last_used', sa.DateTime())
    )
    
    # Create indexes for hashtag_combinations
    op.create_index('ix_hashtag_combinations_client_id', 'hashtag_combinations', ['client_id'])
    op.create_index('ix_hashtag_combinations_content_type', 'hashtag_combinations', ['content_type'])
    op.create_index('ix_hashtag_combinations_confidence_score', 'hashtag_combinations', ['confidence_score'])
    op.create_index('ix_hashtag_combinations_active', 'hashtag_combinations', ['is_active'])
    
    # Hashtag Combination Items table (many-to-many relationship)
    op.create_table(
        'hashtag_combination_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('combination_id', sa.Integer(), sa.ForeignKey('hashtag_combinations.id'), nullable=False),
        sa.Column('hashtag', sa.String(100), nullable=False),
        sa.Column('position', sa.Integer(), default=0),  # Order in the combination
        sa.Column('is_primary', sa.Boolean(), default=False)  # Primary vs supporting hashtag
    )
    
    # Create indexes for hashtag_combination_items
    op.create_index('ix_hashtag_combination_items_combination_id', 'hashtag_combination_items', ['combination_id'])
    op.create_index('ix_hashtag_combination_items_hashtag', 'hashtag_combination_items', ['hashtag'])
    
    # 3. Add backward compatibility columns (temporary, for migration period)
    # These will store the JSON data during transition
    op.add_column('competitors', sa.Column('top_hashtags_migrated', sa.Boolean(), server_default='false'))
    op.add_column('competitors', sa.Column('top_posts_migrated', sa.Boolean(), server_default='false'))
    op.add_column('competitors', sa.Column('audience_demographics_migrated', sa.Boolean(), server_default='false'))
    
    # Note: The actual data migration will be handled by the utility script
    # to avoid timeout issues with large datasets


def downgrade():
    """Drop normalized tables and restore JSON columns"""
    
    # Remove backward compatibility columns
    op.drop_column('competitors', 'audience_demographics_migrated')
    op.drop_column('competitors', 'top_posts_migrated')
    op.drop_column('competitors', 'top_hashtags_migrated')
    
    # Drop indexes and tables in reverse order
    
    # Drop hashtag_combination_items indexes and table
    op.drop_index('ix_hashtag_combination_items_hashtag', 'hashtag_combination_items')
    op.drop_index('ix_hashtag_combination_items_combination_id', 'hashtag_combination_items')
    op.drop_table('hashtag_combination_items')
    
    # Drop hashtag_combinations indexes and table
    op.drop_index('ix_hashtag_combinations_active', 'hashtag_combinations')
    op.drop_index('ix_hashtag_combinations_confidence_score', 'hashtag_combinations')
    op.drop_index('ix_hashtag_combinations_content_type', 'hashtag_combinations')
    op.drop_index('ix_hashtag_combinations_client_id', 'hashtag_combinations')
    op.drop_table('hashtag_combinations')
    
    # Drop trending_hashtags indexes and table
    op.drop_index('ix_trending_hashtags_valid_dates', 'trending_hashtags')
    op.drop_index('ix_trending_hashtags_category', 'trending_hashtags')
    op.drop_index('ix_trending_hashtags_trend_score', 'trending_hashtags')
    op.drop_index('ix_trending_hashtags_hashtag', 'trending_hashtags')
    op.drop_index('ix_trending_hashtags_client_id', 'trending_hashtags')
    op.drop_table('trending_hashtags')
    
    # Drop competitor_audience_demographics indexes and table
    op.drop_index('ix_competitor_audience_demographics_analysis_date', 'competitor_audience_demographics')
    op.drop_index('ix_competitor_audience_demographics_type', 'competitor_audience_demographics')
    op.drop_index('ix_competitor_audience_demographics_competitor_id', 'competitor_audience_demographics')
    op.drop_table('competitor_audience_demographics')
    
    # Drop competitor_top_posts indexes and table
    op.drop_index('ix_competitor_top_posts_engagement_rate', 'competitor_top_posts')
    op.drop_index('ix_competitor_top_posts_analysis_date', 'competitor_top_posts')
    op.drop_index('ix_competitor_top_posts_platform', 'competitor_top_posts')
    op.drop_index('ix_competitor_top_posts_post_id', 'competitor_top_posts')
    op.drop_index('ix_competitor_top_posts_competitor_id', 'competitor_top_posts')
    op.drop_table('competitor_top_posts')
    
    # Drop competitor_top_hashtags indexes and table
    op.drop_index('ix_competitor_top_hashtags_comp_date', 'competitor_top_hashtags')
    op.drop_index('ix_competitor_top_hashtags_analysis_date', 'competitor_top_hashtags')
    op.drop_index('ix_competitor_top_hashtags_hashtag', 'competitor_top_hashtags')
    op.drop_index('ix_competitor_top_hashtags_competitor_id', 'competitor_top_hashtags')
    op.drop_table('competitor_top_hashtags')