'use client';
import { useState, useMemo } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
  Typography,
  IconButton,
  Divider,
  Tooltip,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import PostAddIcon from '@mui/icons-material/PostAdd';
import WorkIcon from '@mui/icons-material/Work';
import PeopleIcon from '@mui/icons-material/People';
import ChatIcon from '@mui/icons-material/Chat';
import BusinessIcon from '@mui/icons-material/Business';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import CreditCardIcon from '@mui/icons-material/CreditCard';
import SettingsIcon from '@mui/icons-material/Settings';
import HelpIcon from '@mui/icons-material/Help';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import LogoutIcon from '@mui/icons-material/Logout';
import { useAuth } from '@/hooks/useAuth';
import { SIDEBAR_WIDTH, SIDEBAR_COLLAPSED_WIDTH } from '@/utils/constants';

const menuItems = [
  { label: 'Dashboard', icon: <DashboardIcon />, path: '/employer/dashboard' },
  { label: 'Post Job', icon: <PostAddIcon />, path: '/employer/post-job' },
  { label: 'Manage Jobs', icon: <WorkIcon />, path: '/employer/jobs' },
  { label: 'Applicants', icon: <PeopleIcon />, path: '/employer/applicants' },
  { label: 'Messages', icon: <ChatIcon />, path: '/employer/messages' },
  { label: 'Company Profile', icon: <BusinessIcon />, path: '/employer/company-profile' },
  { label: 'Analytics', icon: <AnalyticsIcon />, path: '/employer/analytics' },
  { label: 'Subscriptions', icon: <CreditCardIcon />, path: '/employer/subscriptions' },
  { label: 'Settings', icon: <SettingsIcon />, path: '/employer/settings' },
  { label: 'Help', icon: <HelpIcon />, path: '/employer/help' },
];

export default function Sidebar({ collapsed, onToggle }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);

  const currentWidth = collapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH;

  const handleNavigation = (path) => {
    router.push(path);
    if (isMobile) setMobileOpen(false);
  };

  const drawerContent = useMemo(() => (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        bgcolor: 'background.paper',
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'space-between',
          px: collapsed ? 1 : 2.5,
          py: 2.5,
          minHeight: 72,
        }}
      >
        {!collapsed && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Box
              sx={{
                width: 36,
                height: 36,
                borderRadius: 2,
                background: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Typography sx={{ color: '#fff', fontWeight: 800, fontSize: 18 }}>
                J
              </Typography>
            </Box>
            <Box>
              <Typography sx={{ fontWeight: 700, fontSize: 18, lineHeight: 1.2, color: 'text.primary' }}>
                JobCare
              </Typography>
              <Typography sx={{ fontSize: 10, color: 'text.secondary', letterSpacing: '0.1em', textTransform: 'uppercase' }}>
                Employer Panel
              </Typography>
            </Box>
          </Box>
        )}
        {collapsed && (
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: 2,
              background: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Typography sx={{ color: '#fff', fontWeight: 800, fontSize: 20 }}>
              J
            </Typography>
          </Box>
        )}
        {!isMobile && !collapsed && (
          <IconButton size="small" onClick={onToggle} sx={{ color: 'text.secondary' }}>
            <ChevronLeftIcon fontSize="small" />
          </IconButton>
        )}
        {!isMobile && collapsed && (
          <IconButton size="small" onClick={onToggle} sx={{ color: 'text.secondary', position: 'absolute', right: -12, bgcolor: 'background.paper', boxShadow: 2, '&:hover': { bgcolor: 'background.paper' } }}>
            <ChevronRightIcon fontSize="small" />
          </IconButton>
        )}
      </Box>

      <Divider sx={{ mx: collapsed ? 1 : 2 }} />

      <List sx={{ flex: 1, overflow: 'auto', py: 1, px: collapsed ? 0.5 : 1 }}>
        {menuItems.map((item) => {
          const isActive = pathname === item.path || pathname?.startsWith(item.path + '/');
          return collapsed ? (
            <Tooltip key={item.path} title={item.label} placement="right" arrow>
              <ListItem disablePadding sx={{ display: 'flex', justifyContent: 'center', mb: 0.5 }}>
                <ListItemButton
                  onClick={() => handleNavigation(item.path)}
                  sx={{
                    borderRadius: 3,
                    minHeight: 48,
                    width: 48,
                    justifyContent: 'center',
                    bgcolor: isActive ? 'primary.main' : 'transparent',
                    color: isActive ? '#fff' : 'text.secondary',
                    '&:hover': {
                      bgcolor: isActive ? 'primary.dark' : 'action.hover',
                    },
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 0, color: 'inherit' }}>
                    {item.icon}
                  </ListItemIcon>
                </ListItemButton>
              </ListItem>
            </Tooltip>
          ) : (
            <ListItem key={item.path} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                sx={{
                  borderRadius: 3,
                  py: 1.2,
                  bgcolor: isActive ? 'primary.main' : 'transparent',
                  color: isActive ? '#fff' : 'text.secondary',
                  '&:hover': {
                    bgcolor: isActive ? 'primary.dark' : 'action.hover',
                  },
                  '& .MuiListItemIcon-root': {
                    color: isActive ? '#fff' : 'text.secondary',
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.label}
                  primaryTypographyProps={{
                    fontSize: '0.875rem',
                    fontWeight: isActive ? 600 : 500,
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      <Divider sx={{ mx: collapsed ? 1 : 2 }} />

      <Box sx={{ px: collapsed ? 1 : 2, py: 2 }}>
        {collapsed ? (
          <Tooltip title="Logout" placement="right" arrow>
            <ListItemButton
              onClick={logout}
              sx={{ borderRadius: 3, justifyContent: 'center', color: 'text.secondary', '&:hover': { bgcolor: 'action.hover', color: 'error.main' } }}
            >
              <LogoutIcon />
            </ListItemButton>
          </Tooltip>
        ) : (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, px: 1, py: 1 }}>
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: 2,
                background: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                fontWeight: 700,
                fontSize: 16,
                flexShrink: 0,
              }}
            >
              {user?.companyName?.[0] || user?.name?.[0] || 'E'}
            </Box>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography sx={{ fontSize: '0.8125rem', fontWeight: 600, color: 'text.primary', truncate: true }}>
                {user?.companyName || user?.name || 'Employer'}
              </Typography>
              <Typography sx={{ fontSize: '0.75rem', color: 'text.secondary', truncate: true }}>
                {user?.email || ''}
              </Typography>
            </Box>
            <IconButton size="small" onClick={logout} sx={{ color: 'text.secondary', '&:hover': { color: 'error.main' } }}>
              <LogoutIcon fontSize="small" />
            </IconButton>
          </Box>
        )}
      </Box>
    </Box>
  ), [collapsed, pathname, user, isMobile, onToggle, handleNavigation, logout]);

  if (isMobile) {
    return (
      <>
        <IconButton
          onClick={() => setMobileOpen(true)}
          sx={{ position: 'fixed', top: 16, left: 16, zIndex: 1200, bgcolor: 'background.paper', boxShadow: 2, '&:hover': { bgcolor: 'background.paper' } }}
        >
          <ChevronRightIcon />
        </IconButton>
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            '& .MuiDrawer-paper': {
              width: SIDEBAR_WIDTH,
              boxSizing: 'border-box',
              borderRight: '1px solid',
              borderColor: 'divider',
            },
          }}
        >
          {drawerContent}
        </Drawer>
      </>
    );
  }

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: currentWidth,
        flexShrink: 0,
        whiteSpace: 'nowrap',
        '& .MuiDrawer-paper': {
          width: currentWidth,
          boxSizing: 'border-box',
          borderRight: '1px solid',
          borderColor: 'divider',
          transition: 'width 0.3s ease',
          overflowX: 'hidden',
        },
      }}
    >
      {drawerContent}
    </Drawer>
  );
}
