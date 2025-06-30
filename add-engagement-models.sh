#!/bin/bash

echo "📝 Adding engagement models from backup..."

ssh root@209.38.176.129 << 'ENDSSH'
cd /opt/kuwait-social-ai/backend

# First, check current state
echo "Current models.py has $(wc -l < models.py) lines"

# Extract just the model definitions we need
cat >> models.py << 'EOF'

# Engagement Models (from backup)

class CommentTemplate(db.Model):
    __tablename__ = 'comment_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    template_name = db.Column(db.String(100), nullable=False)
    template_text = db.Column(db.Text, nullable=False)
    variables = db.Column(db.JSON)  # List of available variables
    language = db.Column(db.String(10), default='ar')
    category = db.Column(db.String(50))  # greeting, thanks, apology, etc.
    tone = db.Column(db.String(50))  # formal, casual, friendly
    is_active = db.Column(db.Boolean, default=True)
    usage_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', backref='comment_templates')

class UnifiedInboxMessage(db.Model):
    __tablename__ = 'unified_inbox_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # instagram, twitter, tiktok
    platform_message_id = db.Column(db.String(255), unique=True)
    message_type = db.Column(db.String(50))  # comment, dm, mention
    sender_username = db.Column(db.String(255))
    sender_name = db.Column(db.String(255))
    sender_profile_url = db.Column(db.String(500))
    content = db.Column(db.Text)
    sentiment = db.Column(db.String(20))  # positive, negative, neutral
    priority = db.Column(db.String(20), default='normal')  # high, normal, low
    status = db.Column(db.String(20), default='unread')  # unread, read, replied, archived
    thread_id = db.Column(db.Integer, db.ForeignKey('message_threads.id'))
    parent_message_id = db.Column(db.Integer, db.ForeignKey('unified_inbox_messages.id'))
    responded_at = db.Column(db.DateTime)
    response_time_minutes = db.Column(db.Integer)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    tags = db.Column(db.JSON)  # List of tags
    metadata = db.Column(db.JSON)  # Platform-specific data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', backref='inbox_messages')
    thread = db.relationship('MessageThread', backref='messages')
    replies = db.relationship('UnifiedInboxMessage', backref=db.backref('parent', remote_side=[id]))
    assigned_user = db.relationship('User', backref='assigned_messages')

class MessageThread(db.Model):
    __tablename__ = 'message_threads'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    thread_type = db.Column(db.String(50))  # conversation, post_comments
    original_post_id = db.Column(db.String(255))  # For comment threads
    participant_username = db.Column(db.String(255))
    status = db.Column(db.String(20), default='open')  # open, closed, pending
    priority = db.Column(db.String(20), default='normal')
    first_message_at = db.Column(db.DateTime)
    last_message_at = db.Column(db.DateTime)
    message_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', backref='message_threads')

class ResponseMetrics(db.Model):
    __tablename__ = 'response_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    platform = db.Column(db.String(50))
    total_messages = db.Column(db.Integer, default=0)
    messages_replied = db.Column(db.Integer, default=0)
    avg_response_time_minutes = db.Column(db.Float)
    fastest_response_minutes = db.Column(db.Integer)
    slowest_response_minutes = db.Column(db.Integer)
    positive_sentiment_count = db.Column(db.Integer, default=0)
    negative_sentiment_count = db.Column(db.Integer, default=0)
    neutral_sentiment_count = db.Column(db.Integer, default=0)
    automation_rate = db.Column(db.Float)  # Percentage of automated responses
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', backref='response_metrics')

class CustomerProfile(db.Model):
    __tablename__ = 'customer_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    platform_username = db.Column(db.String(255), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    display_name = db.Column(db.String(255))
    profile_url = db.Column(db.String(500))
    follower_count = db.Column(db.Integer)
    is_verified = db.Column(db.Boolean, default=False)
    customer_type = db.Column(db.String(50))  # regular, vip, influencer
    total_interactions = db.Column(db.Integer, default=0)
    positive_interactions = db.Column(db.Integer, default=0)
    negative_interactions = db.Column(db.Integer, default=0)
    last_interaction_at = db.Column(db.DateTime)
    avg_sentiment_score = db.Column(db.Float)
    tags = db.Column(db.JSON)  # Custom tags
    notes = db.Column(db.Text)  # Internal notes
    preferences = db.Column(db.JSON)  # Language preference, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', backref='customer_profiles')

class EngagementAutomation(db.Model):
    __tablename__ = 'engagement_automations'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    trigger_type = db.Column(db.String(50))  # keyword, sentiment, time_based
    trigger_conditions = db.Column(db.JSON)  # Conditions for triggering
    action_type = db.Column(db.String(50))  # auto_reply, alert, tag
    action_data = db.Column(db.JSON)  # Template ID, alert details, etc.
    platform = db.Column(db.String(50))  # all, instagram, twitter, etc.
    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=0)  # Higher priority runs first
    execution_count = db.Column(db.Integer, default=0)
    last_executed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', backref='automations')
EOF

echo "✅ Added engagement models"
echo "New models.py has $(wc -l < models.py) lines"

# Now start the backend
echo ""
echo "🚀 Starting backend..."
pkill -f gunicorn
sleep 2

export $(grep -v '^#' .env | xargs)
/usr/local/bin/gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 3 \
    --daemon \
    --pid /tmp/gunicorn.pid \
    --error-logfile logs/error.log \
    wsgi:app

sleep 5

echo ""
echo "📊 Status check..."
if ps -p $(cat /tmp/gunicorn.pid 2>/dev/null) > /dev/null 2>&1; then
    echo "✅ Backend is running!"
    curl -s http://localhost:5000/api/health
else
    echo "❌ Backend failed"
    tail -10 logs/error.log
fi

ENDSSH