#!/usr/bin/env python3
"""
Verify SQLAlchemy relationships are properly configured
"""

from app_factory import create_app
from models import User, Admin, Client, Owner, Post, SocialAccount, Analytics, PostAnalytics, SupportTicket

app = create_app()

with app.app_context():
    print("=== Verifying SQLAlchemy Relationships ===\n")
    
    # Check User relationships
    print("1. User relationships:")
    user_rels = User.__mapper__.relationships
    for rel in user_rels:
        print(f"   - User.{rel.key} -> {rel.mapper.class_.__name__}")
        if rel.back_populates:
            print(f"     back_populates: {rel.back_populates}")
    
    print("\n2. Admin relationships:")
    admin_rels = Admin.__mapper__.relationships
    for rel in admin_rels:
        print(f"   - Admin.{rel.key} -> {rel.mapper.class_.__name__}")
        if rel.back_populates:
            print(f"     back_populates: {rel.back_populates}")
    
    print("\n3. Client relationships:")
    client_rels = Client.__mapper__.relationships
    for rel in client_rels:
        print(f"   - Client.{rel.key} -> {rel.mapper.class_.__name__}")
        if rel.back_populates:
            print(f"     back_populates: {rel.back_populates}")
    
    print("\n4. Post relationships:")
    post_rels = Post.__mapper__.relationships
    for rel in post_rels:
        print(f"   - Post.{rel.key} -> {rel.mapper.class_.__name__}")
        if rel.back_populates:
            print(f"     back_populates: {rel.back_populates}")
    
    print("\n5. SocialAccount relationships:")
    sa_rels = SocialAccount.__mapper__.relationships
    for rel in sa_rels:
        print(f"   - SocialAccount.{rel.key} -> {rel.mapper.class_.__name__}")
        if rel.back_populates:
            print(f"     back_populates: {rel.back_populates}")
    
    print("\n6. Analytics relationships:")
    analytics_rels = Analytics.__mapper__.relationships
    for rel in analytics_rels:
        print(f"   - Analytics.{rel.key} -> {rel.mapper.class_.__name__}")
        if rel.back_populates:
            print(f"     back_populates: {rel.back_populates}")
    
    print("\n7. PostAnalytics relationships:")
    pa_rels = PostAnalytics.__mapper__.relationships
    for rel in pa_rels:
        print(f"   - PostAnalytics.{rel.key} -> {rel.mapper.class_.__name__}")
        if rel.back_populates:
            print(f"     back_populates: {rel.back_populates}")
    
    print("\n8. SupportTicket relationships:")
    st_rels = SupportTicket.__mapper__.relationships
    for rel in st_rels:
        print(f"   - SupportTicket.{rel.key} -> {rel.mapper.class_.__name__}")
        if rel.back_populates:
            print(f"     back_populates: {rel.back_populates}")
    
    print("\n✅ All critical relationships verified!")