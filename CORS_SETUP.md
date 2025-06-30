# CORS Configuration Guide for Kuwait Social AI

## Overview

The backend API now includes proper CORS (Cross-Origin Resource Sharing) configuration to handle both development and production deployments.

## Quick Setup

### For Production Deployment

1. **When running the setup script**, provide your domain when prompted:
   ```bash
   ./setup.sh
   # When asked: "Enter your domain name"
   # Enter: yourdomain.com
   ```

2. The script will automatically:
   - Set `CORS_ORIGINS` to `https://yourdomain.com`
   - Configure the frontend to use the correct API URL
   - Update the DigitalOcean App Platform spec

### For Development

If you skip the domain configuration, the setup script will configure CORS for local development:
- `CORS_ORIGINS=http://localhost:3000,http://localhost:5173`

## Manual Configuration

If you need to manually set CORS origins, edit your `.env` file:

```bash
# Single domain
CORS_ORIGINS=https://yourdomain.com

# Multiple domains (comma-separated)
CORS_ORIGINS=https://app.example.com,https://admin.example.com

# Development
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## DigitalOcean App Platform

When deploying to DigitalOcean App Platform:

1. **Same-domain deployment** (Recommended):
   - Frontend and backend are in the same app
   - Frontend uses `/api` for API calls
   - No CORS issues as they're on the same domain

2. **Separate domains**:
   - Set `CORS_ORIGINS` environment variable in App Platform
   - Example: `CORS_ORIGINS=https://your-frontend.ondigitalocean.app`

## Testing CORS Configuration

After deployment, test your CORS setup:

```bash
# Test preflight request
curl -X OPTIONS https://yourdomain.com/api/health \
  -H "Origin: https://yourdomain.com" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Authorization" \
  -v

# Test actual request
curl https://yourdomain.com/api/health \
  -H "Origin: https://yourdomain.com" \
  -v
```

## Security Notes

1. **Never use wildcards** (`*`) for CORS origins in production
2. **Always use HTTPS** for production domains
3. **Be specific** with allowed origins - only add domains you control
4. **Review regularly** - remove old domains that are no longer in use

## Troubleshooting

### CORS errors in browser console

1. Check that `CORS_ORIGINS` includes your frontend domain
2. Ensure you're using HTTPS in production
3. Verify the backend is receiving the correct Origin header

### API calls failing in production

1. Check `VITE_API_URL` in frontend build
2. Verify backend CORS configuration includes frontend domain
3. Check browser Network tab for specific error details

### Testing locally

For local development with frontend on port 5173:
```bash
CORS_ORIGINS=http://localhost:5173
```

## Environment Variables

The backend reads CORS configuration from:
- `CORS_ORIGINS`: Comma-separated list of allowed origins
- `FLASK_ENV`: Determines if running in development or production mode

In development mode (`FLASK_ENV=development`), the backend automatically includes common localhost ports.