// Main application layout component

import React, { useState } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Avatar,
  Menu,
  MenuItem,
  useTheme,
  useMediaQuery,
  Badge,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  PostAdd,
  Analytics,
  People,
  Settings,
  Notifications,
  AccountCircle,
  ChevronLeft,
  TrendingUp,
  Schedule,
  Campaign,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../../hooks/useAuth';
import { useAppSelector, useAppDispatch } from '../../../store';
import { 
  selectSidebarOpen, 
  selectSidebarCollapsed,
  toggleSidebar,
  toggleSidebarCollapsed,
  selectLanguage,
  selectDirection 
} from '../../../store/slices/uiSlice';
import { DRAWER_WIDTH, DRAWER_WIDTH_COLLAPSED, HEADER_HEIGHT } from '../../../utils/constants';
import { LanguageSwitcher } from '../LanguageSwitcher';

interface AppLayoutProps {
  children: React.ReactNode;
}

interface NavigationItem {
  id: string;
  label: string;
  labelAr: string;
  icon: React.ReactElement;
  path: string;
  roles?: string[];
  badge?: number;
}

const navigationItems: NavigationItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    labelAr: 'الرئيسية',
    icon: <Dashboard />,
    path: '/dashboard',
    roles: ['client', 'admin'],
  },
  {
    id: 'posts',
    label: 'Posts',
    labelAr: 'المنشورات',
    icon: <PostAdd />,
    path: '/posts',
    roles: ['client'],
  },
  {
    id: 'analytics',
    label: 'Analytics',
    labelAr: 'التحليلات',
    icon: <Analytics />,
    path: '/analytics',
    roles: ['client'],
  },
  {
    id: 'competitors',
    label: 'Competitors',
    labelAr: 'المنافسون',
    icon: <TrendingUp />,
    path: '/competitors',
    roles: ['client'],
  },
  {
    id: 'campaigns',
    label: 'Campaigns',
    labelAr: 'الحملات',
    icon: <Campaign />,
    path: '/campaigns',
    roles: ['client'],
  },
  {
    id: 'schedule',
    label: 'Schedule',
    labelAr: 'الجدولة',
    icon: <Schedule />,
    path: '/schedule',
    roles: ['client'],
  },
  {
    id: 'clients',
    label: 'Clients',
    labelAr: 'العملاء',
    icon: <People />,
    path: '/admin/clients',
    roles: ['admin'],
  },
  {
    id: 'settings',
    label: 'Settings',
    labelAr: 'الإعدادات',
    icon: <Settings />,
    path: '/settings',
    roles: ['client', 'admin'],
  },
];

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useAppDispatch();
  
  const { user, logout, hasRole } = useAuth();
  const sidebarOpen = useAppSelector(selectSidebarOpen);
  const sidebarCollapsed = useAppSelector(selectSidebarCollapsed);
  const language = useAppSelector(selectLanguage);
  const direction = useAppSelector(selectDirection);

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notificationsAnchor, setNotificationsAnchor] = useState<null | HTMLElement>(null);

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationsOpen = (event: React.MouseEvent<HTMLElement>) => {
    setNotificationsAnchor(event.currentTarget);
  };

  const handleNotificationsClose = () => {
    setNotificationsAnchor(null);
  };

  const handleLogout = async () => {
    await logout();
    handleProfileMenuClose();
    navigate('/login');
  };

  const handleNavigate = (path: string) => {
    navigate(path);
    if (isMobile) {
      dispatch(toggleSidebar());
    }
  };

  const handleSidebarToggle = () => {
    if (isMobile) {
      dispatch(toggleSidebar());
    } else {
      dispatch(toggleSidebarCollapsed());
    }
  };

  // Filter navigation items based on user role
  const filteredNavItems = navigationItems.filter(item => 
    !item.roles || item.roles.some(role => hasRole(role))
  );

  const drawerWidth = sidebarCollapsed ? DRAWER_WIDTH_COLLAPSED : DRAWER_WIDTH;

  const drawer = (
    <Box>
      {/* Logo/Header Section */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: sidebarCollapsed ? 'center' : 'space-between',
          px: sidebarCollapsed ? 1 : 2,
          py: 2,
          minHeight: HEADER_HEIGHT,
          borderBottom: `1px solid ${theme.palette.divider}`,
        }}
      >
        {!sidebarCollapsed && (
          <Typography variant="h6" noWrap component="div" fontWeight="bold">
            Kuwait Social AI
          </Typography>
        )}
        {!isMobile && (
          <IconButton onClick={handleSidebarToggle} size="small">
            <ChevronLeft 
              sx={{ 
                transform: sidebarCollapsed 
                  ? direction === 'rtl' ? 'rotate(180deg)' : 'rotate(0deg)'
                  : direction === 'rtl' ? 'rotate(0deg)' : 'rotate(180deg)',
                transition: 'transform 0.3s'
              }} 
            />
          </IconButton>
        )}
      </Box>

      <Divider />

      {/* Navigation Items */}
      <List sx={{ pt: 1 }}>
        {filteredNavItems.map((item) => {
          const isActive = location.pathname === item.path || 
                          location.pathname.startsWith(item.path + '/');
          const label = language === 'ar' ? item.labelAr : item.label;

          return (
            <ListItem key={item.id} disablePadding>
              <ListItemButton
                onClick={() => handleNavigate(item.path)}
                selected={isActive}
                sx={{
                  mx: 1,
                  borderRadius: 1,
                  '&.Mui-selected': {
                    backgroundColor: theme.palette.primary.main + '20',
                    color: theme.palette.primary.main,
                    '& .MuiListItemIcon-root': {
                      color: theme.palette.primary.main,
                    },
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: sidebarCollapsed ? 'auto' : 56 }}>
                  {item.badge ? (
                    <Badge badgeContent={item.badge} color="error">
                      {item.icon}
                    </Badge>
                  ) : (
                    item.icon
                  )}
                </ListItemIcon>
                {!sidebarCollapsed && (
                  <ListItemText 
                    primary={label}
                    primaryTypographyProps={{
                      fontSize: '0.9rem',
                      fontWeight: isActive ? 600 : 400,
                    }}
                  />
                )}
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          backgroundColor: theme.palette.background.paper,
          color: theme.palette.text.primary,
          boxShadow: 1,
        }}
      >
        <Toolbar sx={{ minHeight: `${HEADER_HEIGHT}px !important` }}>
          <IconButton
            edge="start"
            onClick={handleSidebarToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          <Box sx={{ flexGrow: 1 }} />
          
          {/* Language Switcher */}
          <LanguageSwitcher />
          
          {/* Notifications */}
          <IconButton
            onClick={handleNotificationsOpen}
            sx={{ mr: 1 }}
          >
            <Badge badgeContent={3} color="error">
              <Notifications />
            </Badge>
          </IconButton>

          {/* Profile Menu */}
          <IconButton onClick={handleProfileMenuOpen}>
            <Avatar sx={{ width: 32, height: 32 }}>
              {user?.email?.charAt(0).toUpperCase()}
            </Avatar>
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Drawer */}
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant={isMobile ? 'temporary' : 'permanent'}
          open={isMobile ? sidebarOpen : true}
          onClose={() => dispatch(toggleSidebar())}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              borderRight: `1px solid ${theme.palette.divider}`,
              transition: theme.transitions.create('width', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.leavingScreen,
              }),
            },
          }}
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          backgroundColor: theme.palette.background.default,
        }}
      >
        <Toolbar sx={{ minHeight: `${HEADER_HEIGHT}px !important` }} />
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      </Box>

      {/* Profile Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleProfileMenuClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={() => { navigate('/profile'); handleProfileMenuClose(); }}>
          <AccountCircle sx={{ mr: 1 }} />
          {language === 'ar' ? 'الملف الشخصي' : 'Profile'}
        </MenuItem>
        <MenuItem onClick={() => { navigate('/settings'); handleProfileMenuClose(); }}>
          <Settings sx={{ mr: 1 }} />
          {language === 'ar' ? 'الإعدادات' : 'Settings'}
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleLogout}>
          {language === 'ar' ? 'تسجيل الخروج' : 'Logout'}
        </MenuItem>
      </Menu>

      {/* Notifications Menu */}
      <Menu
        anchorEl={notificationsAnchor}
        open={Boolean(notificationsAnchor)}
        onClose={handleNotificationsClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        sx={{ mt: 1 }}
      >
        <MenuItem>
          <Typography variant="body2">
            {language === 'ar' ? 'لا توجد إشعارات جديدة' : 'No new notifications'}
          </Typography>
        </MenuItem>
      </Menu>
    </Box>
  );
};