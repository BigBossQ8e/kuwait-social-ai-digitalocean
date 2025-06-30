#!/bin/bash
# Incremental cleanup of all model relationships

echo "=== Starting Incremental Model Cleanup ==="
echo

ssh root@209.38.176.129 << 'SSHEOF'
cd /opt/kuwait-social-ai/backend

# Create backups first
echo "Creating backups..."
for file in models/*.py; do
    if [ -f "$file" ]; then
        cp "$file" "${file}.backup_cleanup_$(date +%Y%m%d_%H%M%S)"
    fi
done

# Function to check if a model exists
check_model_exists() {
    model_name=$1
    grep -r "class $model_name" . --include="*.py" | grep -v __pycache__ | grep -v backup > /dev/null
    return $?
}

# Step 1: Find all relationships that reference non-existent models
echo -e "\n1. Searching for relationships to non-existent models..."

# Common models that might not exist
potential_missing_models=(
    "PerformanceAlert"
    "CulturalEvent"
    "TelegramAccount"
    "APIKey"
    "CompetitorStrategyMetric"
    "NotificationPreference"
    "SystemAlert"
    "AuditLog"
    "PaymentTransaction"
    "SubscriptionHistory"
)

for model in "${potential_missing_models[@]}"; do
    echo -n "Checking $model... "
    if ! check_model_exists "$model"; then
        echo "NOT FOUND - will comment out relationships"
        # Find and comment out relationships to this model
        for file in models/*.py; do
            if grep -q "relationship.*['\"]$model['\"]" "$file"; then
                echo "  Found in $file"
                sed -i "s/\(.*relationship.*['\"]$model['\"].*\)/# \1  # TODO: $model model not implemented/" "$file"
            fi
        done
    else
        echo "exists"
    fi
done

# Step 2: Find all back_populates mismatches
echo -e "\n2. Checking for back_populates mismatches..."

# Extract all relationships with back_populates
grep -h "relationship.*back_populates" models/*.py | grep -v "^#" | while read -r line; do
    # Extract the target model and back_populates name
    if [[ $line =~ relationship\([\'\"](.*?)[\'\"].*back_populates=[\'\"](.*?)[\'\"] ]]; then
        target_model="${BASH_REMATCH[1]}"
        backref_name="${BASH_REMATCH[2]}"
        
        # Check if the target model has the corresponding relationship
        if ! grep -q "${backref_name}.*=.*relationship.*back_populates" models/*.py 2>/dev/null; then
            echo "  Mismatch found: $target_model.$backref_name"
        fi
    fi
done

# Step 3: Find relationships using backref instead of back_populates
echo -e "\n3. Finding relationships still using backref..."
grep -n "relationship.*backref=" models/*.py | grep -v "^#" | while read -r match; do
    echo "  $match"
done

# Step 4: Apply specific fixes we know about
echo -e "\n4. Applying known fixes..."

# Fix ClientError relationship if needed
if grep -q "class ClientError" models/client_error.py; then
    echo "Fixing ClientError relationships..."
    # Make sure ClientError has user relationship
    if ! grep -q "user = db.relationship" models/client_error.py; then
        sed -i '/reported_by = db.Column/ a\    user = db.relationship("User", back_populates="client_errors")' models/client_error.py
    fi
fi

# Fix CustomerEngagement relationship if needed
if grep -q "class CustomerEngagement" models/engagement_models.py; then
    echo "Fixing CustomerEngagement relationships..."
    # Make sure CustomerEngagement has responder relationship
    if ! grep -q "responder = db.relationship" models/engagement_models.py; then
        sed -i '/responder_id = db.Column/ a\    responder = db.relationship("User", back_populates="engagement_responses")' models/engagement_models.py
    fi
fi

# Step 5: Check for circular imports or missing imports
echo -e "\n5. Checking model imports..."
for file in models/*.py; do
    if [ -f "$file" ] && [ "$file" != "models/__init__.py" ]; then
        filename=$(basename "$file")
        if ! grep -q "from \. import db" "$file" && ! grep -q "from models import db" "$file"; then
            echo "  Warning: $filename might be missing db import"
        fi
    fi
done

# Step 6: Restart backend gracefully
echo -e "\n6. Restarting backend gracefully..."
cd /opt/kuwait-social-ai
docker exec kuwait-social-backend kill -HUP 1 2>/dev/null || docker-compose restart backend

echo "Waiting for backend to reload..."
sleep 10

# Check for errors
echo -e "\n7. Checking for errors after cleanup..."
docker-compose logs --tail=50 backend | grep -E "ERROR|Exception|relationship" | grep -v "INFO" | tail -20

echo -e "\nCleanup complete!"

SSHEOF