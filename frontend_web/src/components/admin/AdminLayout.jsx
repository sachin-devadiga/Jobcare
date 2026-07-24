'use client';
import { useState, useEffect } from 'react';
import { Box, AppBar, Toolbar, Typography, IconButton, Badge, Avatar, Menu, MenuItem, ListItemIcon, Divider, Tooltip } from '@mui/material';
import { useRouter, usePathname } from 'next/navigation';
import AdminSidebar from './AdminSidebar';
import { useAdminAuth } from '@/contexts/AdminAuthContext';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import NotificationsIcon from '@mui/icons-material/Notifications';
import LogoutIcon from '@mui/icons-material/Logout';
import MenuIcon from '@mui/icons-material/Menu';
import { HEADER_HEIGHT } from '@/utils/constants';

const pageTitles = {
  '/admin/dashboard': 'Dashboard',
  '/admin/users': 'User Management',
  '/admin/employers': 'Employer Management',
  '/admin/jobs': 'Job Moderation',
  '/admin/applications': 'Application Management',
  '/admin/categories': 'Category Management',
  '/admin/payments': 'Payments & Revenue',
  '/admin/support': 'Support Tickets',
  '/admin/cms': 'Content Management',
  '/admin/analytics': 'Analytics',
  '/admin/settings': 'System Settings',
};

export default function AdminLayout({ children }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { admin, loading, logout } = useAdminAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [profileAnchor, setProfileAnchor] = useState(null);
  const [notifAnchor, setNotifAnchor] = useState(null);

  useEffect(() => {
    if (!loading && !admin) {
      router.push('/admin/login');
    }
  }, [admin, loading, router]);

  useEffect(() => {
    const stored = localStorage.getItem('adminSidebarCollapsed');
    if (stored === 'true') setSidebarCollapsed(true);
  }, []);

  const toggleSidebar = () => {
    const next = !sidebarCollapsed;
    setSidebarCollapsed(next);
    localStorage.setItem('adminSidebarCollapsed', next);
  };

  if (loading) return <LoadingSpinner message="Authenticating..." />;
  if (!admin) return null;

  const currentTitle = Object.entries(pageTitles).find(([key]) => pathname === key || pathname?.startsWith(key + '/'))?.[1] || 'Admin Panel';

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#0F172A' }}>
      <AdminSidebar collapsed={sidebarCollapsed} onToggle={toggleSidebar} />
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, ml: { xs: 0, md: sidebarCollapsed ? '72px' : '260px' }, transition: 'margin-left 0.3s ease' }}>
        <AppBar position="sticky" sx={{ height: HEADER_HEIGHT, zIndex: 1201, bgcolor: '#1E293B', borderBottom: '1px solid rgba(255,255,255,0.06)' }} elevation={0}>
          <Toolbar sx={{ height: '100%', minHeight: '56px !important', px: { xs: 2, md: 3 } }}>
            <IconButton edge="start" onClick={toggleSidebar} sx={{ mr: 2, display: { md: 'none' }, color: '#94A3B8' }}>
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" sx={{ fontWeight: 600, color: '#F1F5F9', flex: 1 }}>{currentTitle}</Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Tooltip title="Notifications">
                <IconButton onClick={(e) => setNotifAnchor(e.currentTarget)} sx={{ color: '#94A3B8' }}>
                  <Badge badgeContent={3} color="error" max={99}><NotificationsIcon /></Badge>
                </IconButton>
              </Tooltip>
              <Tooltip title="Profile">
                <IconButton onClick={(e) => setProfileAnchor(e.currentTarget)}>
                  <Avatar sx={{ width: 36, height: 36, bgcolor: '#818CF8', fontWeight: 600, fontSize: '0.875rem' }}>{admin?.name?.[0] || 'A'}</Avatar>
                </IconButton>
              </Tooltip>
            </Box>
            <Menu anchorEl={notifAnchor} open={Boolean(notifAnchor)} onClose={() => setNotifAnchor(null)} onClick={() => setNotifAnchor(null)}
              PaperProps={{ sx: { width: 360, maxHeight: 480, mt: 1, bgcolor: '#1E293B', color: '#F1F5F9' } }}
              transformOrigin={{ horizontal: 'right', vertical: 'top' }} anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}>
              <Box sx={{ px: 2, py: 1.5 }}><Typography variant="subtitle2" sx={{ fontWeight: 600 }}>Notifications</Typography></Box>
              <Divider sx={{ borderColor: 'rgba(255,255,255,0.06)' }} />
              <Box sx={{ py: 4, textAlign: 'center' }}>
                <NotificationsIcon sx={{ fontSize: 40, color: '#64748B', mb: 1, opacity: 0.5 }} />
                <Typography variant="body2" color="#64748B">No notifications</Typography>
              </Box>
            </Menu>
            <Menu anchorEl={profileAnchor} open={Boolean(profileAnchor)} onClose={() => setProfileAnchor(null)} onClick={() => setProfileAnchor(null)}
              PaperProps={{ sx: { width: 240, mt: 1, bgcolor: '#1E293B', color: '#F1F5F9' } }}
              transformOrigin={{ horizontal: 'right', vertical: 'top' }} anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}>
              <Box sx={{ px: 2, py: 2, textAlign: 'center' }}>
                <Avatar sx={{ width: 48, height: 48, bgcolor: '#818CF8', fontWeight: 600, mx: 'auto', mb: 1 }}>{admin?.name?.[0] || 'A'}</Avatar>
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>{admin?.name || 'Admin'}</Typography>
                <Typography variant="caption" color="#64748B">{admin?.email || ''}</Typography>
              </Box>
              <Divider sx={{ borderColor: 'rgba(255,255,255,0.06)' }} />
              <MenuItem onClick={logout} sx={{ color: '#F87171' }}>
                <ListItemIcon><LogoutIcon fontSize="small" sx={{ color: '#F87171' }} /></ListItemIcon>
                Logout
              </MenuItem>
            </Menu>
          </Toolbar>
        </AppBar>
        <Box component="main" sx={{ flex: 1, p: { xs: 2, sm: 3 }, overflow: 'auto' }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
}
