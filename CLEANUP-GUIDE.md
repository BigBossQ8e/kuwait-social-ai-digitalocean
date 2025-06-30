# Server Cleanup Guide for Kuwait Social AI

## Quick Audit Commands

Run these scripts to check your server status:

### 1. Quick Duplicate Check
```bash
./check-duplicates.sh
```
This shows:
- Multiple frontend implementations
- Duplicate route/model files
- Temporary/test files

### 2. Full Server Audit
```bash
./server-audit.sh
```
Creates detailed report with:
- Docker status
- File duplicates
- Directory structure
- Resource usage

### 3. Verify What's Running
```bash
./verify-implementation.sh
```
Checks:
- Active endpoints
- Frontend type (React vs HTML)
- Feature availability

## Common Issues & Solutions

### Issue 1: Old HTML Landing Page Still Active

**Check:**
```bash
curl -s https://kwtsocial.com | grep -q "sections-wrapper" && echo "Old HTML active"
```

**Fix:**
```bash
# On server
cd /var/www/kwtsocial
mv static/index.html static/index.html.old  # Backup old file
# Then deploy React build
```

### Issue 2: Multiple Frontend Files

**Check:**
```bash
find /var/www/kwtsocial -name "index.html" -type f | grep -v node_modules
```

**Fix:**
```bash
# Keep only the React build in static/
# Remove or backup other HTML files
```

### Issue 3: Duplicate Python Files

**Check:**
```bash
cd /var/www/kwtsocial
find . -name "*.py" -type f -exec md5sum {} \; | sort | uniq -w32 -d
```

**Fix:**
```bash
# Remove duplicate files
# Keep the most recent/correct version
```

### Issue 4: Old Backup Files

**Check:**
```bash
find /var/www/kwtsocial -name "*.bak" -o -name "*.old" -o -name "*~"
```

**Fix:**
```bash
# Move to backup directory or delete
mkdir -p /var/backups/kwtsocial/old-files
mv *.bak *.old *~ /var/backups/kwtsocial/old-files/
```

## Clean Deployment Structure

Your server should have:

```
/var/www/kwtsocial/
├── static/              # React build output only
│   ├── index.html      # From npm run build
│   ├── assets/         # JS/CSS bundles
│   └── vite.svg        # Favicon
├── routes/             # Python API routes
│   ├── auth.py
│   ├── admin.py
│   ├── client.py
│   ├── translations.py # New bilingual support
│   └── ...
├── models/             # Database models
│   ├── user.py
│   ├── translation.py  # New bilingual support
│   └── ...
├── app_factory.py      # Main app configuration
├── requirements.txt    # Python dependencies
├── docker-compose.yml  # Container orchestration
└── NO index.html in root!
```

## Safe Cleanup Commands

### 1. Remove Python Cache
```bash
find /var/www/kwtsocial -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find /var/www/kwtsocial -name "*.pyc" -delete
```

### 2. Clean Docker Logs
```bash
# Backup recent logs first
docker-compose logs --tail=1000 > logs-backup-$(date +%Y%m%d).txt

# Truncate large log files
truncate -s 0 $(docker inspect --format='{{.LogPath}}' kwtsocial-web)
```

### 3. Remove Temporary Files
```bash
find /var/www/kwtsocial -name "*.tmp" -o -name "*.temp" -delete
```

### 4. Clean Old Docker Images
```bash
docker image prune -a --filter "until=24h"
```

## Verification After Cleanup

1. **Check site still works:**
   ```bash
   curl -I https://kwtsocial.com
   ```

2. **Verify React app active:**
   ```bash
   curl -s https://kwtsocial.com | grep -q "Vite" && echo "React OK"
   ```

3. **Test API:**
   ```bash
   curl https://kwtsocial.com/api/health
   ```

4. **Check Docker status:**
   ```bash
   docker-compose ps
   ```

## Important Notes

- Always backup before deleting
- Don't delete docker volumes (contains database)
- Keep requirements.txt and package.json
- Preserve .env files
- Test after each cleanup step

## Red Flags to Look For

1. **Multiple index.html files** - Should only have one in static/
2. **HTML files in root** - All frontend should be in static/
3. **Duplicate .py files** - Check timestamps and keep newest
4. **.bak/.old files** - Move to backup location
5. **Large log files** - Rotate or truncate
6. **Orphaned containers** - Remove with `docker container prune`

## Quick Health Check

After cleanup, run:
```bash
# Check all services are up
docker-compose ps

# Verify endpoints
curl https://kwtsocial.com/api/health
curl -s https://kwtsocial.com | head -20

# Check disk space
df -h /var/www

# Monitor for errors
docker logs --tail=50 kwtsocial-web
```