#!/bin/bash

# Update Admin Panel Authentication Script
# This script adds proper authentication to the admin panel files on the production server

echo "Updating admin panel authentication..."

# Check if we're on the production server
if [ ! -d "/var/www/html" ]; then
    echo "Error: /var/www/html directory not found. This script should be run on the production server."
    exit 1
fi

# Check if admin.html exists
if [ ! -f "/var/www/html/admin.html" ]; then
    echo "Error: /var/www/html/admin.html not found."
    exit 1
fi

# Create backup of original admin.html
echo "Creating backup of admin.html..."
cp /var/www/html/admin.html /var/www/html/admin.html.backup.$(date +%Y%m%d_%H%M%S)

# Create a temporary file for the updated content
TEMP_FILE=$(mktemp)

# Read the original file and add authentication
echo "Adding authentication code to admin.html..."
awk '
BEGIN { script_found = 0; auth_added = 0 }
{
    # Look for the first <script> tag
    if (!auth_added && /<script>/ || /<script[[:space:]]/) {
        script_found = 1
        print $0
        print "        // Authentication check"
        print "        const token = localStorage.getItem('\''kuwait_social_token'\'');"
        print "        if (!token) {"
        print "            window.location.href = '\''/admin-login.html'\'';"
        print "        }"
        print ""
        print "        // Set up axios defaults"
        print "        if (typeof axios !== '\''undefined'\'') {"
        print "            axios.defaults.headers.common['\''Authorization'\''] = `Bearer ${token}`;"
        print "        }"
        print ""
        auth_added = 1
    } else {
        print $0
    }
}
' /var/www/html/admin.html > "$TEMP_FILE"

# Check if we need to add logout button in the header
if ! grep -q "logout()" /var/www/html/admin.html; then
    echo "Adding logout button to header..."
    
    # Create another temp file for adding logout button
    TEMP_FILE2=$(mktemp)
    
    awk '
    BEGIN { header_found = 0; logout_added = 0 }
    {
        print $0
        # Look for header section or user info area
        if (!logout_added && (/<div class="user-info">/ || /<div class="header-content">/ || /<header[[:space:]]/ || /<header>/)) {
            header_found = 1
        }
        # Add logout button after finding a good spot in the header
        if (header_found && !logout_added && (/<\/span>/ || /<\/div>/) && /user.*email/i) {
            print "                <button class=\"btn-logout\" onclick=\"logout()\" style=\"background-color: #dc3545; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer; font-size: 14px; margin-left: 10px;\">Logout</button>"
            logout_added = 1
        }
    }
    END {
        # If logout function doesn'\''t exist, add it before closing script tag
        if (logout_added) {
            print ""
            print "        // Logout function"
            print "        function logout() {"
            print "            localStorage.removeItem('\''kuwait_social_token'\'');"
            print "            localStorage.removeItem('\''kuwait_social_user'\'');"
            print "            window.location.href = '\''/admin-login.html'\'';"
            print "        }"
        }
    }
    ' "$TEMP_FILE" > "$TEMP_FILE2"
    
    mv "$TEMP_FILE2" "$TEMP_FILE"
fi

# Move the updated file to the original location
mv "$TEMP_FILE" /var/www/html/admin.html

# Set proper permissions
chown www-data:www-data /var/www/html/admin.html
chmod 644 /var/www/html/admin.html

echo "Admin panel authentication update completed!"

# Check if admin-login.html exists
if [ ! -f "/var/www/html/admin-login.html" ]; then
    echo ""
    echo "Warning: /var/www/html/admin-login.html not found!"
    echo "Please make sure to deploy the admin login page as well."
fi

echo ""
echo "Summary of changes:"
echo "1. Added authentication check at the beginning of the first <script> section"
echo "2. Added axios defaults setup with Bearer token"
echo "3. Added logout button in the header (if not already present)"
echo "4. Added logout function"
echo "5. Created backup: admin.html.backup.$(date +%Y%m%d_%H%M%S)"