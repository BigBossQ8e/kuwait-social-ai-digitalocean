# Bilingual System Deployment Guide

## Pre-Deployment Checklist

- [ ] Backup current production database
- [ ] Backup current production files
- [ ] Test build locally
- [ ] Review changed files

## Step 1: Build Frontend Locally

```bash
cd frontend-react
npm install
npm run build
```

Verify the `dist` folder is created.

## Step 2: Connect to Server

```bash
ssh root@209.38.176.129
cd /var/www/kwtsocial
```

## Step 3: Create Backup

```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres kuwait_social_ai > backup-$(date +%Y%m%d).sql

# Backup files
tar -czf backup-$(date +%Y%m%d).tar.gz --exclude='*.log' --exclude='__pycache__' .
```

## Step 4: Update Backend Files

From your local machine:

```bash
# Copy new backend files
scp backend/routes/translations.py root@209.38.176.129:/var/www/kwtsocial/routes/
scp backend/models/translation.py root@209.38.176.129:/var/www/kwtsocial/models/
scp backend/app_factory.py root@209.38.176.129:/var/www/kwtsocial/
scp backend/migrations/add_translations_tables.sql root@209.38.176.129:/var/www/kwtsocial/migrations/
scp backend/scripts/populate_translations.py root@209.38.176.129:/var/www/kwtsocial/scripts/
```

## Step 5: Run Database Migration

On the server:

```bash
# Run migration
docker-compose exec postgres psql -U postgres -d kuwait_social_ai < migrations/add_translations_tables.sql

# Verify tables created
docker-compose exec postgres psql -U postgres -d kuwait_social_ai -c "\dt translations*"
```

## Step 6: Deploy Frontend

From your local machine:

```bash
# Copy built frontend
scp -r frontend-react/dist/* root@209.38.176.129:/var/www/kwtsocial/static/
```

## Step 7: Restart Services

On the server:

```bash
# Restart backend services
docker-compose restart web celery

# Check logs
docker logs kwtsocial-web --tail 50

# Reload nginx
docker exec kwtsocial-nginx nginx -s reload
```

## Step 8: Populate Translations

On the server:

```bash
# First, copy the translation files
docker cp scripts/populate_translations.py kwtsocial-web:/app/scripts/

# Run the population script
docker-compose exec web python scripts/populate_translations.py
```

## Step 9: Verify Deployment

1. **Check API Health**:
   ```bash
   curl https://kwtsocial.com/api/health
   ```

2. **Check Translations API**:
   ```bash
   curl https://kwtsocial.com/api/translations?locale=en
   ```

3. **Test in Browser**:
   - Visit https://kwtsocial.com
   - Click language switcher (AR/EN)
   - Verify RTL layout for Arabic
   - Test signup/login forms

4. **Admin Panel**:
   - Login as admin
   - Go to Admin Dashboard
   - Click Translations tab
   - Verify editor loads

## Step 10: Monitor

```bash
# Watch logs
docker logs -f kwtsocial-web

# Check for errors
docker logs kwtsocial-web 2>&1 | grep ERROR
```

## Rollback (if needed)

```bash
# Restore database
docker-compose exec postgres psql -U postgres -d kuwait_social_ai < backup-YYYYMMDD.sql

# Restore files
tar -xzf backup-YYYYMMDD.tar.gz

# Restart services
docker-compose restart
```

## Common Issues

### Translation API Returns 404
- Check if app_factory.py was updated
- Verify translations blueprint is registered
- Restart web service

### Frontend Shows Old Version
- Clear browser cache
- Check nginx cache: `docker exec kwtsocial-nginx rm -rf /var/cache/nginx/*`
- Verify files copied to correct location

### Database Migration Fails
- Check if tables already exist
- Verify postgres connection
- Check user permissions

### Arabic Text Not RTL
- Verify i18n files are included in build
- Check browser console for errors
- Ensure language switcher is visible

## Post-Deployment

1. **Test Critical Flows**:
   - User registration (both languages)
   - User login (both languages)
   - Language switching persistence
   - Admin translation editing

2. **Performance Check**:
   - Page load times
   - Translation API response time
   - Check server resources: `docker stats`

3. **Set Up Monitoring**:
   - Add translation API to uptime monitoring
   - Set up error alerts for translation failures
   - Monitor disk space for translation cache

## Success Indicators

✅ Language switcher visible on all pages
✅ Arabic displays with RTL layout
✅ Translation API returns 200
✅ Admin can edit translations
✅ No console errors in browser
✅ Users can switch languages instantly
✅ Language preference persists on reload