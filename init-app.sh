#!/bin/bash
# Initialize the application after deployment

echo "🚀 Initializing Kuwait Social AI..."

# Run database migrations
cd backend
source venv/bin/activate || python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
flask db upgrade

# Create admin user
python << END
from app_factory import create_app
from models import db, User
import os

app = create_app()
with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(email='admin@kuwaisocial.ai').first()
    if not admin:
        admin = User(
            email='admin@kuwaisocial.ai',
            role='admin',
            is_active=True
        )
        admin.set_password('ChangeMeFirst123!')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created: admin@kuwaisocial.ai")
        print("⚠️  Default password: ChangeMeFirst123!")
        print("🔐 Please change this password immediately!")
    else:
        print("ℹ️  Admin user already exists")
END

deactivate
echo "✅ Initialization complete!"
