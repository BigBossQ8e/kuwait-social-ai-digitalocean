# Upload Checklist for Droplet

## Files to Upload via SFTP

Make sure these files exist and are configured:

### ✅ Critical Files:
- [ ] `.env` (created by setup.sh - contains your secrets)
- [ ] `docker-compose.yml`
- [ ] `deploy.sh`
- [ ] `nginx.conf`

### ✅ Backend Folder:
- [ ] `backend/` (entire folder)
- [ ] `backend/requirements.txt`
- [ ] `backend/Dockerfile`
- [ ] `backend/wsgi.py`

### ✅ Frontend Folder:
- [ ] `frontend-react/` (entire folder)
- [ ] `frontend-react/package.json`
- [ ] `frontend-react/Dockerfile.digitalocean`
- [ ] `frontend-react/.env.production`

### ✅ Deployment Scripts:
- [ ] `init-app.sh`
- [ ] `backup.sh`

## SFTP Connection Details:
- **Host**: [YOUR_DROPLET_IP]
- **Port**: 22
- **Username**: root
- **Password**: [Your root password]
- **Upload to**: `/root/kuwait-social-ai/`

## Recommended SFTP Clients:
- **Mac**: Cyberduck (free) - https://cyberduck.io
- **Windows**: WinSCP (free) - https://winscp.net
- **Cross-platform**: FileZilla - https://filezilla-project.org