# Admin Settings & Client Signup Implementation

## 🎛️ 1. Admin Settings Panel (`admin-panel/settings.html`)

### What It Does:
The admin can control **EXACTLY** which fields are required for client registration using toggle switches.

### Settings Available:

#### Basic Information
- ✅ Company Name (always required - cannot disable)
- ✅ Contact Name (toggle on/off)
- ✅ Email (always required - cannot disable)  
- ✅ Phone Number (toggle on/off)

#### Kuwait Compliance Fields
- ⚡ Commercial License Number (toggle on/off)
- ⚡ Civil ID (toggle on/off)
- ⚡ Kuwait Phone Validation (toggle on/off)
- ⚡ SMS OTP Verification (toggle on/off)

#### Additional Information
- ⚡ Business Address (toggle on/off)
- ⚡ Website URL (toggle on/off)
- ⚡ Business Category (toggle on/off)

#### Required Agreements
- ⚡ Content Compliance Agreement (toggle on/off)
- ⚡ Data Privacy Consent (toggle on/off)
- ⚡ Terms of Service (toggle on/off)

#### Client Self-Registration Options
- ⚡ Enable Client Signup (toggle on/off)
- ⚡ Auto-approve Registrations (toggle on/off)
- ⚡ Default Trial Period (toggle on/off)

### How It Works:
1. Admin goes to Settings page
2. Toggles ON/OFF any requirements
3. Clicks "Save Settings"
4. These settings apply to BOTH:
   - Admin creating clients in dashboard
   - Clients signing up themselves

## 📝 2. Client Self-Signup Page (`client-signup/index.html`)

### Features:
- **Beautiful 4-step wizard** with progress indicator
- **Responsive design** works on all devices
- **Dynamic fields** based on admin settings
- **Real-time validation**

### Steps:
1. **Business Info** - Company details
2. **Contact Details** - Personal info & password
3. **Choose Plan** - Select subscription
4. **Verification** - Accept terms

### Smart Features:
- Shows/hides fields based on admin settings
- If admin turns OFF "Commercial License", it won't show
- If admin turns ON "Kuwait Phone Validation", enforces +965 format
- Password confirmation validation
- All required checkboxes must be checked

### Plans Available:
- **Free Trial** - 7 days, 10 posts
- **Basic** - 29 KWD/month, 30 posts
- **Professional** - 79 KWD/month, 100 posts
- **Premium** - 199 KWD/month, 500 posts

## 🚀 Deployment

### 1. Deploy Admin Settings:
```bash
scp admin-panel/settings.html root@kwtsocial.com:/var/www/html/admin-panel/
```

### 2. Deploy Client Signup:
```bash
scp -r client-signup root@kwtsocial.com:/var/www/html/
```

### 3. Update nginx to serve signup page:
```nginx
location /signup {
    alias /var/www/html/client-signup;
    try_files $uri $uri/ /signup/index.html;
}
```

### 4. Add Settings link to admin dashboard:
In `dashboard.html`, add:
```html
<a href="/admin-panel/settings.html" class="btn btn-secondary">⚙️ Settings</a>
```

## 📋 How Admin Controls Work

### Example Scenarios:

#### Scenario 1: Basic Setup (International Clients)
Admin turns OFF:
- ❌ Commercial License
- ❌ Civil ID
- ❌ Kuwait Phone Validation

Result: Signup form only asks for basic info

#### Scenario 2: Full Kuwait Compliance
Admin turns ON:
- ✅ Commercial License
- ✅ Civil ID
- ✅ Kuwait Phone Validation
- ✅ SMS OTP Verification

Result: Signup form requires all Kuwait fields

#### Scenario 3: Privacy-Focused
Admin turns ON:
- ✅ All agreement checkboxes
- ✅ SMS verification

Result: Clients must accept all terms and verify phone

## 🔗 URLs

- **Admin Settings**: https://kwtsocial.com/admin-panel/settings.html
- **Client Signup**: https://kwtsocial.com/signup
- **Admin Dashboard**: https://kwtsocial.com/admin-panel/

## 🎯 Benefits

1. **Flexibility**: Admin decides requirements based on business needs
2. **Compliance**: Can enforce Kuwait regulations when needed
3. **User-Friendly**: Clean signup process with clear steps
4. **Validation**: Real-time checking prevents errors
5. **Professional**: Modern design builds trust

## 📱 Mobile Optimized

Both settings panel and signup form are fully responsive:
- Settings panel stacks vertically on mobile
- Signup form adjusts to single column
- Touch-friendly toggle switches
- Large buttons for easy tapping

## 🔒 Security Features

- Password minimum 8 characters
- Password confirmation required
- Email validation
- Phone format validation
- Required fields cannot be bypassed
- All data sent over HTTPS

The admin now has COMPLETE CONTROL over registration requirements!