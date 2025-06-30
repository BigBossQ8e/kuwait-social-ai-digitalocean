# Kuwait Social AI - DigitalOcean Deployment

This folder contains all the necessary files for deploying the Kuwait Social AI platform to DigitalOcean.

## Structure

```
digitalocean-latest/
├── backend/          # Flask backend API
├── frontend-react/   # React frontend application
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick Start

### Option 1: DigitalOcean App Platform

1. Fork this repository to your GitHub account
2. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
3. Create a new app and connect your GitHub repository
4. Configure the following components:
   - **Frontend**: Set build command to `cd frontend-react && npm run build`
   - **Backend**: Set run command to `cd backend && gunicorn wsgi:app`

### Option 2: DigitalOcean Droplet

1. Create a Ubuntu 22.04 droplet
2. SSH into your droplet
3. Clone this repository
4. Run the deployment script:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

## Environment Variables

Copy `.env.example` to `.env` and configure:

### Backend (.env)
```
FLASK_APP=wsgi.py
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/dbname
OPENAI_API_KEY=your-openai-key
JWT_SECRET_KEY=your-jwt-secret
```

### Frontend (.env.production)
```
VITE_API_URL=https://your-api-domain.com/api
```

## Database Setup

1. Create a PostgreSQL database on DigitalOcean
2. Update the DATABASE_URL in your backend .env file
3. Run migrations:
   ```bash
   cd backend
   flask db upgrade
   ```

## SSL Certificate

For custom domains, use Certbot:
```bash
sudo certbot --nginx -d yourdomain.com
```

## Monitoring

- Backend logs: `/var/log/kuwait-social-backend.log`
- Frontend served by nginx: `/var/log/nginx/access.log`
- Use DigitalOcean monitoring dashboard

## Support

For issues, check the logs or open an issue in the repository.