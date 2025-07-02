#!/bin/bash

# Update admin panel with authentication

# Add logout function at the end of the script section
cat >> /var/www/html/admin.html << 'LOGOUT_FUNCTION'

// Logout function
function logout() {
    localStorage.removeItem('kuwait_social_token');
    localStorage.removeItem('kuwait_social_user');
    window.location.href = '/admin-login.html';
}
LOGOUT_FUNCTION

# Update header to include logout button
sed -i 's|<h1>🤖 AI Prompt Management</h1>|<div style="display: flex; justify-content: space-between; align-items: center; width: 100%;"><div><h1>🤖 AI Prompt Management</h1>|' /var/www/html/admin.html
sed -i 's|<p>Create, edit, and manage AI prompts with Kuwaiti NLP support</p>|<p>Create, edit, and manage AI prompts with Kuwaiti NLP support</p></div><button onclick="logout()" style="background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3); padding: 8px 16px; border-radius: 6px; cursor: pointer;">Logout</button></div>|' /var/www/html/admin.html

echo "Admin panel updated with authentication!"