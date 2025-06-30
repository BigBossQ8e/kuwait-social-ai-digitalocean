# Flask Built-in Server vs Gunicorn

## Current Setup

We have both options configured:

### 1. Flask Development Server (Currently Using)
- **Script**: `start_server.py`
- **Command**: `python3 start_server.py`
- **Port**: 8000
- **Pros**:
  - Built-in debugger
  - Auto-reloading on code changes
  - Detailed error messages
  - Good for development
- **Cons**:
  - Single-threaded (handles one request at a time)
  - Not secure for production
  - Poor performance
  - Flask warns against production use

### 2. Gunicorn Production Server (Recommended)
- **Script**: `start_gunicorn.py`
- **Command**: `python3 start_gunicorn.py`
- **Config**: `gunicorn_config.py`
- **Port**: 8000
- **Pros**:
  - Multi-worker (handles concurrent requests)
  - Production-ready
  - Better performance
  - Process management
  - Graceful worker restart
- **Cons**:
  - No built-in debugger
  - Requires manual reload for code changes (unless --reload flag)

## Usage

### For Development
```bash
# Use Flask's built-in server for debugging
python3 start_server.py
```

### For Production-like Testing
```bash
# Use Gunicorn
python3 start_gunicorn.py
```

### For Actual Production
```bash
# Use Gunicorn with production config
gunicorn --config gunicorn_config.py wsgi:application
```

## Current Configuration

- **Workers**: Based on CPU cores (2 * CPU count + 1)
- **Worker Class**: sync (standard synchronous workers)
- **Timeout**: 30 seconds
- **Auto-reload**: Enabled in development mode

## Performance Comparison

| Feature | Flask Dev Server | Gunicorn |
|---------|-----------------|-----------|
| Concurrent Requests | 1 | Multiple (based on workers) |
| Request/sec | ~50-100 | ~1000-5000 |
| Memory Usage | Low | Medium |
| CPU Usage | Single core | Multi-core |
| Stability | Dev only | Production ready |