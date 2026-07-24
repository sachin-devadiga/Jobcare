'use client';
import { useState, useEffect, useCallback } from 'react';
import { Box, Typography, TextField, Button, Chip, MenuItem, InputAdornment, Grid, Alert, LinearProgress } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import FlagIcon from '@mui/icons-material/Flag';
import DataTable from '@/components/admin/DataTable';
import StatusBadge from '@/components/admin/StatusBadge';
import JobDetailModal from '@/components/admin/JobDetailModal';
import ConfirmDialog from '@/components/admin/ConfirmDialog';
import { formatDate, formatJobType } from '@/utils/formatters';
import adminService from '@/services/adminService';
import { toast } from 'react-toastify';
import { DatePicker } from '@mui/x-date-pickers';

export default function AdminJobsPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [dateFrom, setDateFrom] = useState(null);
  const [dateTo, setDateTo] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [total, setTotal] = useState(0);
  const [selected, setSelected] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [categories, setCategories] = useState([]);
  const [confirmDialog, setConfirmDialog] = useState({ open: false, type: '' });

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = { page: page + 1, limit: rowsPerPage, search, status: statusFilter !== 'all' ? statusFilter : undefined, category: categoryFilter !== 'all' ? categoryFilter : undefined };
      if (dateFrom) params.dateFrom = dateFrom.toISOString();
      if (dateTo) params.dateTo = dateTo.toISOString();
      const { data } = await adminService.getJobs(params);
      setJobs(data.jobs || data.data || data || []);
      setTotal(data.total || 0);
    } catch (err) {
      setError(err.message || 'Failed to load jobs');
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage, search, statusFilter, categoryFilter, dateFrom, dateTo]);

  useEffect(() => { fetchJobs(); }, [fetchJobs]);

  useEffect(() => {
    adminService.getCategories({ limit: 100 }).then(({ data }) => setCategories(data.categories || data || [])).catch(() => {});
  }, []);

  const handleBulk = async (action) => {
    try {
      const actions = { approve: adminService.bulkApproveJobs, reject: adminService.bulkRejectJobs, feature: adminService.bulkFeatureJobs, remove: adminService.bulkRemoveJobs };
      if (actions[action]) {
        await actions[action](selected);
        toast.success(`${selected.length} jobs ${action}d`);
      }
      setSelected([]);
      setConfirmDialog({ open: false, type: '' });
      fetchJobs();
    } catch (err) { toast.error(err.message || `Failed to ${action} jobs`); }
  };

  const columns = [
    { key: 'title', label: 'Title', sortable: true, render: (row) => <Box><Typography variant="body2" sx={{ fontWeight: 600, color: '#F1F5F9' }}>{row.title}</Typography><Typography variant="caption" sx={{ color: '#64748B' }}>{row.company?.companyName || row.companyName}</Typography></Box> },
    { key: 'category', label: 'Category', render: (row) => <Typography variant="body2" sx={{ color: '#94A3B8' }}>{row.category?.name || row.category || '-'}</Typography> },
    { key: 'status', label: 'Status', render: (row) => <StatusBadge status={row.status} /> },
    { key: 'applications', label: 'Apps', render: (row) => <Typography variant="body2" sx={{ color: '#94A3B8' }}>{row.applicationCount || row.applicationsCount || 0}</Typography> },
    { key: 'aiScore', label: 'AI Score', render: (row) => row.aiModerationScore != null ? (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <LinearProgress variant="determinate" value={row.aiModerationScore * 10} sx={{ width: 60, height: 6, borderRadius: 3, bgcolor: 'rgba(255,255,255,0.06)', '& .MuiLinearProgress-bar': { bgcolor: row.aiModerationScore >= 7 ? '#4ADE80' : row.aiModerationScore >= 4 ? '#FBBF24' : '#F87171' } }} />
        <Typography variant="caption" sx={{ color: '#94A3B8' }}>{row.aiModerationScore}/10</Typography>
      </Box>
    ) : <Typography variant="caption" sx={{ color: '#64748B' }}>-</Typography> },
    { key: 'isFlagged', label: 'Flagged', render: (row) => row.isFlagged ? <FlagIcon sx={{ color: '#F87171', fontSize: 18 }} /> : '-' },
    { key: 'createdAt', label: 'Posted', sortable: true, render: (row) => <Typography variant="body2" sx={{ color: '#94A3B8' }}>{formatDate(row.createdAt)}</Typography> },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 700, color: '#F1F5F9' }}>Job Moderation</Typography>
      </Box>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <TextField fullWidth placeholder="Search jobs..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(0); }}
            sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } } }}
            InputProps={{ startAdornment: <InputAdornment position="start"><SearchIcon sx={{ color: '#64748B' }} /></InputAdornment> }} />
        </Grid>
        <Grid item xs={6} md={2}>
          <TextField select fullWidth label="Status" value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(0); }}
            sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }}>
            <MenuItem value="all">All Status</MenuItem>
            <MenuItem value="active">Active</MenuItem>
            <MenuItem value="paused">Paused</MenuItem>
            <MenuItem value="closed">Closed</MenuItem>
            <MenuItem value="filled">Filled</MenuItem>
            <MenuItem value="flagged">Flagged</MenuItem>
            <MenuItem value="draft">Draft</MenuItem>
          </TextField>
        </Grid>
        <Grid item xs={6} md={2}>
          <TextField select fullWidth label="Category" value={categoryFilter} onChange={(e) => { setCategoryFilter(e.target.value); setPage(0); }}
            sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }}>
            <MenuItem value="all">All Categories</MenuItem>
            {categories.map((cat) => <MenuItem key={cat._id || cat.id} value={cat._id || cat.id || cat.name}>{cat.name}</MenuItem>)}
          </TextField>
        </Grid>
      </Grid>

      {error && <Alert severity="error" sx={{ mb: 2, borderRadius: 2, bgcolor: 'rgba(248,113,113,0.15)', color: '#F87171' }}>{error}</Alert>}

      <DataTable columns={columns} rows={jobs} loading={loading} onRetry={fetchJobs}
        selectable selected={selected} onSelectionChange={setSelected}
        page={page} rowsPerPage={rowsPerPage} total={total}
        onPageChange={setPage} onRowsPerPageChange={setRowsPerPage}
        onRowClick={(row) => { setSelectedJobId(row._id || row.id); setModalOpen(true); }}
        emptyTitle="No jobs found" emptyDescription="Try adjusting your filters"
        bulkActions={
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Chip label="Approve" size="small" onClick={() => setConfirmDialog({ open: true, type: 'approve' })} sx={{ color: '#4ADE80', bgcolor: 'rgba(74,222,128,0.15)', cursor: 'pointer' }} />
            <Chip label="Reject" size="small" onClick={() => setConfirmDialog({ open: true, type: 'reject' })} sx={{ color: '#F87171', bgcolor: 'rgba(248,113,113,0.15)', cursor: 'pointer' }} />
            <Chip label="Feature" size="small" onClick={() => setConfirmDialog({ open: true, type: 'feature' })} sx={{ color: '#FBBF24', bgcolor: 'rgba(251,191,36,0.15)', cursor: 'pointer' }} />
            <Chip label="Remove" size="small" onClick={() => setConfirmDialog({ open: true, type: 'remove' })} sx={{ color: '#F87171', bgcolor: 'rgba(248,113,113,0.15)', cursor: 'pointer' }} />
          </Box>
        } />

      <JobDetailModal open={modalOpen} onClose={() => { setModalOpen(false); setSelectedJobId(null); }} jobId={selectedJobId} onAction={fetchJobs} />

      <ConfirmDialog open={confirmDialog.open} onClose={() => setConfirmDialog({ open: false, type: '' })}
        onConfirm={() => handleBulk(confirmDialog.type)}
        title={`${confirmDialog.type.charAt(0).toUpperCase() + confirmDialog.type.slice(1)} Jobs`}
        message={`Are you sure you want to ${confirmDialog.type} ${selected.length} selected jobs?`}
        severity={confirmDialog.type === 'remove' ? 'error' : confirmDialog.type === 'reject' ? 'warning' : 'info'} />
    </Box>
  );
}
