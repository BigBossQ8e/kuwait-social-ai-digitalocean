# 🧪 Admin Panel Testing Guide

## Quick Start

### 1. Start the Backend Server

```bash
cd backend
python wsgi.py
```

The server will start on `http://localhost:5001`

### 2. Create Test Admin User

Run this script to create a test admin user:

```bash
python create_test_admin.py
```

This creates:
- **Email**: admin@example.com
- **Password**: password
- **Role**: owner (highest privileges)

### 3. Setup Test Data

Run this script to populate test data:

```bash
python setup_test_data.py
```

This creates:
- 6 social media platforms (Instagram, Twitter, Facebook, LinkedIn, TikTok, YouTube)
- 6 feature flags (AI Content, Multi-Language, Scheduling, Analytics, etc.)
- 3 service packages (Starter, Professional, Enterprise)

### 4. Access the Admin Panel

Open your browser and navigate to:

```
http://localhost:5001/admin-test
```

## 🎯 Testing the Admin Panel

### Step 1: Authentication

1. Enter the test credentials:
   - Email: `admin@example.com`
   - Password: `password`
2. Click **Login**
3. You should see "Authenticated" status

### Step 2: WebSocket Connection

1. After logging in, click **Connect** in the WebSocket section
2. You should see:
   - "Connected" status
   - Real-time log entries
   - Admin role confirmation

### Step 3: Platform Management

1. The Platforms tab shows all social media platforms
2. Try toggling platforms on/off using the switches
3. Watch the WebSocket log for real-time updates
4. Notice the active client count for each platform

### Step 4: Feature Flags

1. Click the **Features** tab
2. View all available features with descriptions
3. Toggle features on/off
4. Features are categorized (AI, Content, Posting, etc.)

### Step 5: Service Packages

1. Click the **Packages** tab
2. View the three service tiers
3. See pricing and feature limits
4. Check active/inactive status

### Step 6: Activity Feed

1. Click the **Activity** tab
2. See real-time admin actions
3. Every toggle and change is logged
4. Timestamps show when actions occurred

### Step 7: Configuration Sync

1. Click the **Config Sync** tab
2. Click **Sync All Clients** to test sync
3. Click **Get Stats** to see sync statistics
4. Monitor sync health status

## 🔍 What to Look For

### Real-Time Updates
- When you toggle a platform or feature, check the WebSocket log
- You should see immediate update messages
- The UI should refresh automatically

### Security Features
- Try logging out and accessing the page again
- The system should require re-authentication
- WebSocket should disconnect on logout

### Role-Based Access
- The admin user has "owner" role with full access
- All actions are logged with admin ID
- Audit trail shows who made changes

## 🛠️ Troubleshooting

### Can't Login?
1. Make sure you ran `create_test_admin.py`
2. Check the server is running on port 5001
3. Try the exact credentials: admin@example.com / password

### WebSocket Won't Connect?
1. Make sure you're logged in first
2. Check browser console for errors
3. Ensure the server supports WebSocket connections

### No Data Showing?
1. Run `setup_test_data.py` to create test data
2. Refresh the page after running the script
3. Check browser console for API errors

### Server Errors?
1. Check if all required models are migrated:
   ```bash
   python -c "from app_factory import create_app; app = create_app(); app.app_context().push(); from models import db; db.create_all()"
   ```
2. Check server logs for detailed errors
3. Ensure all dependencies are installed

## 🎨 UI Features

### Dashboard Stats
- Total active clients
- Enabled platforms count
- Total features
- Monthly revenue

### Interactive Elements
- Toggle switches for instant on/off
- Tab navigation for different sections
- Real-time WebSocket status
- Activity feed auto-updates

### Visual Feedback
- Green badges for connected/active states
- Red badges for disconnected/inactive
- Loading spinners during data fetch
- Success/error messages

## 🔧 Advanced Testing

### Test Real-Time Sync
1. Open two browser tabs with the admin panel
2. Login in both tabs
3. Toggle a platform in one tab
4. The other tab should update automatically

### Test Token Refresh
1. Login and wait 15 minutes
2. Try to perform an action
3. The system should automatically refresh your token

### Test Bulk Operations
1. In Features tab, use bulk toggle (if implemented)
2. Watch multiple features update at once
3. Check activity log for bulk action record

## 📊 What's Implemented

✅ **Authentication System**
- JWT login with refresh tokens
- Secure logout
- Token auto-refresh

✅ **Platform Management**
- Enable/disable platforms
- View active client counts
- Real-time updates

✅ **Feature Flags**
- Toggle features on/off
- Categorized features
- Sub-feature support (backend ready)

✅ **Package Management**
- View service tiers
- Pricing information
- Feature assignments

✅ **Real-Time Updates**
- WebSocket connection
- Live configuration changes
- Activity feed updates

✅ **Configuration Sync**
- Force sync clients
- View sync statistics
- Monitor sync health

## 🚀 Next Steps

After testing the current implementation, consider:

1. **Frontend Framework**: Replace the test HTML with React/Vue
2. **Advanced Analytics**: Add charts and graphs
3. **User Management**: Add/edit/delete users interface
4. **Monitoring Dashboard**: System health metrics
5. **Mobile Responsive**: Optimize for mobile devices

---

The admin panel backend is fully functional and ready for production use. This HTML interface demonstrates all the implemented features and real-time capabilities.