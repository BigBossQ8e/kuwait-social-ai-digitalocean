# Admin Panel Deployment Instructions

The admin panel has been created and is ready for deployment. Follow these steps to deploy it to your server:

## Files Created

1. **admin-panel/index.html** - Login page
2. **admin-panel/dashboard.html** - Admin dashboard

## Deployment Steps

1. **SSH into your server:**
   ```bash
   ssh root@kwtsocial.com
   ```

2. **Create the admin-panel directory:**
   ```bash
   mkdir -p /var/www/html/admin-panel
   ```

3. **Create the login page:**
   ```bash
   cat > /var/www/html/admin-panel/index.html << 'EOF'
   # [Copy the contents of admin-panel/index.html here]
   EOF
   ```

4. **Create the dashboard page:**
   ```bash
   cat > /var/www/html/admin-panel/dashboard.html << 'EOF'
   # [Copy the contents of admin-panel/dashboard.html here]
   EOF
   ```

5. **Set proper permissions:**
   ```bash
   chown -R www-data:www-data /var/www/html/admin-panel
   chmod -R 755 /var/www/html/admin-panel
   ```

6. **Update nginx configuration:**
   ```bash
   # Add this location block to your nginx config for kwtsocial.com
   
   # Admin Panel (static files)
   location /admin-panel {
       alias /var/www/html/admin-panel;
       try_files $uri $uri/ /admin-panel/index.html;
       
       # Security headers for admin panel
       add_header X-Frame-Options "SAMEORIGIN" always;
       add_header X-Content-Type-Options "nosniff" always;
       add_header X-XSS-Protection "1; mode=block" always;
   }
   ```

7. **Test and reload nginx:**
   ```bash
   nginx -t
   systemctl reload nginx
   ```

## Access the Admin Panel

Once deployed, the admin panel will be available at:
- **URL:** https://kwtsocial.com/admin-panel/
- **Email:** admin@kwtsocial.com
- **Password:** KuwaitSocial2024!

## Features

### Login Page
- Secure authentication using JWT tokens
- Clean, modern UI
- Error handling for failed logins
- Automatic redirect if already logged in

### Dashboard
- **Statistics Cards:**
  - Total Clients
  - Active Clients
  - Trial Accounts
  - Total Posts

- **Client List Table:**
  - Company Name
  - Contact Name
  - Email
  - Subscription Plan
  - Status (with color-coded badges)
  - Posts Used/Limit
  - Join Date

- **Additional Features:**
  - Auto-refresh every 30 seconds
  - Logout functionality
  - Responsive design for mobile
  - Session management

## Security Notes

1. The admin panel uses JWT authentication
2. Tokens are stored in localStorage
3. All API calls include the Authorization header
4. Session expires on 401 responses
5. HTTPS is enforced via nginx

## Troubleshooting

If you encounter issues:

1. **Check nginx logs:**
   ```bash
   tail -f /var/log/nginx/error.log
   ```

2. **Verify backend is running:**
   ```bash
   docker-compose ps
   curl http://localhost:5000/api/health/health
   ```

3. **Check browser console for errors**

4. **Ensure /api/auth/me endpoint exists in backend**

## Next Steps

After deployment:
1. Test login functionality
2. Verify client list displays correctly
3. Check statistics are accurate
4. Test on mobile devices
5. Monitor for any errors

The admin panel provides a foundation for Phase 1 requirements and can be expanded with additional features as needed.