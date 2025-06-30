# Redis Connection Fix

## Problem
The backend is trying to connect to Redis for rate limiting, but Redis is not running.

## Solutions

### Option 1: Use Memory Storage (Development Only)
```bash
# In .env file:
RATELIMIT_STORAGE_URL=memory://
```

### Option 2: Install Redis (Recommended for Production)

#### On macOS (local development):
```bash
brew install redis
brew services start redis
```

#### On Ubuntu/Debian (production server):
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis
sudo systemctl start redis
```

### Option 3: Use Docker Redis
```bash
docker run -d -p 6379:6379 redis:alpine
```

## Production Configuration

For production with multiple Gunicorn workers, you MUST use Redis:

1. Install Redis on server
2. Update .env:
```bash
RATELIMIT_STORAGE_URL=redis://localhost:6379/1
```

3. Ensure Redis is running:
```bash
sudo systemctl status redis
```

## Testing Redis Connection
```bash
redis-cli ping
# Should return: PONG
```

## Alternative: Disable Rate Limiting (NOT Recommended)
If you absolutely cannot use Redis, you can disable rate limiting by modifying the Flask-Limiter initialization, but this leaves your API vulnerable to abuse.