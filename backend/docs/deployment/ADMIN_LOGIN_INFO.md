# Kuwait Social AI - Admin Login Information

## Production Admin Account

**URL**: https://kwtsocial.com/admin  
**Email**: admin@kwtsocial.com  
**Password**: You'll need to reset it (see below)

## Reset Admin Password

Since the password in the database is hashed, here's how to reset it:

### Option 1: Create a Password Reset Script

```bash
ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221

cd /opt/kuwait-social-ai/backend
source venv-py311/bin/activate

python << EOF
from app_factory import create_app
from models import db, User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    admin = User.query.filter_by(email='admin@kwtsocial.com').first()
    if admin:
        # Set a new password
        admin.password_hash = generate_password_hash('Kuwait2024Admin!')
        db.session.commit()
        print("✅ Password reset successfully!")
        print("New password: Kuwait2024Admin!")
    else:
        print("❌ Admin user not found!")
EOF
```

### Option 2: Create a New Admin User

If you prefer to create your own admin account:

```bash
ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221

cd /opt/kuwait-social-ai/backend
source venv-py311/bin/activate

python << EOF
from app_factory import create_app
from models import db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app()
with app.app_context():
    # Create new admin
    new_admin = User(
        email='your-email@example.com',  # Change this!
        username='yourusername',         # Change this!
        password_hash=generate_password_hash('YourSecurePassword123!'),  # Change this!
        role='admin',
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow()
    )
    
    db.session.add(new_admin)
    db.session.commit()
    print("✅ New admin user created!")
EOF
```

## Important Security Notes

1. **Change the default password immediately** after first login
2. Use a strong password (minimum 12 characters, mix of letters, numbers, symbols)
3. Consider enabling 2FA if available
4. Don't share admin credentials
5. Create individual admin accounts for each administrator

## Test Admin Panel Access

After resetting the password:

1. Visit https://kwtsocial.com/admin
2. Login with:
   - Email: admin@kwtsocial.com
   - Password: Kuwait2024Admin! (or whatever you set)
3. You should see the admin dashboard

## Troubleshooting

If you can't access the admin panel:

1. Check if the service is running:
   ```bash
   systemctl status kuwait-backend
   ```

2. Check the logs:
   ```bash
   journalctl -u kuwait-backend -n 50
   ```

3. Verify the admin routes are registered:
   ```bash
   curl https://kwtsocial.com/admin/login
   ```
   Should return the login page, not a 404.