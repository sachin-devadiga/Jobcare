'use client';
import { useMemo } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import {
  Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText,
  Box, Typography, IconButton, Divider, Tooltip, useMediaQuery, useTheme,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import PeopleIcon from '@mui/icons-material/People';
import BusinessIcon from '@mui/icons-material/Business';
import WorkIcon from '@mui/icons-material/Work';
import DescriptionIcon from '@mui/icons-material/Description';
import CategoryIcon from '@mui/icons-material/Category';
import PaymentsIcon from '@mui/icons-material/Payments';
import SupportAgentIcon from '@mui/icons-material/SupportAgent';
import ArticleIcon from '@mui/icons-material/Article';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import SettingsIcon from '@mui/icons-material/Settings';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import LogoutIcon from '@mui/icons-material/Logout';
import { SIDEBAR_WIDTH, SIDEBAR_COLLAPSED_WIDTH } from '@/utils/constants';
import { useAdminAuth } from '@/contexts/AdminAuthContext';

const menuItems = [
  { label: 'Dashboard', icon: <DashboardIcon />, path: '/admin/dashboard' },
  { label: 'Users', icon: <PeopleIcon />, path: '/admin/users' },
  { label: 'Employers', icon: <BusinessIcon />, path: '/admin/employers' },
  { label: 'Jobs', icon: <WorkIcon />, path: '/admin/jobs' },
  { label: 'Applications', icon: <DescriptionIcon />, path: '/admin/applications' },
  { label: 'Categories', icon: <CategoryIcon />, path: '/admin/categories' },
  { label: 'Payments', icon: <PaymentsIcon />, path: '/admin/payments' },
  { label: 'Support', icon: <SupportAgentIcon />, path: '/admin/support' },
  { label: 'CMS', icon: <ArticleIcon />, path: '/admin/cms' },
  { label: 'Analytics', icon: <AnalyticsIcon />, path: '/admin/analytics' },
  { label: 'Settings', icon: <SettingsIcon />, path: '/admin/settings' },
];

export default function AdminSidebar({ collapsed, onToggle }) {
  const pathname = usePathname();
  const router = useRouter();
  const { admin, logout } = useAdminAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const currentWidth = collapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH;

  const handleNavigation = (path) => {
    router.push(path);
  };

  const drawerContent = useMemo(() => (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden', bgcolor: '#0F172A' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: collapsed ? 'center' : 'space-between', px: collapsed ? 1 : 2.5, py: 2.5, minHeight: 72 }}>
        {!collapsed && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Box sx={{ width: 36, height: 36, borderRadius: 2, background: 'linear-gradient(135deg, #818CF8 0%, #A78BFA 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Typography sx={{ color: '#fff', fontWeight: 800, fontSize: 18 }}>J</Typography>
            </Box>
            <Box>
              <Typography sx={{ fontWeight: 700, fontSize: 18, lineHeight: 1.2, color: '#F1F5F9' }}>JobCare</Typography>
              <Typography sx={{ fontSize: 10, color: '#64748B', letterSpacing: '0.1em', textTransform: 'uppercase' }}>Admin Panel</Typography>
            </Box>
          </Box>
        )}
        {collapsed && (
          <Box sx={{ width: 40, height: 40, borderRadius: 2, background: 'linear-gradient(135deg, #818CF8 0%, #A78BFA 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography sx={{ color: '#fff', fontWeight: 800, fontSize: 20 }}>J</Typography>
          </Box>
        )}
        {!isMobile && (
          <IconButton size="small" onClick={onToggle} sx={{ color: '#64748B' }}>
            {collapsed ? <ChevronRightIcon fontSize="small" /> : <ChevronLeftIcon fontSize="small" />}
          </IconButton>
        )}
      </Box>
      <Divider sx={{ mx: collapsed ? 1 : 2, borderColor: 'rgba(255,255,255,0.06)' }} />
      <List sx={{ flex: 1, overflow: 'auto', py: 1, px: collapsed ? 0.5 : 1 }}>
        {menuItems.map((item) => {
          const isActive = pathname === item.path || pathname?.startsWith(item.path + '/');
          const btn = (
            <ListItemButton
              onClick={() => handleNavigation(item.path)}
              sx={{
                borderRadius: 3, minHeight: 48, justifyContent: collapsed ? 'center' : 'flex-start', px: collapsed ? 0 : 2,
                bgcolor: isActive ? 'rgba(129,140,248,0.15)' : 'transparent',
                color: isActive ? '#818CF8' : '#64748B',
                '&:hover': { bgcolor: isActive ? 'rgba(129,140,248,0.2)' : 'rgba(255,255,255,0.05)' },
                '& .MuiListItemIcon-root': { color: isActive ? '#818CF8' : '#64748B', minWidth: collapsed ? 0 : 40 },
                mb: 0.5,
              }}
            >
              <ListItemIcon sx={{ justifyContent: 'center' }}>{item.icon}</ListItemIcon>
              {!collapsed && (
                <ListItemText primary={item.label} primaryTypographyProps={{ fontSize: '0.875rem', fontWeight: isActive ? 600 : 500 }} />
              )}
            </ListItemButton>
          );
          return collapsed ? (
            <ListItem key={item.path} disablePadding sx={{ display: 'flex', justifyContent: 'center', mb: 0.5 }}>
              <Tooltip title={item.label} placement="right" arrow>{btn}</Tooltip>
            </ListItem>
          ) : (
            <ListItem key={item.path} disablePadding sx={{ mb: 0.5 }}>{btn}</ListItem>
          );
        })}
      </List>
      <Divider sx={{ mx: collapsed ? 1 : 2, borderColor: 'rgba(255,255,255,0.06)' }} />
      <Box sx={{ px: collapsed ? 1 : 2, py: 2 }}>
        {collapsed ? (
          <Tooltip title="Logout" placement="right" arrow>
            <ListItemButton onClick={logout} sx={{ borderRadius: 3, justifyContent: 'center', color: '#64748B', '&:hover': { bgcolor: 'rgba(255,255,255,0.05)', color: '#F87171' } }}>
              <LogoutIcon />
            </ListItemButton>
          </Tooltip>
        ) : (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, px: 1, py: 1 }}>
            <Box sx={{ width: 40, height: 40, borderRadius: 2, background: 'linear-gradient(135deg, #818CF8 0%, #A78BFA 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 700, fontSize: 16, flexShrink: 0 }}>
              {admin?.name?.[0] || 'A'}
            </Box>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography sx={{ fontSize: '0.8125rem', fontWeight: 600, color: '#F1F5F9' }}>{admin?.name || 'Admin'}</Typography>
              <Typography sx={{ fontSize: '0.75rem', color: '#64748B' }}>{admin?.email || ''}</Typography>
            </Box>
            <IconButton size="small" onClick={logout} sx={{ color: '#64748B', '&:hover': { color: '#F87171' } }}>
              <LogoutIcon fontSize="small" />
            </IconButton>
          </Box>
        )}
      </Box>
    </Box>
  ), [collapsed, pathname, admin, isMobile, onToggle, handleNavigation, logout]);

  if (isMobile) {
    return (
      <Drawer
        variant="temporary"
        open={!collapsed}
        onClose={() => onToggle()}
        ModalProps={{ keepMounted: true }}
        sx={{ '& .MuiDrawer-paper': { width: SIDEBAR_WIDTH, boxSizing: 'border-box' } }}
      >
        {drawerContent}
      </Drawer>
    );
  }

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: currentWidth, flexShrink: 0, whiteSpace: 'nowrap',
        '& .MuiDrawer-paper': { width: currentWidth, boxSizing: 'border-box', borderRight: '1px solid rgba(255,255,255,0.06)', transition: 'width 0.3s ease', overflowX: 'hidden', bgcolor: '#0F172A' },
      }}
    >
      {drawerContent}
    </Drawer>
  );
}
