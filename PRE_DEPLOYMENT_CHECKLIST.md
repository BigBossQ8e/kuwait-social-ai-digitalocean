# Pre-Deployment Checklist

## Before Uploading to GitHub/DigitalOcean

### 1. Run Setup Script ✅
```bash
./setup.sh
```

When running the script:
- **Enter your domain name** when prompted (e.g., `kuwaisocial.com`)
- **Provide your OpenAI API key**
- **Choose database option**:
  - Option 1: Local PostgreSQL (for Docker/Droplet)
  - Option 2: DigitalOcean Managed Database (recommended for production)
- **Configure email settings** (optional but recommended)

### 2. Verify Generated Files ✅
After running setup.sh, check that these files were created:
- `.env` - Contains all your secrets and configuration
- `frontend-react/.env.production` - Frontend production config
- `.do/app.yaml` - DigitalOcean App Platform specification
- `DEPLOYMENT_SUMMARY.md` - Summary of your configuration

### 3. Security Check ✅
**IMPORTANT**: Before uploading to GitHub:
- Ensure `.env` is in `.gitignore` (it should be by default)
- Never commit `.env` to version control
- Review `DEPLOYMENT_SUMMARY.md` - it shows masked secrets

### 4. Update GitHub References ✅
If using DigitalOcean App Platform, edit `.do/app.yaml`:
```yaml
github:
  repo: your-github-username/your-repo-name  # Update this!
  branch: main
```

### 5. Test Locally (Optional) ✅
```bash
# Test with Docker
docker-compose up -d

# Visit http://localhost to verify
```

### 6. Final Upload Steps ✅

```bash
# 1. Initialize git (if not already done)
git init

# 2. Add all files EXCEPT .env
git add .
git status  # Verify .env is NOT listed

# 3. Commit
git commit -m "Initial deployment - Kuwait Social AI"

# 4. Add your GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# 5. Push to GitHub
git push -u origin main
```

### 7. Deploy on DigitalOcean ✅
1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click "Create App"
3. Select your GitHub repository
4. DigitalOcean will detect the `.do/app.yaml` file
5. Review and deploy

### 8. Post-Deployment ✅
After your app is deployed:
1. Run database migrations (check DigitalOcean console)
2. Access your app at your domain
3. Login with default admin credentials
4. **IMMEDIATELY change the admin password**

## Quick Commands Summary

```bash
# 1. Configure everything
./setup.sh

# 2. Validate setup
./validate-deployment.sh

# 3. Upload to GitHub (excluding .env)
git add . && git commit -m "Deploy" && git push

# 4. Deploy via DigitalOcean dashboard
```

## Need Help?
- Run `./validate-deployment.sh` to check for issues
- See `DEPLOY_GUIDE.md` for detailed instructions
- Check `CORS_SETUP.md` for API connectivity issues