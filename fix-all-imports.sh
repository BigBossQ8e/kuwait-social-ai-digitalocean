#!/bin/bash

echo "🔧 Fixing ALL model import issues..."

ssh root@209.38.176.129 << 'ENDSSH'
cd /opt/kuwait-social-ai/backend

echo "Step 1: Fixing hashtag_strategy_service.py..."
sed -i 's/from models\.hashtag_models import/# from models.hashtag_models import/' services/hashtag_strategy_service.py

echo "Step 2: Fixing normalized_query_examples.py..."  
sed -i 's/from models\.normalized_models import/# from models.normalized_models import/' services/normalized_query_examples.py

echo "Step 3: Creating missing model classes in models.py..."
cat >> models.py << 'EOF'

# Add missing model classes
class HashtagTemplate(Base):
    __tablename__ = 'hashtag_templates'
    id = Column(Integer, primary_key=True)
    template = Column(String(255))
    category = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class HashtagVariable(Base):
    __tablename__ = 'hashtag_variables'
    id = Column(Integer, primary_key=True)
    variable_name = Column(String(100))
    values = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class NormalizedQuery(Base):
    __tablename__ = 'normalized_queries'
    id = Column(Integer, primary_key=True)
    query = Column(String(500))
    normalized_query = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

class QueryIntent(Base):
    __tablename__ = 'query_intents'
    id = Column(Integer, primary_key=True)
    intent = Column(String(100))
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

class ClientError(Base):
    __tablename__ = 'client_errors'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    error_type = Column(String(100))
    error_message = Column(Text)
    stack_trace = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    client = relationship('Client', backref='errors')
EOF

echo "Step 4: Fixing imports to use main models file..."
# Fix hashtag service
sed -i '1a from models import HashtagTemplate, HashtagVariable' services/hashtag_strategy_service.py

# Fix normalized service
sed -i '1a from models import NormalizedQuery, QueryIntent' services/normalized_query_examples.py

# Fix client error imports
sed -i 's/from models\.client_error import ClientError/from models import ClientError/' routes/monitoring.py
sed -i 's/from models\.client_error import ClientError/from models import ClientError/' routes/client_errors.py

echo "Step 5: Removing problematic validator imports..."
sed -i '/from models\.api_key import/d' utils/validators.py

echo "Step 6: Clearing Python cache..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo "Step 7: Restarting backend..."
pkill -f gunicorn 2>/dev/null || true
sleep 2

# Start with proper environment
export $(cat .env | grep -v '^#' | xargs)
/usr/local/bin/gunicorn --bind 0.0.0.0:5000 --workers 3 --daemon wsgi:app

echo ""
echo "Step 8: Waiting and testing..."
sleep 5

echo -n "API test: "
curl -s http://localhost:5000/api/health -w " (HTTP %{http_code})\n" || echo "Failed"

echo ""
echo "Checking for remaining errors..."
tail -10 logs/error.log 2>/dev/null | grep -i "import\|module" | tail -5

echo ""
echo "✅ Import fixes complete!"
ENDSSH

echo ""
echo "🌐 External test..."
curl -s https://kwtsocial.com/api/health