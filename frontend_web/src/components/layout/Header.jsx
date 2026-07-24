'use client';
import { useState, useRef } from 'react';
import {
  AppBar,
  Toolbar,
  IconButton,
  Badge,
  Menu,
  MenuItem,
  Typography,
  Box,
  Avatar,
  InputBase,
  ListItemIcon,
  Divider,
  Tooltip,
  Chip,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import NotificationsIcon from '@mui/icons-material/Notifications';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';
import SettingsIcon from '@mui/icons-material/Settings';
import LogoutIcon from '@mui/icons-material/Logout';
import PersonIcon from '@mui/icons-material/Person';
import BusinessIcon from '@mui/icons-material/Business';
import HelpIcon from '@mui/icons-material/Help';
import MenuIcon from '@mui/icons-material/Menu';
import { useAuth } from '@/hooks/useAuth';
import { useContext } from 'react';
import { ThemeContext } from '@/contexts/ThemeContext';
import { NotificationContext } from '@/contexts/NotificationContext';
import { HEADER_HEIGHT } from '@/utils/constants';
import { formatRelativeTime } from '@/utils/formatters';
import { useRouter } from 'next/navigation';
import { styled, alpha } from '@mui/material/styles';

const Search = styled('div')(({ theme }) => ({
  position: 'relative',
  borderRadius: 12,
  backgroundColor: alpha(theme.palette.common.black, 0.04),
  '&:hover': { backgroundColor: alpha(theme.palette.common.black, 0.06) },
  marginRight: theme.spacing(2),
  marginLeft: 0,
  width: '100%',
  maxWidth: 400,
  [theme.breakpoints.down('sm')]: { maxWidth: '100%' },
  transition: 'all 0.2s ease',
  '&:focus-within': {
    boxShadow: `0 0 0 2px ${theme.palette.primary.main}`,
    backgroundColor: alpha(theme.palette.common.black, 0.02),
  },
}));

const SearchIconWrapper = styled('div')(({ theme }) => ({
  padding: theme.spacing(0, 2),
  height: '100%',
  position: 'absolute',
  pointerEvents: 'none',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: theme.palette.text.secondary,
}));

const StyledInputBase = styled(InputBase)(({ theme }) => ({
  color: 'inherit',
  width: '100%',
  '& .MuiInputBase-input': {
    padding: theme.spacing(1.2, 1, 1.2, 0),
    paddingLeft: `calc(1em + ${theme.spacing(4)})`,
    transition: theme.transitions.create('width'),
    width: '100%',
    fontSize: '0.875rem',
  },
}));

export default function Header({ onMenuToggle }) {
  const { user, logout } = useAuth();
  const { mode, toggleTheme } = useContext(ThemeContext);
  const { notifications, unreadCount, markAsRead, markAllAsRead } = useContext(NotificationContext);
  const router = useRouter();

  const [profileAnchor, setProfileAnchor] = useState(null);
  const [notifAnchor, setNotifAnchor] = useState(null);
  const [searchValue, setSearchValue] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchValue.trim()) {
      router.push(`/employer/jobs?search=${encodeURIComponent(searchValue)}`);
    }
  };

  return (
    <AppBar
      position="sticky"
      sx={{
        height: HEADER_HEIGHT,
        zIndex: 1201,
        bgcolor: 'background.paper',
        borderBottom: '1px solid',
        borderColor: 'divider',
      }}
      elevation={0}
    >
      <Toolbar sx={{ height: '100%', minHeight: '56px !important', px: { xs: 2, md: 3 } }}>
        <IconButton
          edge="start"
          onClick={onMenuToggle}
          sx={{ mr: 2, display: { md: 'none' }, color: 'text.secondary' }}
        >
          <MenuIcon />
        </IconButton>

        <Box component="form" onSubmit={handleSearch} sx={{ flex: 1, display: 'flex', alignItems: 'center' }}>
          <Search>
            <SearchIconWrapper>
              <SearchIcon />
            </SearchIconWrapper>
            <StyledInputBase
              placeholder="Search jobs, applicants..."
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
            />
          </Search>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title={mode === 'dark' ? 'Light Mode' : 'Dark Mode'}>
            <IconButton onClick={toggleTheme} sx={{ color: 'text.secondary' }}>
              {mode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>
          </Tooltip>

          <Tooltip title="Notifications">
            <IconButton
              onClick={(e) => setNotifAnchor(e.currentTarget)}
              sx={{ color: 'text.secondary' }}
            >
              <Badge badgeContent={unreadCount} color="error" max={99}>
                <NotificationsIcon />
              </Badge>
            </IconButton>
          </Tooltip>

          <Tooltip title="Profile">
            <IconButton
              onClick={(e) => setProfileAnchor(e.currentTarget)}
              sx={{ ml: 1 }}
            >
              <Avatar
                sx={{
                  width: 36,
                  height: 36,
                  bgcolor: 'primary.main',
                  fontWeight: 600,
                  fontSize: '0.875rem',
                }}
              >
                {user?.companyName?.[0] || user?.name?.[0] || 'E'}
              </Avatar>
            </IconButton>
          </Tooltip>
        </Box>

        <Menu
          anchorEl={notifAnchor}
          open={Boolean(notifAnchor)}
          onClose={() => setNotifAnchor(null)}
          onClick={() => setNotifAnchor(null)}
          PaperProps={{ sx: { width: 360, maxHeight: 480, mt: 1 } }}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        >
          <Box sx={{ px: 2, py: 1.5, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>Notifications</Typography>
            {unreadCount > 0 && (
              <Chip
                label="Mark all read"
                size="small"
                onClick={(e) => { e.stopPropagation(); markAllAsRead(); }}
                sx={{ fontSize: '0.75rem', cursor: 'pointer' }}
              />
            )}
          </Box>
          <Divider />
          {notifications.length === 0 ? (
            <Box sx={{ py: 4, textAlign: 'center' }}>
              <NotificationsIcon sx={{ fontSize: 40, color: 'text.disabled', mb: 1, opacity: 0.5 }} />
              <Typography variant="body2" color="text.secondary">No notifications</Typography>
            </Box>
          ) : (
            notifications.slice(0, 20).map((notif) => (
              <MenuItem
                key={notif.id}
                onClick={() => markAsRead(notif.id)}
                sx={{
                  py: 1.5,
                  px: 2,
                  bgcolor: notif.read ? 'transparent' : 'action.hover',
                  borderBottom: '1px solid',
                  borderColor: 'divider',
                }}
              >
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: notif.read ? 400 : 600, mb: 0.5 }}>
                    {notif.message}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {formatRelativeTime(notif.createdAt)}
                  </Typography>
                </Box>
              </MenuItem>
            ))
          )}
        </Menu>

        <Menu
          anchorEl={profileAnchor}
          open={Boolean(profileAnchor)}
          onClose={() => setProfileAnchor(null)}
          onClick={() => setProfileAnchor(null)}
          PaperProps={{ sx: { width: 240, mt: 1 } }}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        >
          <Box sx={{ px: 2, py: 2, textAlign: 'center' }}>
            <Avatar
              sx={{
                width: 48,
                height: 48,
                bgcolor: 'primary.main',
                fontWeight: 600,
                mx: 'auto',
                mb: 1,
              }}
            >
              {user?.companyName?.[0] || user?.name?.[0] || 'E'}
            </Avatar>
            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
              {user?.companyName || user?.name || 'Employer'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {user?.email || ''}
            </Typography>
          </Box>
          <Divider />
          <MenuItem onClick={() => router.push('/employer/company-profile')}>
            <ListItemIcon><BusinessIcon fontSize="small" /></ListItemIcon>
            Company Profile
          </MenuItem>
          <MenuItem onClick={() => router.push('/employer/settings')}>
            <ListItemIcon><SettingsIcon fontSize="small" /></ListItemIcon>
            Settings
          </MenuItem>
          <MenuItem onClick={() => router.push('/employer/help')}>
            <ListItemIcon><HelpIcon fontSize="small" /></ListItemIcon>
            Help
          </MenuItem>
          <Divider />
          <MenuItem onClick={logout} sx={{ color: 'error.main' }}>
            <ListItemIcon><LogoutIcon fontSize="small" color="error" /></ListItemIcon>
            Logout
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
}
