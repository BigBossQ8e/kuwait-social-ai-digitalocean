#!/bin/bash

# Deploy Admin Panel V2 Updates

echo "======================================"
echo "Deploying Admin Panel V2"
echo "======================================"

# Update files on server
echo "Choose deployment method:"
echo "1. Deploy via SSH (recommended)"
echo "2. Manual deployment instructions"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
    echo "Deploying to server..."
    
    # Copy new dashboard
    scp admin-panel/dashboard-v2.html root@kwtsocial.com:/var/www/html/admin-panel/
    
    # Copy updated backend admin routes
    scp backend/routes/admin_complete.py root@kwtsocial.com:/tmp/
    
    # Apply on server
    ssh root@kwtsocial.com << 'EOF'
    # Backup current dashboard
    cp /var/www/html/admin-panel/dashboard.html /var/www/html/admin-panel/dashboard-backup.html
    
    # Replace with new version
    mv /var/www/html/admin-panel/dashboard-v2.html /var/www/html/admin-panel/dashboard.html
    
    # Update backend
    cd /opt/kuwait-social-ai
    cp backend/routes/admin.py backend/routes/admin-backup.py
    cp /tmp/admin_complete.py backend/routes/admin.py
    
    # Restart backend
    docker-compose restart backend
    
    # Clean up
    rm /tmp/admin_complete.py
    
    echo "Admin Panel V2 deployed successfully!"
EOF

else
    echo ""
    echo "Manual Deployment Instructions:"
    echo "==============================="
    echo ""
    echo "1. Copy dashboard-v2.html to server:"
    echo "   scp admin-panel/dashboard-v2.html root@kwtsocial.com:/var/www/html/admin-panel/"
    echo ""
    echo "2. SSH into server:"
    echo "   ssh root@kwtsocial.com"
    echo ""
    echo "3. Backup and replace dashboard:"
    echo "   cp /var/www/html/admin-panel/dashboard.html /var/www/html/admin-panel/dashboard-backup.html"
    echo "   mv /var/www/html/admin-panel/dashboard-v2.html /var/www/html/admin-panel/dashboard.html"
    echo ""
    echo "4. Update backend admin routes:"
    echo "   Copy the content of backend/routes/admin_complete.py to backend/routes/admin.py"
    echo ""
    echo "5. Restart backend:"
    echo "   cd /opt/kuwait-social-ai"
    echo "   docker-compose restart backend"
fi

echo ""
echo "======================================"
echo "New Features in V2:"
echo "======================================"
echo "✅ Create New Client button and modal"
echo "✅ Search functionality"
echo "✅ Action buttons for each client"
echo "✅ Success/Error messages"
echo "✅ Complete backend API endpoints"
echo ""
echo "Access at: https://kwtsocial.com/admin-panel/"