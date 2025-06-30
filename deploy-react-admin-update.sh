#!/bin/bash

# Deploy React Admin Updates to Production

echo "======================================"
echo "Deploying React Admin Updates"
echo "======================================"

# Navigate to frontend directory
cd /Users/almassaied/Downloads/kuwait-social-ai-hosting/application/frontend-react

# Install dependencies (including axios if not present)
echo "Installing dependencies..."
npm install axios

# Build the React app
echo "Building React application..."
npm run build

# Create deployment archive
echo "Creating deployment archive..."
tar -czf frontend-admin-update.tar.gz dist/

# Copy to server
echo "Copying to server..."
scp frontend-admin-update.tar.gz root@kwtsocial.com:/tmp/

# Deploy on server
echo "Deploying on server..."
ssh root@kwtsocial.com << 'EOF'
cd /opt/kuwait-social-ai
docker-compose stop frontend
cd frontend
rm -rf dist
tar -xzf /tmp/frontend-admin-update.tar.gz
docker-compose up -d frontend
rm /tmp/frontend-admin-update.tar.gz
echo "Frontend updated successfully!"
EOF

echo ""
echo "======================================"
echo "React Admin Update Complete!"
echo "======================================"
echo ""
echo "The React admin is now updated with:"
echo "- Real-time statistics dashboard"
echo "- Client list with search and pagination"
echo "- Tabbed interface matching the original design"
echo ""
echo "Access it at: https://kwtsocial.com/admin"
echo "(will redirect to /admin-panel/ until nginx redirect is removed)"