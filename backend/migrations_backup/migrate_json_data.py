"""
Utility script to migrate existing JSON data to normalized tables

This script handles the data migration from JSON columns to the new normalized
relational tables. It processes data in batches to avoid memory issues and
provides progress tracking.

Usage:
    python migrate_json_data.py [--batch-size=100] [--dry-run]
"""

import os
import sys
import json
import argparse
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from models import db
from models.normalized_models import (
    CompetitorTopHashtag, CompetitorTopPost, CompetitorAudienceDemographic,
    TrendingHashtag, HashtagCombination, HashtagCombinationItem
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JSONDataMigrator:
    """Handle migration of JSON data to normalized tables"""
    
    def __init__(self, db_url=None, batch_size=100, dry_run=False):
        self.db_url = db_url or Config.SQLALCHEMY_DATABASE_URI
        self.batch_size = batch_size
        self.dry_run = dry_run
        self.engine = create_engine(self.db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.stats = {
            'competitor_hashtags': 0,
            'competitor_posts': 0,
            'competitor_demographics': 0,
            'trending_hashtags': 0,
            'hashtag_combinations': 0,
            'errors': 0
        }
    
    def migrate_all(self):
        """Run all migrations"""
        logger.info(f"Starting JSON data migration (dry_run={self.dry_run})")
        
        try:
            self.migrate_competitor_analysis_data()
            self.migrate_hashtag_strategy_data()
            
            logger.info("Migration completed successfully!")
            self.print_stats()
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            raise
    
    def migrate_competitor_analysis_data(self):
        """Migrate CompetitorAnalysis JSON fields"""
        logger.info("Migrating CompetitorAnalysis data...")
        session = self.Session()
        
        try:
            # Get all competitor analysis records with JSON data
            query = text("""
                SELECT ca.id, ca.competitor_id, ca.analysis_date,
                       ca.top_hashtags, ca.top_posts, ca.audience_demographics,
                       c.top_hashtags_migrated, c.top_posts_migrated, c.audience_demographics_migrated
                FROM competitor_analysis ca
                JOIN competitors c ON ca.competitor_id = c.id
                WHERE (ca.top_hashtags IS NOT NULL OR 
                       ca.top_posts IS NOT NULL OR 
                       ca.audience_demographics IS NOT NULL)
                AND (c.top_hashtags_migrated = false OR 
                     c.top_posts_migrated = false OR 
                     c.audience_demographics_migrated = false)
                ORDER BY ca.id
            """)
            
            result = session.execute(query)
            records = result.fetchall()
            total_records = len(records)
            logger.info(f"Found {total_records} CompetitorAnalysis records to migrate")
            
            for i in range(0, total_records, self.batch_size):
                batch = records[i:i + self.batch_size]
                self._process_competitor_batch(session, batch)
                
                if not self.dry_run:
                    session.commit()
                    
                logger.info(f"Processed {min(i + self.batch_size, total_records)}/{total_records} records")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error migrating competitor analysis data: {str(e)}")
            self.stats['errors'] += 1
            raise
        finally:
            session.close()
    
    def _process_competitor_batch(self, session, batch):
        """Process a batch of competitor analysis records"""
        for record in batch:
            try:
                analysis_id = record.id
                competitor_id = record.competitor_id
                analysis_date = record.analysis_date
                
                # Migrate top hashtags
                if record.top_hashtags and not record.top_hashtags_migrated:
                    self._migrate_top_hashtags(session, competitor_id, analysis_date, record.top_hashtags)
                
                # Migrate top posts
                if record.top_posts and not record.top_posts_migrated:
                    self._migrate_top_posts(session, competitor_id, analysis_date, record.top_posts)
                
                # Migrate audience demographics
                if record.audience_demographics and not record.audience_demographics_migrated:
                    self._migrate_audience_demographics(session, competitor_id, analysis_date, 
                                                       record.audience_demographics)
                
                # Mark as migrated
                if not self.dry_run:
                    update_query = text("""
                        UPDATE competitors 
                        SET top_hashtags_migrated = true,
                            top_posts_migrated = true,
                            audience_demographics_migrated = true
                        WHERE id = :competitor_id
                    """)
                    session.execute(update_query, {'competitor_id': competitor_id})
                    
            except Exception as e:
                logger.error(f"Error processing competitor analysis {analysis_id}: {str(e)}")
                self.stats['errors'] += 1
    
    def _migrate_top_hashtags(self, session, competitor_id, analysis_date, json_data):
        """Migrate top hashtags JSON to normalized table"""
        try:
            hashtags = json.loads(json_data) if isinstance(json_data, str) else json_data
            
            for idx, hashtag_data in enumerate(hashtags):
                if self.dry_run:
                    logger.debug(f"Would insert hashtag: {hashtag_data}")
                else:
                    # Handle different possible JSON structures
                    if isinstance(hashtag_data, dict):
                        hashtag = CompetitorTopHashtag(
                            competitor_id=competitor_id,
                            hashtag=hashtag_data.get('hashtag', hashtag_data.get('name', '')),
                            usage_count=hashtag_data.get('usage_count', hashtag_data.get('count', 0)),
                            avg_engagement=hashtag_data.get('avg_engagement', hashtag_data.get('engagement', 0.0)),
                            rank=hashtag_data.get('rank', idx + 1),
                            analysis_date=analysis_date
                        )
                    else:
                        # Simple string hashtag
                        hashtag = CompetitorTopHashtag(
                            competitor_id=competitor_id,
                            hashtag=str(hashtag_data),
                            rank=idx + 1,
                            analysis_date=analysis_date
                        )
                    
                    session.add(hashtag)
                    self.stats['competitor_hashtags'] += 1
                    
        except Exception as e:
            logger.error(f"Error migrating top hashtags: {str(e)}")
            self.stats['errors'] += 1
    
    def _migrate_top_posts(self, session, competitor_id, analysis_date, json_data):
        """Migrate top posts JSON to normalized table"""
        try:
            posts = json.loads(json_data) if isinstance(json_data, str) else json_data
            
            for idx, post_data in enumerate(posts):
                if isinstance(post_data, dict) and not self.dry_run:
                    post = CompetitorTopPost(
                        competitor_id=competitor_id,
                        post_id=post_data.get('post_id', post_data.get('id', f'unknown_{idx}')),
                        platform=post_data.get('platform', 'instagram'),
                        content_type=post_data.get('content_type', post_data.get('type', 'unknown')),
                        caption=post_data.get('caption', '')[:1000],  # Truncate long captions
                        media_url=post_data.get('media_url', post_data.get('image_url', '')),
                        likes=post_data.get('likes', 0),
                        comments=post_data.get('comments', 0),
                        shares=post_data.get('shares', 0),
                        engagement_rate=post_data.get('engagement_rate', 0.0),
                        posted_at=self._parse_datetime(post_data.get('posted_at')),
                        rank=post_data.get('rank', idx + 1),
                        analysis_date=analysis_date
                    )
                    session.add(post)
                    self.stats['competitor_posts'] += 1
                    
        except Exception as e:
            logger.error(f"Error migrating top posts: {str(e)}")
            self.stats['errors'] += 1
    
    def _migrate_audience_demographics(self, session, competitor_id, analysis_date, json_data):
        """Migrate audience demographics JSON to normalized table"""
        try:
            demographics = json.loads(json_data) if isinstance(json_data, str) else json_data
            
            # Handle different JSON structures
            if isinstance(demographics, dict):
                for demo_type, demo_values in demographics.items():
                    if isinstance(demo_values, dict):
                        for value, data in demo_values.items():
                            if not self.dry_run:
                                if isinstance(data, dict):
                                    demographic = CompetitorAudienceDemographic(
                                        competitor_id=competitor_id,
                                        demographic_type=demo_type,
                                        demographic_value=value,
                                        percentage=data.get('percentage', 0.0),
                                        count=data.get('count', 0),
                                        analysis_date=analysis_date
                                    )
                                else:
                                    # Simple percentage value
                                    demographic = CompetitorAudienceDemographic(
                                        competitor_id=competitor_id,
                                        demographic_type=demo_type,
                                        demographic_value=value,
                                        percentage=float(data),
                                        analysis_date=analysis_date
                                    )
                                session.add(demographic)
                                self.stats['competitor_demographics'] += 1
                                
        except Exception as e:
            logger.error(f"Error migrating audience demographics: {str(e)}")
            self.stats['errors'] += 1
    
    def migrate_hashtag_strategy_data(self):
        """Migrate HashtagStrategy JSON fields"""
        logger.info("Migrating HashtagStrategy data...")
        session = self.Session()
        
        try:
            # Get all hashtag strategy records with JSON data
            query = text("""
                SELECT hs.id, hs.client_id, hs.trending_hashtags, hs.recommended_combinations
                FROM hashtag_strategies hs
                WHERE hs.trending_hashtags IS NOT NULL OR hs.recommended_combinations IS NOT NULL
                ORDER BY hs.id
            """)
            
            result = session.execute(query)
            records = result.fetchall()
            total_records = len(records)
            logger.info(f"Found {total_records} HashtagStrategy records to migrate")
            
            for i in range(0, total_records, self.batch_size):
                batch = records[i:i + self.batch_size]
                self._process_hashtag_strategy_batch(session, batch)
                
                if not self.dry_run:
                    session.commit()
                    
                logger.info(f"Processed {min(i + self.batch_size, total_records)}/{total_records} records")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error migrating hashtag strategy data: {str(e)}")
            self.stats['errors'] += 1
            raise
        finally:
            session.close()
    
    def _process_hashtag_strategy_batch(self, session, batch):
        """Process a batch of hashtag strategy records"""
        for record in batch:
            try:
                strategy_id = record.id
                client_id = record.client_id
                
                # Migrate trending hashtags
                if record.trending_hashtags:
                    self._migrate_trending_hashtags(session, client_id, record.trending_hashtags)
                
                # Migrate recommended combinations
                if record.recommended_combinations:
                    self._migrate_hashtag_combinations(session, client_id, record.recommended_combinations)
                    
            except Exception as e:
                logger.error(f"Error processing hashtag strategy {strategy_id}: {str(e)}")
                self.stats['errors'] += 1
    
    def _migrate_trending_hashtags(self, session, client_id, json_data):
        """Migrate trending hashtags JSON to normalized table"""
        try:
            hashtags = json.loads(json_data) if isinstance(json_data, str) else json_data
            
            for hashtag_data in hashtags:
                if isinstance(hashtag_data, dict) and not self.dry_run:
                    trending = TrendingHashtag(
                        client_id=client_id,
                        hashtag=hashtag_data.get('hashtag', hashtag_data.get('name', '')),
                        trend_score=hashtag_data.get('trend_score', hashtag_data.get('score', 0.0)),
                        growth_rate=hashtag_data.get('growth_rate', 0.0),
                        category=hashtag_data.get('category', 'general'),
                        avg_engagement=hashtag_data.get('avg_engagement', 0.0),
                        post_count=hashtag_data.get('post_count', 0),
                        is_seasonal=hashtag_data.get('is_seasonal', False),
                        valid_from=datetime.utcnow(),
                        valid_until=self._parse_datetime(hashtag_data.get('expires_at'))
                    )
                    session.add(trending)
                    self.stats['trending_hashtags'] += 1
                    
        except Exception as e:
            logger.error(f"Error migrating trending hashtags: {str(e)}")
            self.stats['errors'] += 1
    
    def _migrate_hashtag_combinations(self, session, client_id, json_data):
        """Migrate hashtag combinations JSON to normalized tables"""
        try:
            combinations = json.loads(json_data) if isinstance(json_data, str) else json_data
            
            for combo_data in combinations:
                if isinstance(combo_data, dict) and not self.dry_run:
                    # Create combination record
                    combination = HashtagCombination(
                        client_id=client_id,
                        combination_name=combo_data.get('name', 'Unnamed Combination'),
                        content_type=combo_data.get('content_type', combo_data.get('type', 'general')),
                        expected_reach=combo_data.get('expected_reach', 0),
                        expected_engagement_rate=combo_data.get('expected_engagement_rate', 0.0),
                        confidence_score=combo_data.get('confidence_score', combo_data.get('score', 0.0)),
                        valid_from=datetime.utcnow()
                    )
                    session.add(combination)
                    session.flush()  # Get the ID
                    
                    # Add individual hashtags
                    hashtags = combo_data.get('hashtags', [])
                    primary_hashtags = combo_data.get('primary_hashtags', [])
                    
                    for idx, hashtag in enumerate(hashtags):
                        if isinstance(hashtag, str):
                            item = HashtagCombinationItem(
                                combination_id=combination.id,
                                hashtag=hashtag,
                                position=idx,
                                is_primary=hashtag in primary_hashtags
                            )
                            session.add(item)
                    
                    self.stats['hashtag_combinations'] += 1
                    
        except Exception as e:
            logger.error(f"Error migrating hashtag combinations: {str(e)}")
            self.stats['errors'] += 1
    
    def _parse_datetime(self, date_str):
        """Parse datetime string to datetime object"""
        if not date_str:
            return None
        
        try:
            # Try common datetime formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return None
        except:
            return None
    
    def print_stats(self):
        """Print migration statistics"""
        logger.info("\n=== Migration Statistics ===")
        logger.info(f"Competitor Top Hashtags: {self.stats['competitor_hashtags']}")
        logger.info(f"Competitor Top Posts: {self.stats['competitor_posts']}")
        logger.info(f"Competitor Demographics: {self.stats['competitor_demographics']}")
        logger.info(f"Trending Hashtags: {self.stats['trending_hashtags']}")
        logger.info(f"Hashtag Combinations: {self.stats['hashtag_combinations']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info("===========================\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Migrate JSON data to normalized tables')
    parser.add_argument('--batch-size', type=int, default=100, 
                       help='Number of records to process in each batch')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Run without making actual changes')
    parser.add_argument('--db-url', type=str, help='Database URL (overrides config)')
    
    args = parser.parse_args()
    
    # Create and run migrator
    migrator = JSONDataMigrator(
        db_url=args.db_url,
        batch_size=args.batch_size,
        dry_run=args.dry_run
    )
    
    try:
        migrator.migrate_all()
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()