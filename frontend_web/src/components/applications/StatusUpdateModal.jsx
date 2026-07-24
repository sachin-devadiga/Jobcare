'use client';
import { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions, Button,
  TextField, MenuItem, Typography, Box, CircularProgress,
} from '@mui/material';
import { APPLICATION_STATUS } from '@/utils/constants';

const statusOptions = Object.entries(APPLICATION_STATUS).map(([key, val]) => ({
  value: val,
  label: val.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()),
}));

export default function StatusUpdateModal({ open, onClose, currentStatus, onSubmit, loading = false }) {
  const [status, setStatus] = useState(currentStatus || 'new');
  const [notes, setNotes] = useState('');

  const handleSubmit = () => {
    onSubmit(status, notes);
    setNotes('');
    onClose();
  };

  const handleClose = () => {
    if (!loading) onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="xs" fullWidth>
      <DialogTitle sx={{ pb: 1 }}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>Update Application Status</Typography>
      </DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 1 }}>
          <TextField
            fullWidth
            select
            label="Status"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            sx={{ mb: 2.5 }}
          >
            {statusOptions.map((opt) => (
              <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
            ))}
          </TextField>
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Notes (optional)"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Add internal notes about this status change..."
          />
        </Box>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={handleClose} disabled={loading}>Cancel</Button>
        <Button variant="contained" onClick={handleSubmit} disabled={loading}>
          {loading ? <CircularProgress size={20} sx={{ color: '#fff' }} /> : 'Update Status'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
