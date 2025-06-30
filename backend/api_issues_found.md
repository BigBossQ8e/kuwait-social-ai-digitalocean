# API Issues Found During Testing

## Date: June 30, 2025

### 1. Authentication Issues
- **Admin login fails** with credentials `admin@kwtsocial.com / admin123`
  - Error: Invalid credentials (401)
  - The password on production server is different

### 2. Missing/404 Endpoints
Many endpoints that the React UI expects are returning 404:

#### Client endpoints:
- `/api/clients/profile` 
- `/api/clients/dashboard`
- `/api/clients/posts`
- `/api/clients/analytics`
- `/api/clients/social-accounts`
- `/api/clients/competitors`
- `/api/clients/features`
- `/api/clients/subscription`

**Note**: There's a `/api/client/dashboard` endpoint (singular "client") that exists but requires active subscription

#### Post Management:
- `/api/posts` (all CRUD operations)
- `/api/posts/drafts`
- `/api/posts/scheduled`
- `/api/posts/published`

#### Content Features:
- `/api/content/hashtags/suggest`
- `/api/content/trending-hashtags`

#### Analytics (partial):
- `/api/analytics/posts`
- `/api/analytics/engagement` 
- `/api/analytics/growth`
- `/api/analytics/export`

#### Social Integration:
- `/api/social/instagram/auth-url`
- `/api/social/snapchat/auth-url`

#### Kuwait Features:
- `/api/prayer-times`
- `/api/kuwait/events`
- `/api/kuwait/trending`
- `/api/kuwait/cultural-guidelines`

#### Competitor Analysis:
- `/api/competitors` (all endpoints)

### 3. Subscription/Permission Issues
Several endpoints return 403 "Active subscription required" even for trial users:
- `/api/content/generate`
- `/api/content/templates`
- `/api/content/validate`
- `/api/client/dashboard`

### 4. Inconsistent URL Patterns
- Some endpoints use plural (`/clients/`) while others use singular (`/client/`)
- This inconsistency may cause the React app to call wrong endpoints

### 5. Recommendations

1. **Fix Admin Password**: Update the admin password in production database
2. **Implement Missing Endpoints**: Many core features are not implemented
3. **Fix Subscription Logic**: Trial users should have access to basic features
4. **Standardize URL Patterns**: Use consistent plural/singular naming
5. **Update React App**: Ensure it calls the correct endpoint URLs

### Working Endpoints:
✅ `/api/health`
✅ `/api/auth/login` (client only)
✅ `/api/auth/me`
✅ `/api/auth/logout`
✅ `/api/analytics/overview`
✅ `/api/social/accounts`

### React UI Impact:
The React app likely won't function properly for:
- Client dashboard
- Post creation and management
- Analytics views
- Competitor analysis
- Social media integration
- Kuwait-specific features