# Kuwait Social AI - Test Preview Pages

This directory contains HTML preview pages for testing both frontend UI and backend API connections.

## Preview Pages

### 1. Login Page (`login-page.html`)
- Main entry point for the application
- Shows login form with demo credentials
- Tests authentication API endpoint
- Includes quick demo mode (no login required)

### 2. Client Dashboard (`client-dashboard.html`)
- Preview of client user interface
- Shows main features available to business clients:
  - Dashboard statistics
  - Quick actions (Create Post, AI Content, etc.)
  - Recent posts with Arabic support
  - API testing section
- Simulates real-time updates

### 3. Admin Dashboard (`admin-dashboard.html`)
- Preview of admin panel interface
- Shows admin-specific features:
  - Client management
  - System health monitoring
  - Revenue tracking
  - Performance metrics
  - API testing for admin endpoints

### 4. Admin Panel Complete (`admin-panel-complete.html`)
- Comprehensive admin interface with all features
- Includes full sidebar navigation with sections:
  - Dashboard with detailed metrics
  - Client Management with advanced filters
  - Analytics & Reports
  - Performance Monitoring
  - Revenue & Subscriptions
  - Content Moderation
  - System Health
  - Audit Logs
  - Error Tracking
  - Settings & Configuration
- Features interactive components and real-time updates

### 5. Platform Settings (`platform-settings.html`)
- Platform owner configuration interface
- 10 comprehensive settings categories:
  - General Settings (platform name, URL, timezone)
  - Branding (logo, colors, custom CSS)
  - API Keys (OpenAI, Instagram, Snapchat, TikTok, Telegram)
  - Email Configuration (SMTP settings, templates)
  - Feature Management (toggle platform features)
  - Pricing & Subscriptions (plan management)
  - Localization (languages, Kuwait-specific settings)
  - Security (password policy, 2FA, rate limiting)
  - Integrations (third-party services, webhooks)
  - Advanced Settings (debug mode, maintenance tools)

## How to Use

### Local Testing
1. Open any HTML file directly in your browser
2. Use the "Quick Demo" button to navigate without authentication
3. Test the UI interactions and responsive design

### API Testing
Each dashboard includes an API test section that attempts to connect to:
- Production API: `https://kwtsocial.com/api`
- Local API: `http://localhost:5000/api` (if running locally)

### Demo Credentials
The login page provides three test accounts:
- **Client**: client@demo.com / Demo123!
- **Admin**: admin@demo.com / Admin123!
- **Owner**: owner@demo.com / Owner123!

## Features Demonstrated

### Client Features
- Social media post management
- AI content generation interface
- Analytics dashboard
- Multi-platform support (Instagram, Snapchat, TikTok)
- Arabic language support
- Real-time statistics

### Admin Features
- User management table
- System health monitoring
- Revenue tracking
- Performance metrics
- Error tracking
- Database statistics

### Platform Owner Features
- Complete platform configuration
- API key management
- Branding customization
- Feature toggles
- Security settings
- Integration management

### API Endpoints Tested
- `/api/health` - System health check
- `/api/auth/login` - Authentication
- `/api/client/dashboard` - Client dashboard data
- `/api/admin/users` - User management
- `/api/admin/performance/system/health` - System metrics
- `/api/monitoring/metrics` - Monitoring data

## Customization
You can modify these files to:
- Test different UI layouts
- Add new features
- Test additional API endpoints
- Customize styling and branding

## Note
These are static HTML previews. For full functionality, the backend API must be running and accessible.

## Quick Start Navigation
1. Start with `login-page.html`
2. Use "Quick Demo" to explore without authentication
3. Navigate between dashboards using the provided links
4. Test API connections using the built-in test buttons
5. For platform configuration, open `platform-settings.html` directly