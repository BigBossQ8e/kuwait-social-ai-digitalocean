#!/bin/bash

# Deploy Admin Authentication System
# This script deploys both admin-login.html and updates admin.html with authentication

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Kuwait Social AI Admin Authentication Deployment ===${NC}"
echo ""

# Function to deploy to production server
deploy_to_production() {
    local SERVER="root@68.183.67.219"
    
    echo -e "${YELLOW}Deploying admin authentication to production server...${NC}"
    
    # First, copy the admin-login.html file
    echo "Copying admin-login.html to server..."
    scp /Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/backend/admin-login.html $SERVER:/var/www/html/
    
    # Copy the update script
    echo "Copying update script to server..."
    scp /Users/almassaied/Downloads/kuwait-social-ai-hosting/digitalocean-latest/update-admin-auth.sh $SERVER:/tmp/
    
    # Execute the update script on the server
    echo "Executing authentication update on server..."
    ssh $SERVER "bash /tmp/update-admin-auth.sh"
    
    # Clean up
    ssh $SERVER "rm /tmp/update-admin-auth.sh"
    
    echo -e "${GREEN}Deployment completed!${NC}"
}

# Function to create a manual update for admin.html
create_manual_update() {
    echo -e "${YELLOW}Creating manual update instructions...${NC}"
    
    cat > manual-admin-auth-update.txt << 'EOF'
MANUAL ADMIN AUTHENTICATION UPDATE
==================================

If the automated script fails, follow these steps to manually update admin.html:

1. SSH into your server:
   ssh root@68.183.67.219

2. Create a backup of admin.html:
   cp /var/www/html/admin.html /var/www/html/admin.html.backup

3. Edit admin.html:
   nano /var/www/html/admin.html

4. Find the first <script> tag in the file and add this code right after it:

        // Authentication check
        const token = localStorage.getItem('kuwait_social_token');
        if (!token) {
            window.location.href = '/admin-login.html';
        }

        // Set up axios defaults
        if (typeof axios !== 'undefined') {
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        }

5. Find the header section with user info and add a logout button:

        <button class="btn-logout" onclick="logout()" style="background-color: #dc3545; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer; font-size: 14px; margin-left: 10px;">Logout</button>

6. Add the logout function before the closing </script> tag:

        // Logout function
        function logout() {
            localStorage.removeItem('kuwait_social_token');
            localStorage.removeItem('kuwait_social_user');
            window.location.href = '/admin-login.html';
        }

7. Save and exit (Ctrl+X, then Y, then Enter)

8. Set proper permissions:
   chown www-data:www-data /var/www/html/admin.html
   chmod 644 /var/www/html/admin.html

9. Deploy admin-login.html if not already present:
   # Copy the admin-login.html content from the backup location

EOF
    
    echo -e "${GREEN}Manual instructions saved to: manual-admin-auth-update.txt${NC}"
}

# Main execution
echo "Choose deployment method:"
echo "1) Automatic deployment to production server"
echo "2) Create manual update instructions"
echo "3) Both"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        deploy_to_production
        ;;
    2)
        create_manual_update
        ;;
    3)
        deploy_to_production
        create_manual_update
        ;;
    *)
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}=== Important Notes ===${NC}"
echo "1. Make sure admin-login.html is accessible at /admin-login.html"
echo "2. The authentication uses 'kuwait_social_token' in localStorage"
echo "3. All API calls will include the Bearer token in Authorization header"
echo "4. Users will be redirected to login if no token is found"
echo "5. The logout button will clear the token and redirect to login"