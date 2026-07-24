'use client';
import { useState, useEffect, useCallback } from 'react';
import { Box, Typography, TextField, Button, Chip, MenuItem, InputAdornment, Grid, Alert, Dialog, DialogTitle, DialogContent, DialogActions, LinearProgress } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import DataTable from '@/components/admin/DataTable';
import StatusBadge from '@/components/admin/StatusBadge';
import { formatDate, formatDateTime } from '@/utils/formatters';
import adminService from '@/services/adminService';
import { toast } from 'react-toastify';

export default function AdminApplicationsPage() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [total, setTotal] = useState(0);
  const [selected, setSelected] = useState([]);
  const [detailOpen, setDetailOpen] = useState(false);
  const [selectedApp, setSelectedApp] = useState(null);
  const [duplicates, setDuplicates] = useState([]);
  const [spamAlerts, setSpamAlerts] = useState([]);

  const fetchApplications = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = { page: page + 1, limit: rowsPerPage, search, status: statusFilter !== 'all' ? statusFilter : undefined };
      const { data } = await adminService.getApplications(params);
      setApplications(data.applications || data.data || data || []);
      setTotal(data.total || 0);
    } catch (err) {
      setError(err.message || 'Failed to load applications');
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage, search, statusFilter]);

  useEffect(() => { fetchApplications(); }, [fetchApplications]);

  useEffect(() => {
    adminService.getDuplicateApplications({ limit: 5 }).then(({ data }) => setDuplicates(data || [])).catch(() => {});
    adminService.getSpamApplications({ limit: 5 }).then(({ data }) => setSpamAlerts(data || [])).catch(() => {});
  }, []);

  const openDetail = async (app) => {
    setSelectedApp(app);
    setDetailOpen(true);
  };

  const handleMarkSpam = async (id) => {
    try {
      await adminService.markSpam(id);
      toast.success('Marked as spam');
      setDetailOpen(false);
      fetchApplications();
    } catch (err) { toast.error(err.message || 'Failed'); }
  };

  const columns = [
    { key: 'applicant', label: 'Applicant', render: (row) => <Box><Typography variant="body2" sx={{ fontWeight: 600, color: '#F1F5F9' }}>{row.applicant?.name || row.name || 'N/A'}</Typography><Typography variant="caption" sx={{ color: '#64748B' }}>{row.applicant?.email || row.email}</Typography></Box> },
    { key: 'job', label: 'Job', render: (row) => <Typography variant="body2" sx={{ color: '#F1F5F9' }}>{row.job?.title || row.jobTitle || 'N/A'}</Typography> },
    { key: 'status', label: 'Status', render: (row) => <StatusBadge status={row.status} /> },
    { key: 'matchScore', label: 'AI Match', render: (row) => row.matchScore != null ? (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <LinearProgress variant="determinate" value={row.matchScore} sx={{ width: 60, height: 6, borderRadius: 3, bgcolor: 'rgba(255,255,255,0.06)', '& .MuiLinearProgress-bar': { bgcolor: row.matchScore >= 70 ? '#4ADE80' : row.matchScore >= 40 ? '#FBBF24' : '#F87171' } }} />
        <Typography variant="caption" sx={{ color: '#94A3B8' }}>{row.matchScore}%</Typography>
      </Box>
    ) : <Typography variant="caption" sx={{ color: '#64748B' }}>-</Typography> },
    { key: 'isDuplicate', label: 'Duplicate', render: (row) => row.isDuplicate ? <Chip icon={<WarningAmberIcon />} label="Duplicate" size="small" sx={{ bgcolor: 'rgba(251,191,36,0.15)', color: '#FBBF24' }} /> : '-' },
    { key: 'isSpam', label: 'Spam', render: (row) => row.isSpam ? <Chip icon={<WarningAmberIcon />} label="SPAM" size="small" sx={{ bgcolor: 'rgba(248,113,113,0.15)', color: '#F87171' }} /> : '-' },
    { key: 'createdAt', label: 'Applied', sortable: true, render: (row) => <Typography variant="body2" sx={{ color: '#94A3B8' }}>{formatDate(row.createdAt)}</Typography> },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 700, color: '#F1F5F9' }}>Application Management</Typography>
      </Box>

      {(duplicates.length > 0 || spamAlerts.length > 0) && (
        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          {duplicates.length > 0 && (
            <Alert severity="warning" sx={{ flex: 1, borderRadius: 2, bgcolor: 'rgba(251,191,36,0.1)', color: '#FBBF24' }}>
              {duplicates.length} duplicate application(s) detected. <Button size="small" sx={{ color: '#FBBF24', textDecoration: 'underline' }} onClick={() => {}}>Review</Button>
            </Alert>
          )}
          {spamAlerts.length > 0 && (
            <Alert severity="error" sx={{ flex: 1, borderRadius: 2, bgcolor: 'rgba(248,113,113,0.1)', color: '#F87171' }}>
              {spamAlerts.length} spam application(s) detected. <Button size="small" sx={{ color: '#F87171', textDecoration: 'underline' }} onClick={() => setStatusFilter('spam')}>Review</Button>
            </Alert>
          )}
        </Box>
      )}

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <TextField fullWidth placeholder="Search by applicant, job..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(0); }}
            sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } } }}
            InputProps={{ startAdornment: <InputAdornment position="start"><SearchIcon sx={{ color: '#64748B' }} /></InputAdornment> }} />
        </Grid>
        <Grid item xs={6} md={3}>
          <TextField select fullWidth label="Status" value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(0); }}
            sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }}>
            <MenuItem value="all">All Status</MenuItem>
            <MenuItem value="new">New</MenuItem>
            <MenuItem value="reviewing">Reviewing</MenuItem>
            <MenuItem value="shortlisted">Shortlisted</MenuItem>
            <MenuItem value="rejected">Rejected</MenuItem>
            <MenuItem value="spam">Spam</MenuItem>
          </TextField>
        </Grid>
      </Grid>

      {error && <Alert severity="error" sx={{ mb: 2, borderRadius: 2, bgcolor: 'rgba(248,113,113,0.15)', color: '#F87171' }}>{error}</Alert>}

      <DataTable columns={columns} rows={applications} loading={loading} onRetry={fetchApplications}
        selectable selected={selected} onSelectionChange={setSelected}
        page={page} rowsPerPage={rowsPerPage} total={total}
        onPageChange={setPage} onRowsPerPageChange={setRowsPerPage}
        onRowClick={(row) => openDetail(row)}
        emptyTitle="No applications found" emptyDescription="No applications match your criteria" />

      <Dialog open={detailOpen} onClose={() => setDetailOpen(false)} maxWidth="sm" fullWidth
        PaperProps={{ sx: { bgcolor: '#1E293B', color: '#F1F5F9', borderRadius: 3 } }}>
        <DialogTitle sx={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>Application Details</Typography>
        </DialogTitle>
        <DialogContent sx={{ pt: 3 }}>
          {selectedApp && (
            <Box>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mb: 3 }}>
                <Box><Typography variant="caption" sx={{ color: '#64748B' }}>Applicant</Typography><Typography variant="body2" sx={{ color: '#F1F5F9' }}>{selectedApp.applicant?.name || selectedApp.name}</Typography></Box>
                <Box><Typography variant="caption" sx={{ color: '#64748B' }}>Email</Typography><Typography variant="body2" sx={{ color: '#F1F5F9' }}>{selectedApp.applicant?.email || selectedApp.email}</Typography></Box>
                <Box><Typography variant="caption" sx={{ color: '#64748B' }}>Job</Typography><Typography variant="body2" sx={{ color: '#F1F5F9' }}>{selectedApp.job?.title || selectedApp.jobTitle}</Typography></Box>
                <Box><Typography variant="caption" sx={{ color: '#64748B' }}>Status</Typography><Box><StatusBadge status={selectedApp.status} /></Box></Box>
                <Box><Typography variant="caption" sx={{ color: '#64748B' }}>Applied</Typography><Typography variant="body2" sx={{ color: '#F1F5F9' }}>{formatDateTime(selectedApp.createdAt)}</Typography></Box>
                <Box><Typography variant="caption" sx={{ color: '#64748B' }}>AI Match Score</Typography>
                  {selectedApp.matchScore != null ? (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <LinearProgress variant="determinate" value={selectedApp.matchScore} sx={{ flex: 1, height: 8, borderRadius: 4, bgcolor: 'rgba(255,255,255,0.06)', '& .MuiLinearProgress-bar': { bgcolor: selectedApp.matchScore >= 70 ? '#4ADE80' : selectedApp.matchScore >= 40 ? '#FBBF24' : '#F87171' } }} />
                      <Typography variant="body2" sx={{ color: '#F1F5F9', fontWeight: 600 }}>{selectedApp.matchScore}%</Typography>
                    </Box>
                  ) : <Typography variant="body2" sx={{ color: '#64748B' }}>N/A</Typography>}
                </Box>
              </Box>

              {selectedApp.isDuplicate && (
                <Alert severity="warning" sx={{ mb: 2, borderRadius: 2, bgcolor: 'rgba(251,191,36,0.1)', color: '#FBBF24' }}>
                  This application appears to be a duplicate.
                </Alert>
              )}
              {selectedApp.isSpam && (
                <Alert severity="error" sx={{ mb: 2, borderRadius: 2, bgcolor: 'rgba(248,113,113,0.1)', color: '#F87171' }}>
                  This application has been flagged as spam.
                </Alert>
              )}

              {selectedApp.coverLetter && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: '#94A3B8' }}>Cover Letter</Typography>
                  <Typography variant="body2" sx={{ color: '#CBD5E1', whiteSpace: 'pre-wrap' }}>{selectedApp.coverLetter}</Typography>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 2, borderTop: '1px solid rgba(255,255,255,0.06)', gap: 1 }}>
          {!selectedApp?.isSpam && (
            <Button color="error" onClick={() => handleMarkSpam(selectedApp._id || selectedApp.id)} sx={{ color: '#F87171' }}>Mark as Spam</Button>
          )}
          <Button onClick={() => setDetailOpen(false)} sx={{ color: '#94A3B8' }}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
