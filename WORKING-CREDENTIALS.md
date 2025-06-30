# Kuwait Social AI - Working Credentials

Last Updated: June 29, 2025

## ✅ Production Server Details

- **Domain**: https://kwtsocial.com
- **Server IP**: 209.38.176.129
- **Server Hostname**: kuwait-social-ai-1750866347

## 🔐 Working User Credentials

### Test Client User
- **Email**: test@restaurant.com
- **Password**: password123
- **Role**: client
- **Company**: Test Restaurant
- **Status**: Active

### Admin User
- **Email**: admin@kwtsocial.com
- **Password**: admin123
- **Role**: admin
- **Status**: Active

## 📋 All Known Users

### Client Users:
1. test@test.com - Test Company (Active subscription)
2. test@restaurant.com - Test Restaurant (Trial) ✅
3. test@fbrestaurant.com - ⚠️ No client profile
4. client1@test.com - Kuwait Coffee House (Active)
5. client2@test.com - Desert Rose Restaurant (Active)
6. client3@test.com - Tech Solutions Kuwait (Active)

### Admin Users:
1. admin@kwtsocial.com ✅
2. admin@kuwaitsocial.ai

## 🚀 System Status (as of June 29, 2025)

### Backend Status: ✅ WORKING
- Login endpoint: `/api/auth/login` - Working
- User verification: `/api/auth/me` - Working
- Health check: `/api/health` - Working
- Database: Connected and operational
- Redis: Connected and operational

### Frontend Status: ✅ DEPLOYED
- React SPA deployed with login timeout fix
- Role-based routing implemented
- Enhanced content features added
- Time-based hashtag suggestions active

### Infrastructure:
- Docker Compose deployment
- Nginx reverse proxy configured
- SSL certificates active
- CORS properly configured

## 🔧 Common Commands

### SSH into server:
```bash
ssh root@209.38.176.129
```

### Check backend logs:
```bash
docker logs backend-web-1 --tail 50
```

### Restart backend:
```bash
docker restart backend-web-1
```

### Check all containers:
```bash
docker ps
```

## 📝 Notes

- Backend was fixed to handle JWT user IDs properly
- CORS is configured to accept requests from https://kwtsocial.com
- Database has all necessary columns
- Authentication flow is fully functional