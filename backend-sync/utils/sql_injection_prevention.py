"""
SQL Injection Prevention Utilities and Examples
This module demonstrates safe database query practices
"""

from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from models import db


class SafeQueryBuilder:
    """
    Helper class for building safe SQL queries
    Always use SQLAlchemy ORM when possible, but if raw SQL is needed,
    this class provides safe patterns.
    """
    
    @staticmethod
    def safe_search_users(session: Session, search_term: str, limit: int = 50) -> List[Dict]:
        """
        Safe user search using SQLAlchemy ORM
        
        GOOD: Uses ORM with proper escaping
        """
        from models import User
        
        # ORM automatically escapes the search term
        users = User.query.filter(
            db.or_(
                User.username.ilike(f'%{search_term}%'),
                User.email.ilike(f'%{search_term}%'),
                User.full_name.ilike(f'%{search_term}%')
            )
        ).limit(limit).all()
        
        return [user.to_dict() for user in users]
    
    @staticmethod
    def safe_raw_query_example(session: Session, user_id: int, status: str) -> List[Dict]:
        """
        Example of safe raw SQL query using parameters
        
        GOOD: Uses parameterized queries
        """
        # Using named parameters (recommended)
        query = text("""
            SELECT p.id, p.title, p.created_at
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE u.id = :user_id 
              AND p.status = :status
            ORDER BY p.created_at DESC
            LIMIT :limit
        """)
        
        result = session.execute(query, {
            'user_id': user_id,
            'status': status,
            'limit': 50
        })
        
        return [dict(row) for row in result]
    
    @staticmethod
    def safe_dynamic_filter(session: Session, filters: Dict[str, Any]) -> List[Any]:
        """
        Build dynamic queries safely using SQLAlchemy
        
        GOOD: Builds query programmatically without string concatenation
        """
        from models import Post
        
        query = Post.query
        
        # Apply filters dynamically but safely
        if 'status' in filters:
            query = query.filter(Post.status == filters['status'])
        
        if 'user_id' in filters:
            query = query.filter(Post.user_id == filters['user_id'])
        
        if 'date_from' in filters:
            query = query.filter(Post.created_at >= filters['date_from'])
        
        if 'date_to' in filters:
            query = query.filter(Post.created_at <= filters['date_to'])
        
        if 'search' in filters:
            search_term = f"%{filters['search']}%"
            query = query.filter(
                db.or_(
                    Post.title.ilike(search_term),
                    Post.content.ilike(search_term)
                )
            )
        
        return query.all()
    
    @staticmethod
    def safe_bulk_insert(session: Session, records: List[Dict]) -> int:
        """
        Safe bulk insert operation
        
        GOOD: Uses SQLAlchemy's bulk operations
        """
        from models import Post
        
        # Validate and sanitize data before insertion
        clean_records = []
        for record in records:
            clean_record = {
                'title': str(record.get('title', ''))[:200],
                'content': str(record.get('content', '')),
                'user_id': int(record.get('user_id', 0)),
                'status': str(record.get('status', 'draft'))
            }
            clean_records.append(clean_record)
        
        # Bulk insert using SQLAlchemy
        session.bulk_insert_mappings(Post, clean_records)
        session.commit()
        
        return len(clean_records)
    
    @staticmethod
    def safe_column_selection(allowed_columns: List[str], requested_columns: List[str]) -> List[str]:
        """
        Safely filter requested columns against allowed list
        
        Prevents SQL injection via column names
        """
        # Only return columns that are in the allowed list
        return [col for col in requested_columns if col in allowed_columns]


class UnsafeExamples:
    """
    DO NOT USE THESE PATTERNS!
    These examples show what NOT to do.
    """
    
    @staticmethod
    def unsafe_query_example(email: str):
        """
        BAD: Direct string concatenation - vulnerable to SQL injection
        
        NEVER DO THIS!
        """
        # This is vulnerable to SQL injection
        # query = f"SELECT * FROM users WHERE email = '{email}'"
        # db.session.execute(query)  # DON'T DO THIS!
        pass
    
    @staticmethod
    def unsafe_dynamic_query(table_name: str, column: str, value: str):
        """
        BAD: Dynamic query building with string formatting
        
        NEVER DO THIS!
        """
        # This is extremely dangerous
        # query = f"SELECT * FROM {table_name} WHERE {column} = '{value}'"
        # db.session.execute(query)  # DON'T DO THIS!
        pass


def validate_sql_identifier(identifier: str, allowed_identifiers: List[str]) -> str:
    """
    Validate SQL identifiers (table names, column names) against whitelist
    
    Use this when you absolutely must use dynamic identifiers
    """
    if identifier not in allowed_identifiers:
        raise ValueError(f"Invalid identifier: {identifier}")
    return identifier


def escape_like_pattern(pattern: str) -> str:
    """
    Escape special characters in LIKE patterns
    
    Use this when building LIKE queries with user input
    """
    # Escape special LIKE characters
    pattern = pattern.replace('\\', '\\\\')
    pattern = pattern.replace('%', '\\%')
    pattern = pattern.replace('_', '\\_')
    return pattern


# Configuration for query complexity limits
QUERY_LIMITS = {
    'max_results': 1000,
    'max_join_depth': 3,
    'max_subqueries': 2,
    'timeout_seconds': 30
}


def apply_query_limits(query):
    """
    Apply security limits to queries to prevent resource exhaustion
    """
    # Always apply a maximum limit
    if not query._limit:
        query = query.limit(QUERY_LIMITS['max_results'])
    
    return query


# Example usage in routes
"""
from utils.sql_injection_prevention import SafeQueryBuilder

@app.route('/api/search/users')
@jwt_required()
def search_users():
    search_term = request.args.get('q', '')
    
    # Safe search using ORM
    results = SafeQueryBuilder.safe_search_users(
        db.session, 
        search_term, 
        limit=50
    )
    
    return jsonify(results)
"""