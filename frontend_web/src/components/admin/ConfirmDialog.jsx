'use client';
import { Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Button, Box } from '@mui/material';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';

export default function ConfirmDialog({ open, onClose, onConfirm, title = 'Confirm Action', message = 'Are you sure you want to proceed?', confirmText = 'Confirm', cancelText = 'Cancel', severity = 'warning', loading = false }) {
  const severityColors = {
    warning: { icon: '#FBBF24', btn: 'warning' },
    error: { icon: '#F87171', btn: 'error' },
    info: { icon: '#60A5FA', btn: 'primary' },
    success: { icon: '#4ADE80', btn: 'success' },
  };
  const config = severityColors[severity] || severityColors.warning;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth
      PaperProps={{ sx: { bgcolor: '#1E293B', color: '#F1F5F9', borderRadius: 3 } }}>
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <WarningAmberIcon sx={{ fontSize: 56, color: config.icon, mb: 2 }} />
        <DialogTitle sx={{ pb: 1, pt: 0, textAlign: 'center', color: '#F1F5F9' }}>{title}</DialogTitle>
        <DialogContent sx={{ pb: 2 }}>
          <DialogContentText sx={{ textAlign: 'center', color: '#94A3B8' }}>{message}</DialogContentText>
        </DialogContent>
        <DialogActions sx={{ justifyContent: 'center', gap: 2, pb: 2 }}>
          <Button variant="outlined" onClick={onClose} disabled={loading}
            sx={{ minWidth: 120, borderColor: 'rgba(255,255,255,0.12)', color: '#94A3B8', '&:hover': { borderColor: 'rgba(255,255,255,0.2)', bgcolor: 'rgba(255,255,255,0.05)' } }}>
            {cancelText}
          </Button>
          <Button variant="contained" color={config.btn} onClick={onConfirm} disabled={loading} sx={{ minWidth: 120 }}>
            {loading ? 'Processing...' : confirmText}
          </Button>
        </DialogActions>
      </Box>
    </Dialog>
  );
}
