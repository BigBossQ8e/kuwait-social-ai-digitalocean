# Full Synchronization Plan - Kuwait Social AI
**Date:** July 2, 2025
**Objective:** Complete synchronization between local and production environments

## Current Status

### ✅ Successfully Deployed Yesterday:
1. **AI Services** - All working with latest models
2. **Admin Panel** - AI prompts management complete
3. **Arabic Support** - Fixed and tested
4. **Python 3.11** - Upgraded on production
5. **Authentication** - Admin login working

### ⚠️ Issues to Address:
1. **Duplicate Files** on production (old versions)
2. **Requirements.txt** - Missing locally but exists on production
3. **Environment Variables** - Different .env files
4. **Git Status** - Many untracked files need organizing

## Step-by-Step Sync Plan

### Phase 1: Clean Up Production
```bash
# Remove duplicate files
ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221 << 'EOF'
cd /opt/kuwait-social-ai/backend
# Backup old files first
mkdir -p old_files_backup
mv ai_service.py old_files_backup/ 2>/dev/null || true
mv content_generator.py old_files_backup/ 2>/dev/null || true
# Remove old backups
rm -rf models.backup-20250628-* 2>/dev/null || true
EOF
```

### Phase 2: Sync Requirements
```bash
# Copy production requirements.txt to local
scp -i ~/.ssh/kuwait-social-ai-1750866399 \
  root@46.101.180.221:/opt/kuwait-social-ai/backend/requirements.txt \
  ./requirements.txt

# Add to git
git add requirements.txt
```

### Phase 3: Organize Local Files
```bash
# Create directories for organization
mkdir -p docs/deployment
mkdir -p docs/testing
mkdir -p scripts/setup
mkdir -p scripts/testing

# Move documentation files
mv *.md docs/
mv ADMIN_*.md docs/deployment/
mv *_STATUS*.md docs/deployment/
mv *_GUIDE.md docs/testing/

# Move scripts
mv test_*.py scripts/testing/
mv fix_*.py scripts/setup/
mv check_*.py scripts/testing/
```

### Phase 4: Critical Files to Deploy

1. **Admin Panel Files** (already done, but verify)
   - routes/admin/*.py
   - models/ai_prompts.py
   - static/admin*.html

2. **Updated Services**
   - services/ai_service.py
   - services/content_generator.py
   - services/ai_agents/*.py

3. **Configuration**
   - config/config.py (with Arabic support)
   - requirements.txt

### Phase 5: Database Updates
```bash
# Ensure all tables are created
ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221 << 'EOF'
cd /opt/kuwait-social-ai/backend
source venv-py311/bin/activate
python << 'PYTHON'
from app_factory import create_app
from models import db
app = create_app()
with app.app_context():
    db.create_all()
    print("All tables created/verified")
PYTHON
EOF
```

### Phase 6: Final Verification
1. Test admin login
2. Test AI content generation
3. Test Arabic support
4. Check all API endpoints
5. Verify WebSocket connections

## Files Summary

### Must Deploy:
- [x] routes/admin/ai_prompts.py
- [x] models/ai_prompts.py
- [x] services/ai_service.py
- [x] services/content_generator.py
- [ ] requirements.txt (sync from production)
- [x] config/config.py (Arabic support)

### Already on Production:
- All admin panel routes
- AI agents implementation
- Authentication system
- Database models

### Clean Up on Production:
- [ ] /opt/kuwait-social-ai/backend/ai_service.py (old)
- [ ] /opt/kuwait-social-ai/backend/content_generator.py (duplicate)
- [ ] Old backup directories

### Local Organization Needed:
- [ ] Move 40+ documentation files to docs/
- [ ] Move test scripts to scripts/testing/
- [ ] Move setup scripts to scripts/setup/
- [ ] Add organized files to git

## Commands to Execute

```bash
# 1. Sync requirements from production
scp -i ~/.ssh/kuwait-social-ai-1750866399 \
  root@46.101.180.221:/opt/kuwait-social-ai/backend/requirements.txt .

# 2. Clean production duplicates
ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221 \
  "cd /opt/kuwait-social-ai/backend && mkdir -p old_files_backup && \
   mv ai_service.py content_generator.py old_files_backup/ 2>/dev/null || true"

# 3. Restart service
ssh -i ~/.ssh/kuwait-social-ai-1750866399 root@46.101.180.221 \
  "systemctl restart kuwait-backend && systemctl status kuwait-backend"

# 4. Test deployment
curl -s https://kwtsocial.com/api/health | jq
curl -s https://kwtsocial.com/api/test/arabic | jq
```

## Notes
- All critical functionality is already working
- Main task is cleanup and organization
- No breaking changes needed
- Backup everything before cleanup