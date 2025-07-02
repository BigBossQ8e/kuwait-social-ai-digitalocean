# Kuwait Social AI Backend - Quick Start Guide

## Setup Complete! ✓

All issues have been fixed:
- Database connection working (SQLite for development)
- User authentication working
- All routes registered and accessible

## Test User Created

```
Email: test@restaurant.com
Password: password123
Role: client
```

## Starting the Backend Server

```bash
cd /Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/backend
python3 start_server.py
```

The server will run on: **http://localhost:8000**

## Testing the API

### 1. Login (Get Access Token)

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@restaurant.com","password":"password123"}'
```

This will return a JSON response with an access token:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {
    "id": 1,
    "email": "test@restaurant.com",
    "role": "client",
    "company_name": "Test Restaurant"
  }
}
```

### 2. Access Protected Routes

Use the access token in the Authorization header:

```bash
# Get user profile
curl http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Get client dashboard
curl http://localhost:8000/api/client/dashboard \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Available Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Register new user
- `POST /api/auth/logout` - Logout
- `GET /api/auth/profile` - Get user profile (requires auth)
- `POST /api/auth/refresh` - Refresh access token

### Client Portal
- `GET /api/client/dashboard` - Client dashboard
- `GET /api/client/posts` - List posts
- `POST /api/client/posts` - Create new post
- `GET /api/client/analytics/overview` - Analytics overview
- `GET /api/client/competitors` - List competitors

### Admin Portal
- `GET /api/admin/dashboard` - Admin dashboard (requires admin role)
- `GET /api/admin/clients` - List all clients
- `GET /api/admin/analytics` - Platform analytics

## Frontend Access

If you have the React frontend running on `http://localhost:3000`, it should now be able to connect to the backend API on `http://localhost:8000`.

## Troubleshooting

### Port Already in Use
If port 8000 is in use, you can change it in `start_server.py`

### Database Issues
The database file is `kuwait_social_test.db` in the backend directory. To reset:
```bash
rm kuwait_social_test.db
python3 init_db.py
```

### Redis Errors
Redis is not required for development. The app uses in-memory storage for rate limiting in dev mode.