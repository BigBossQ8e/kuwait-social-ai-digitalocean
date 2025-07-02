# 🚀 How to Run the Admin Panel

## Step-by-Step Instructions

### 1. Activate Virtual Environment

```bash
cd /Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/backend
source venv/bin/activate
```

### 2. Run the Server

```bash
python wsgi.py
```

Or if that doesn't work:
```bash
python3 wsgi.py
```

### 3. Create Test Admin User

In a new terminal window (also activate venv):
```bash
cd /Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/backend
source venv/bin/activate
python create_test_admin.py
```

### 4. Setup Test Data

```bash
python setup_test_data.py
```

### 5. Open Admin Panel

Open your browser and go to:
```
http://localhost:5001/admin-test
```

### 6. Login

- **Email**: admin@example.com
- **Password**: password

## Alternative: Run Everything in One Command

Create a startup script:

```bash
#!/bin/bash
cd /Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/backend
source venv/bin/activate
echo "Creating test admin..."
python create_test_admin.py
echo "Setting up test data..."
python setup_test_data.py
echo "Starting server..."
python wsgi.py
```

## Troubleshooting

### If "python" command not found:
- Use `python3` instead of `python`
- Make sure virtual environment is activated

### If modules not found:
```bash
pip install -r requirements.txt
```

### If port 5001 is in use:
```bash
# Find what's using port 5001
lsof -i :5001

# Kill the process if needed
kill -9 <PID>
```

### If database errors:
```bash
# Create all tables
python3 -c "from app_factory import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all()"
```