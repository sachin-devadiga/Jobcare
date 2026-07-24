'use client';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
} from '@mui/material';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import { Box } from '@mui/material';

export default function ConfirmDialog({
  open,
  onClose,
  onConfirm,
  title = 'Confirm Action',
  message = 'Are you sure you want to proceed?',
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  severity = 'warning',
  loading = false,
}) {
  const severityColors = {
    warning: { icon: '#F59E0B', btn: 'warning' },
    error: { icon: '#EF4444', btn: 'error' },
    info: { icon: '#3B82F6', btn: 'primary' },
    success: { icon: '#22C55E', btn: 'success' },
  };

  const config = severityColors[severity] || severityColors.warning;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <WarningAmberIcon sx={{ fontSize: 56, color: config.icon, mb: 2 }} />
        <DialogTitle sx={{ pb: 1, pt: 0, textAlign: 'center' }}>{title}</DialogTitle>
        <DialogContent sx={{ pb: 2 }}>
          <DialogContentText sx={{ textAlign: 'center' }}>{message}</DialogContentText>
        </DialogContent>
        <DialogActions sx={{ justifyContent: 'center', gap: 2, pb: 2 }}>
          <Button
            variant="outlined"
            onClick={onClose}
            disabled={loading}
            sx={{ minWidth: 120 }}
          >
            {cancelText}
          </Button>
          <Button
            variant="contained"
            color={config.btn}
            onClick={onConfirm}
            disabled={loading}
            sx={{ minWidth: 120 }}
          >
            {loading ? 'Processing...' : confirmText}
          </Button>
        </DialogActions>
      </Box>
    </Dialog>
  );
}
