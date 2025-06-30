# MAX_CONTENT_LENGTH Type Error Fix

## Problem
The error `TypeError: '>' not supported between instances of 'int' and 'str'` indicates that `MAX_CONTENT_LENGTH` is being loaded as a string from the environment but Flask expects an integer.

## Quick Fix

SSH into your server and run these commands:

```bash
ssh root@209.38.176.129
cd /opt/kuwait-social-ai/backend
```

### Option 1: Quick Manual Fix

1. First, run the debug script to see the current state:
```bash
# Copy and run the debug script
bash debug_max_content_length.sh
```

2. Edit the config file to ensure MAX_CONTENT_LENGTH is converted to int:
```bash
# Backup the config file first
cp config/config.py config/config.py.backup

# Edit the file
nano config/config.py
```

3. Find the line that sets MAX_CONTENT_LENGTH and change it to:
```python
# Change from:
MAX_CONTENT_LENGTH = os.getenv('MAX_CONTENT_LENGTH', '16777216')

# To:
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB default
```

4. Also check `app_factory.py` for any direct config assignments:
```bash
nano app_factory.py
```

Look for lines like:
```python
app.config['MAX_CONTENT_LENGTH'] = some_value
```

And ensure they convert to int if needed:
```python
app.config['MAX_CONTENT_LENGTH'] = int(some_value) if isinstance(some_value, str) else some_value
```

### Option 2: Automated Fix

Run the fix script:
```bash
# Copy the fix script to the server
scp fix_max_content_length.py root@209.38.176.129:/opt/kuwait-social-ai/backend/

# Run it
cd /opt/kuwait-social-ai/backend
python3 fix_max_content_length.py
```

### Option 3: Environment Variable Fix

If you want to keep the code unchanged, ensure the environment variable is set as a number:

1. Check current systemd service file:
```bash
cat /etc/systemd/system/kuwait-social.service
```

2. Edit the service file:
```bash
nano /etc/systemd/system/kuwait-social.service
```

3. Ensure MAX_CONTENT_LENGTH is set without quotes:
```ini
Environment="MAX_CONTENT_LENGTH=16777216"
# NOT: Environment="MAX_CONTENT_LENGTH='16777216'"
```

4. Reload and restart:
```bash
systemctl daemon-reload
systemctl restart kuwait-social
```

## Verification

After applying the fix:

1. Check the logs:
```bash
journalctl -u kuwait-social -f
```

2. Test file upload:
```bash
# This should work without the type error
curl -X POST http://localhost:5000/api/some-upload-endpoint \
  -F "file=@test-file.jpg" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Common MAX_CONTENT_LENGTH Values

- `16777216` (16MB) - Good for most applications
- `5242880` (5MB) - Conservative, good for images
- `104857600` (100MB) - For video uploads
- `1073741824` (1GB) - Very large files

## Prevention

Always ensure environment variables that should be numbers are converted:
```python
# Good practices:
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
PORT = int(os.getenv('PORT', '5000'))
```