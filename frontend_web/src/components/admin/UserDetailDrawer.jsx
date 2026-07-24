'use client';
import { useState, useEffect } from 'react';
import {
  Drawer, Box, Typography, IconButton, Avatar, Divider, Chip, Button,
  List, ListItem, ListItemText, CircularProgress, Tooltip,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import BlockIcon from '@mui/icons-material/Block';
import DeleteIcon from '@mui/icons-material/Delete';
import VerifiedIcon from '@mui/icons-material/Verified';
import EmailIcon from '@mui/icons-material/Email';
import PhoneIcon from '@mui/icons-material/Phone';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import BadgeIcon from '@mui/icons-material/Badge';
import adminService from '@/services/adminService';
import { formatDate, formatDateTime } from '@/utils/formatters';
import StatusBadge from './StatusBadge';
import ConfirmDialog from './ConfirmDialog';
import { toast } from 'react-toastify';

export default function UserDetailDrawer({ open, onClose, userId, onAction }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [confirmDialog, setConfirmDialog] = useState({ open: false, type: '' });

  useEffect(() => {
    if (open && userId) {
      fetchUser();
    }
  }, [open, userId]);

  const fetchUser = async () => {
    setLoading(true);
    try {
      const { data } = await adminService.getUserById(userId);
      setUser(data);
    } catch (err) {
      toast.error('Failed to load user details');
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (action) => {
    try {
      await adminService.updateUser(userId, { action });
      toast.success(`User ${action}d successfully`);
      setConfirmDialog({ open: false, type: '' });
      onAction?.();
      fetchUser();
    } catch (err) {
      toast.error(err.message || `Failed to ${action} user`);
    }
  };

  return (
    <>
      <Drawer anchor="right" open={open} onClose={onClose}
        PaperProps={{ sx: { width: { xs: '100%', sm: 480 }, bgcolor: '#1E293B', color: '#F1F5F9' } }}>
        <Box sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>User Details</Typography>
          <IconButton onClick={onClose} sx={{ color: '#64748B' }}><CloseIcon /></IconButton>
        </Box>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}><CircularProgress /></Box>
        ) : user ? (
          <Box sx={{ overflow: 'auto', flex: 1 }}>
            <Box sx={{ p: 3, textAlign: 'center', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
              <Avatar src={user.avatar} sx={{ width: 80, height: 80, mx: 'auto', mb: 2, bgcolor: '#818CF8', fontSize: 32 }}>
                {(user.name?.[0] || user.email?.[0] || 'U').toUpperCase()}
              </Avatar>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>{user.name || 'N/A'}</Typography>
              <Typography variant="body2" sx={{ color: '#64748B', mb: 1 }}>{user.email}</Typography>
              <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                <StatusBadge status={user.role} />
                <StatusBadge status={user.status} />
                {user.isVerified && <Chip icon={<VerifiedIcon />} label="Verified" size="small" sx={{ bgcolor: 'rgba(74,222,128,0.15)', color: '#4ADE80', fontWeight: 600 }} />}
              </Box>
            </Box>

            <Box sx={{ p: 3 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.05em', fontSize: '0.75rem' }}>Contact Information</Typography>
              <List dense disablePadding>
                <ListItem sx={{ px: 0, py: 1 }}>
                  <EmailIcon sx={{ fontSize: 20, color: '#64748B', mr: 2 }} />
                  <ListItemText primary="Email" secondary={user.email} primaryTypographyProps={{ variant: 'caption', color: '#64748B' }} secondaryTypographyProps={{ color: '#F1F5F9' }} />
                </ListItem>
                <ListItem sx={{ px: 0, py: 1 }}>
                  <PhoneIcon sx={{ fontSize: 20, color: '#64748B', mr: 2 }} />
                  <ListItemText primary="Phone" secondary={user.phone || '-'} primaryTypographyProps={{ variant: 'caption', color: '#64748B' }} secondaryTypographyProps={{ color: '#F1F5F9' }} />
                </ListItem>
              </List>
            </Box>

            <Box sx={{ px: 3, pb: 2 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.05em', fontSize: '0.75rem' }}>Account Details</Typography>
              <List dense disablePadding>
                <ListItem sx={{ px: 0, py: 1 }}>
                  <BadgeIcon sx={{ fontSize: 20, color: '#64748B', mr: 2 }} />
                  <ListItemText primary="Role" secondary={user.role} primaryTypographyProps={{ variant: 'caption', color: '#64748B' }} secondaryTypographyProps={{ color: '#F1F5F9' }} />
                </ListItem>
                <ListItem sx={{ px: 0, py: 1 }}>
                  <CalendarTodayIcon sx={{ fontSize: 20, color: '#64748B', mr: 2 }} />
                  <ListItemText primary="Joined" secondary={formatDate(user.createdAt)} primaryTypographyProps={{ variant: 'caption', color: '#64748B' }} secondaryTypographyProps={{ color: '#F1F5F9' }} />
                </ListItem>
              </List>
            </Box>

            {user.activityLog && user.activityLog.length > 0 && (
              <Box sx={{ px: 3, pb: 2 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.05em', fontSize: '0.75rem' }}>Activity Log</Typography>
                <List dense>
                  {user.activityLog.slice(0, 10).map((log, i) => (
                    <ListItem key={i} sx={{ px: 0, py: 0.5 }}>
                      <ListItemText primary={log.action} secondary={formatDateTime(log.createdAt)} primaryTypographyProps={{ variant: 'body2', color: '#F1F5F9' }} secondaryTypographyProps={{ variant: 'caption', color: '#64748B' }} />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            <Box sx={{ p: 3, borderTop: '1px solid rgba(255,255,255,0.06)', display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Tooltip title="Activate user"><Button size="small" variant="contained" color="success" startIcon={<CheckCircleIcon />}
                onClick={() => setConfirmDialog({ open: true, type: 'activate' })}>Activate</Button></Tooltip>
              <Tooltip title="Deactivate user"><Button size="small" variant="contained" color="warning" startIcon={<BlockIcon />}
                onClick={() => setConfirmDialog({ open: true, type: 'deactivate' })}>Deactivate</Button></Tooltip>
              <Tooltip title="Verify user"><Button size="small" variant="contained" color="info" startIcon={<VerifiedIcon />}
                onClick={() => setConfirmDialog({ open: true, type: 'verify' })}>Verify</Button></Tooltip>
              <Tooltip title="Delete user"><Button size="small" variant="contained" color="error" startIcon={<DeleteIcon />}
                onClick={() => setConfirmDialog({ open: true, type: 'delete' })}>Delete</Button></Tooltip>
            </Box>
          </Box>
        ) : null}
      </Drawer>

      <ConfirmDialog
        open={confirmDialog.open}
        onClose={() => setConfirmDialog({ open: false, type: '' })}
        onConfirm={() => handleAction(confirmDialog.type)}
        title={`${confirmDialog.type.charAt(0).toUpperCase() + confirmDialog.type.slice(1)} User`}
        message={`Are you sure you want to ${confirmDialog.type} this user?`}
        severity={confirmDialog.type === 'delete' ? 'error' : confirmDialog.type === 'deactivate' ? 'warning' : 'info'}
      />
    </>
  );
}
