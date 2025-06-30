"""
Add missing indexes for performance optimization

This migration adds indexes to foreign keys and frequently queried columns
to improve database performance.
"""

from alembic import op
import sqlalchemy as sa

# Revision identifiers
revision = 'add_missing_indexes_001'
down_revision = 'initial_migration'  # Update this to point to the actual previous migration
branch_labels = None
depends_on = None


def upgrade():
    """Add indexes to improve query performance"""
    
    # Users table indexes
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_role', 'users', ['role'])
    op.create_index('ix_users_is_active', 'users', ['is_active'])
    
    # Clients table indexes
    op.create_index('ix_clients_user_id', 'clients', ['user_id'])
    op.create_index('ix_clients_admin_id', 'clients', ['admin_id'])
    op.create_index('ix_clients_business_name', 'clients', ['business_name'])
    op.create_index('ix_clients_is_active', 'clients', ['is_active'])
    op.create_index('ix_clients_subscription_status', 'clients', ['subscription_status'])
    
    # Social Media Accounts indexes
    op.create_index('ix_social_media_accounts_client_id', 'social_media_accounts', ['client_id'])
    op.create_index('ix_social_media_accounts_platform', 'social_media_accounts', ['platform'])
    op.create_index('ix_social_media_accounts_is_active', 'social_media_accounts', ['is_active'])
    
    # Scheduled Posts indexes
    op.create_index('ix_scheduled_posts_client_id', 'scheduled_posts', ['client_id'])
    op.create_index('ix_scheduled_posts_scheduled_time', 'scheduled_posts', ['scheduled_time'])
    op.create_index('ix_scheduled_posts_status', 'scheduled_posts', ['status'])
    op.create_index('ix_scheduled_posts_created_at', 'scheduled_posts', ['created_at'])
    
    # Post Analytics indexes
    op.create_index('ix_post_analytics_post_id', 'post_analytics', ['post_id'])
    op.create_index('ix_post_analytics_platform', 'post_analytics', ['platform'])
    op.create_index('ix_post_analytics_recorded_at', 'post_analytics', ['recorded_at'])
    
    # Content Templates indexes
    op.create_index('ix_content_templates_client_id', 'content_templates', ['client_id'])
    op.create_index('ix_content_templates_category', 'content_templates', ['category'])
    op.create_index('ix_content_templates_is_active', 'content_templates', ['is_active'])
    
    # Campaigns indexes
    op.create_index('ix_campaigns_client_id', 'campaigns', ['client_id'])
    op.create_index('ix_campaigns_status', 'campaigns', ['status'])
    op.create_index('ix_campaigns_start_date_end_date', 'campaigns', ['start_date', 'end_date'])
    
    # AI Content History indexes
    op.create_index('ix_ai_content_history_client_id', 'ai_content_history', ['client_id'])
    op.create_index('ix_ai_content_history_created_at', 'ai_content_history', ['created_at'])
    
    # Competitors indexes
    op.create_index('ix_competitors_client_id', 'competitors', ['client_id'])
    op.create_index('ix_competitors_platform', 'competitors', ['platform'])
    op.create_index('ix_competitors_is_active', 'competitors', ['is_active'])
    
    # Competitor Analysis indexes
    op.create_index('ix_competitor_analysis_competitor_id', 'competitor_analysis', ['competitor_id'])
    op.create_index('ix_competitor_analysis_analysis_date', 'competitor_analysis', ['analysis_date'])
    
    # Hashtag Performance indexes
    op.create_index('ix_hashtag_performance_hashtag', 'hashtag_performance', ['hashtag'])
    op.create_index('ix_hashtag_performance_client_id', 'hashtag_performance', ['client_id'])
    op.create_index('ix_hashtag_performance_post_id', 'hashtag_performance', ['post_id'])
    op.create_index('ix_hashtag_performance_measured_at', 'hashtag_performance', ['measured_at'])
    
    # Unified Inbox Messages indexes
    op.create_index('ix_unified_inbox_messages_client_id', 'unified_inbox_messages', ['client_id'])
    op.create_index('ix_unified_inbox_messages_platform', 'unified_inbox_messages', ['platform'])
    op.create_index('ix_unified_inbox_messages_is_read', 'unified_inbox_messages', ['is_read'])
    op.create_index('ix_unified_inbox_messages_is_responded', 'unified_inbox_messages', ['is_responded'])
    op.create_index('ix_unified_inbox_messages_received_at', 'unified_inbox_messages', ['received_at'])
    op.create_index('ix_unified_inbox_messages_sentiment', 'unified_inbox_messages', ['sentiment'])
    
    # Customer Profiles indexes
    op.create_index('ix_customer_profiles_client_id', 'customer_profiles', ['client_id'])
    op.create_index('ix_customer_profiles_instagram_username', 'customer_profiles', ['instagram_username'])
    op.create_index('ix_customer_profiles_snapchat_username', 'customer_profiles', ['snapchat_username'])
    
    # Composite indexes for common queries
    op.create_index('ix_scheduled_posts_client_status', 'scheduled_posts', ['client_id', 'status'])
    op.create_index('ix_post_analytics_post_platform', 'post_analytics', ['post_id', 'platform'])
    op.create_index('ix_unified_inbox_client_unread', 'unified_inbox_messages', ['client_id', 'is_read'])
    
    # Payment history indexes
    op.create_index('ix_payment_history_client_id', 'payment_history', ['client_id'])
    op.create_index('ix_payment_history_status', 'payment_history', ['status'])
    op.create_index('ix_payment_history_created_at', 'payment_history', ['created_at'])


def downgrade():
    """Remove indexes"""
    
    # Remove all indexes in reverse order
    op.drop_index('ix_payment_history_created_at', 'payment_history')
    op.drop_index('ix_payment_history_status', 'payment_history')
    op.drop_index('ix_payment_history_client_id', 'payment_history')
    
    op.drop_index('ix_unified_inbox_client_unread', 'unified_inbox_messages')
    op.drop_index('ix_post_analytics_post_platform', 'post_analytics')
    op.drop_index('ix_scheduled_posts_client_status', 'scheduled_posts')
    
    op.drop_index('ix_customer_profiles_snapchat_username', 'customer_profiles')
    op.drop_index('ix_customer_profiles_instagram_username', 'customer_profiles')
    op.drop_index('ix_customer_profiles_client_id', 'customer_profiles')
    
    op.drop_index('ix_unified_inbox_messages_sentiment', 'unified_inbox_messages')
    op.drop_index('ix_unified_inbox_messages_received_at', 'unified_inbox_messages')
    op.drop_index('ix_unified_inbox_messages_is_responded', 'unified_inbox_messages')
    op.drop_index('ix_unified_inbox_messages_is_read', 'unified_inbox_messages')
    op.drop_index('ix_unified_inbox_messages_platform', 'unified_inbox_messages')
    op.drop_index('ix_unified_inbox_messages_client_id', 'unified_inbox_messages')
    
    op.drop_index('ix_hashtag_performance_measured_at', 'hashtag_performance')
    op.drop_index('ix_hashtag_performance_post_id', 'hashtag_performance')
    op.drop_index('ix_hashtag_performance_client_id', 'hashtag_performance')
    op.drop_index('ix_hashtag_performance_hashtag', 'hashtag_performance')
    
    op.drop_index('ix_competitor_analysis_analysis_date', 'competitor_analysis')
    op.drop_index('ix_competitor_analysis_competitor_id', 'competitor_analysis')
    
    op.drop_index('ix_competitors_is_active', 'competitors')
    op.drop_index('ix_competitors_platform', 'competitors')
    op.drop_index('ix_competitors_client_id', 'competitors')
    
    op.drop_index('ix_ai_content_history_created_at', 'ai_content_history')
    op.drop_index('ix_ai_content_history_client_id', 'ai_content_history')
    
    op.drop_index('ix_campaigns_start_date_end_date', 'campaigns')
    op.drop_index('ix_campaigns_status', 'campaigns')
    op.drop_index('ix_campaigns_client_id', 'campaigns')
    
    op.drop_index('ix_content_templates_is_active', 'content_templates')
    op.drop_index('ix_content_templates_category', 'content_templates')
    op.drop_index('ix_content_templates_client_id', 'content_templates')
    
    op.drop_index('ix_post_analytics_recorded_at', 'post_analytics')
    op.drop_index('ix_post_analytics_platform', 'post_analytics')
    op.drop_index('ix_post_analytics_post_id', 'post_analytics')
    
    op.drop_index('ix_scheduled_posts_created_at', 'scheduled_posts')
    op.drop_index('ix_scheduled_posts_status', 'scheduled_posts')
    op.drop_index('ix_scheduled_posts_scheduled_time', 'scheduled_posts')
    op.drop_index('ix_scheduled_posts_client_id', 'scheduled_posts')
    
    op.drop_index('ix_social_media_accounts_is_active', 'social_media_accounts')
    op.drop_index('ix_social_media_accounts_platform', 'social_media_accounts')
    op.drop_index('ix_social_media_accounts_client_id', 'social_media_accounts')
    
    op.drop_index('ix_clients_subscription_status', 'clients')
    op.drop_index('ix_clients_is_active', 'clients')
    op.drop_index('ix_clients_business_name', 'clients')
    op.drop_index('ix_clients_admin_id', 'clients')
    op.drop_index('ix_clients_user_id', 'clients')
    
    op.drop_index('ix_users_is_active', 'users')
    op.drop_index('ix_users_role', 'users')
    op.drop_index('ix_users_email', 'users')