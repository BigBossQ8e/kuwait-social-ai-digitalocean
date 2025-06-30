#\!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/opt/kuwait-social-ai/backend')

from app_factory import create_app
from models import db, User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    user = User.query.filter_by(email='admin@kwtsocial.com').first()
    if user:
        user.password_hash = generate_password_hash('Kuwait2025@AI\!')
        db.session.commit()
        print("Password reset successfully\!")
    else:
        print("User not found\!")
EOF < /dev/null
