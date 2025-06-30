# Add Admin Redirect to Working Panel

To redirect users from the React admin route to the working HTML admin panel, add this to your nginx configuration:

```nginx
# In /etc/nginx/sites-available/kwtsocial.com, add this location block:

location = /admin {
    return 301 /admin-panel/;
}
```

This way:
- Users going to `/admin` will automatically redirect to `/admin-panel/`
- The working admin panel becomes the default
- We can enhance the React version later without confusion

## Commands to run on server:

```bash
# Edit nginx config
nano /etc/nginx/sites-available/kwtsocial.com

# Add the redirect location block

# Test and reload
nginx -t
systemctl reload nginx
```