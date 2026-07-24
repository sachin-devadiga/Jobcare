'use client';
import { useState, useEffect, useCallback } from 'react';
import { Box, Typography, TextField, Button, Chip, MenuItem, InputAdornment, Grid, Alert, Dialog, DialogTitle, DialogContent, DialogActions, Tabs, Tab, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import DataTable from '@/components/admin/DataTable';
import StatusBadge from '@/components/admin/StatusBadge';
import { formatDate, formatCurrency } from '@/utils/formatters';
import adminService from '@/services/adminService';
import { toast } from 'react-toastify';

export default function AdminEmployersPage() {
  const [employers, setEmployers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [verificationFilter, setVerificationFilter] = useState('all');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [total, setTotal] = useState(0);
  const [selected, setSelected] = useState([]);
  const [detailOpen, setDetailOpen] = useState(false);
  const [selectedEmployer, setSelectedEmployer] = useState(null);
  const [employerJobs, setEmployerJobs] = useState([]);
  const [detailTab, setDetailTab] = useState(0);
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState('');

  const fetchEmployers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = { page: page + 1, limit: rowsPerPage, search, status: statusFilter !== 'all' ? statusFilter : undefined, verificationStatus: verificationFilter !== 'all' ? verificationFilter : undefined };
      const { data } = await adminService.getEmployers(params);
      setEmployers(data.employers || data.data || data || []);
      setTotal(data.total || 0);
    } catch (err) {
      setError(err.message || 'Failed to load employers');
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage, search, statusFilter, verificationFilter]);

  useEffect(() => { fetchEmployers(); }, [fetchEmployers]);

  const handleVerify = async (id) => {
    try {
      await adminService.verifyEmployer(id, {});
      toast.success('Employer verified successfully');
      fetchEmployers();
    } catch (err) { toast.error(err.message || 'Failed to verify'); }
  };

  const handleReject = async () => {
    if (!selectedEmployer || !rejectReason) return;
    try {
      await adminService.rejectEmployer(selectedEmployer._id || selectedEmployer.id, { reason: rejectReason });
      toast.success('Employer rejected');
      setRejectDialogOpen(false);
      setRejectReason('');
      setDetailOpen(false);
      fetchEmployers();
    } catch (err) { toast.error(err.message || 'Failed to reject'); }
  };

  const handleBulkVerify = async () => {
    try {
      await adminService.bulkVerifyEmployers(selected);
      toast.success(`${selected.length} employers verified`);
      setSelected([]);
      fetchEmployers();
    } catch (err) { toast.error(err.message || 'Bulk verify failed'); }
  };

  const openDetail = async (row) => {
    setSelectedEmployer(row);
    setDetailTab(0);
    setDetailOpen(true);
    try {
      const { data } = await adminService.getEmployerJobs(row._id || row.id, { limit: 50 });
      setEmployerJobs(data.jobs || data || []);
    } catch {}
  };

  const columns = [
    { key: 'companyName', label: 'Company', sortable: true, render: (row) => <Box><Typography variant="body2" sx={{ fontWeight: 600, color: '#F1F5F9' }}>{row.companyName || row.company?.companyName || 'N/A'}</Typography><Typography variant="caption" sx={{ color: '#64748B' }}>{row.industry || ''}</Typography></Box> },
    { key: 'owner', label: 'Owner', render: (row) => <Typography variant="body2" sx={{ color: '#F1F5F9' }}>{row.owner?.name || row.name || 'N/A'}</Typography> },
    { key: 'employeeCount', label: 'Employees', render: (row) => <Typography variant="body2" sx={{ color: '#94A3B8' }}>{row.employeeCount || row.employeesCount || '-'}</Typography> },
    { key: 'jobCount', label: 'Jobs Posted', render: (row) => <Typography variant="body2" sx={{ color: '#94A3B8' }}>{row.jobCount || row.jobsCount || 0}</Typography> },
    { key: 'verificationStatus', label: 'Verification', render: (row) => <StatusBadge status={row.verificationStatus || (row.isVerified ? 'verified' : 'pending')} /> },
    { key: 'subscription', label: 'Subscription', render: (row) => <StatusBadge status={row.subscription?.plan || row.plan || 'free'} /> },
    { key: 'createdAt', label: 'Joined', sortable: true, render: (row) => <Typography variant="body2" sx={{ color: '#94A3B8' }}>{formatDate(row.createdAt)}</Typography> },
    { key: 'actions', label: 'Actions', render: (row) => (
      <Box sx={{ display: 'flex', gap: 0.5 }}>
        {(!row.isVerified && row.verificationStatus !== 'verified') && (
          <>
            <Chip icon={<CheckCircleIcon />} label="Verify" size="small" onClick={(e) => { e.stopPropagation(); handleVerify(row._id || row.id); }} sx={{ color: '#4ADE80', bgcolor: 'rgba(74,222,128,0.15)', cursor: 'pointer' }} />
            <Chip icon={<CancelIcon />} label="Reject" size="small" onClick={(e) => { e.stopPropagation(); setSelectedEmployer(row); setRejectDialogOpen(true); }} sx={{ color: '#F87171', bgcolor: 'rgba(248,113,113,0.15)', cursor: 'pointer' }} />
          </>
        )}
        <Chip label="View" size="small" onClick={(e) => { e.stopPropagation(); openDetail(row); }} sx={{ color: '#60A5FA', bgcolor: 'rgba(96,165,250,0.15)', cursor: 'pointer' }} />
      </Box>
    )},
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 700, color: '#F1F5F9' }}>Employer Management</Typography>
        {selected.length > 0 && (
          <Button variant="contained" color="success" startIcon={<CheckCircleIcon />} onClick={handleBulkVerify}
            sx={{ bgcolor: 'rgba(74,222,128,0.15)', color: '#4ADE80', '&:hover': { bgcolor: 'rgba(74,222,128,0.25)' } }}>
            Verify {selected.length} Selected
          </Button>
        )}
      </Box>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <TextField fullWidth placeholder="Search by company, owner..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(0); }}
            sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } } }}
            InputProps={{ startAdornment: <InputAdornment position="start"><SearchIcon sx={{ color: '#64748B' }} /></InputAdornment> }} />
        </Grid>
        <Grid item xs={6} md={3}>
          <TextField select fullWidth label="Status" value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(0); }}
            sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }}>
            <MenuItem value="all">All Status</MenuItem>
            <MenuItem value="active">Active</MenuItem>
            <MenuItem value="inactive">Inactive</MenuItem>
            <MenuItem value="banned">Banned</MenuItem>
          </TextField>
        </Grid>
        <Grid item xs={6} md={3}>
          <TextField select fullWidth label="Verification" value={verificationFilter} onChange={(e) => { setVerificationFilter(e.target.value); setPage(0); }}
            sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }}>
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="verified">Verified</MenuItem>
            <MenuItem value="pending">Pending</MenuItem>
            <MenuItem value="rejected">Rejected</MenuItem>
          </TextField>
        </Grid>
      </Grid>

      {error && <Alert severity="error" sx={{ mb: 2, borderRadius: 2, bgcolor: 'rgba(248,113,113,0.15)', color: '#F87171' }}>{error}</Alert>}

      <DataTable columns={columns} rows={employers} loading={loading} onRetry={fetchEmployers}
        selectable selected={selected} onSelectionChange={setSelected}
        page={page} rowsPerPage={rowsPerPage} total={total}
        onPageChange={setPage} onRowsPerPageChange={setRowsPerPage}
        onRowClick={(row) => openDetail(row)}
        emptyTitle="No employers found" emptyDescription="Try adjusting your filters" />

      <Dialog open={detailOpen} onClose={() => setDetailOpen(false)} maxWidth="md" fullWidth
        PaperProps={{ sx: { bgcolor: '#1E293B', color: '#F1F5F9', borderRadius: 3 } }}>
        <DialogTitle sx={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>{selectedEmployer?.companyName || selectedEmployer?.company?.companyName || 'Company Details'}</Typography>
        </DialogTitle>
        <Tabs value={detailTab} onChange={(_, v) => setDetailTab(v)} sx={{ px: 2, '& .MuiTab-root': { color: '#64748B', textTransform: 'none' }, '& .Mui-selected': { color: '#818CF8' } }}>
          <Tab label="Company Info" />
          <Tab label={`Jobs (${employerJobs.length})`} />
        </Tabs>
        <DialogContent>
          {detailTab === 0 && selectedEmployer && (
            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, py: 2 }}>
              <Box><Typography variant="caption" sx={{ color: '#64748B' }}>Company Name</Typography><Typography variant="body2" sx={{ color: '#F1F5F9' }}>{selectedEmployer.companyName || selectedEmployer.company?.companyName || 'N/A'}</Typography></Box>
              <Box><Typography variant="caption" sx={{ color: '#64748B' }}>Email</Typography><Typography variant="body2" sx={{ color: '#F1F5F9' }}>{selectedEmployer.companyEmail || selectedEmployer.email || 'N/A'}</Typography></Box>
              <Box><Typography variant="caption" sx={{ color: '#64748B' }}>Phone</Typography><Typography variant="body2" sx={{ color: '#F1F5F9' }}>{selectedEmployer.phone || 'N/A'}</Typography></Box>
              <Box><Typography variant="caption" sx={{ color: '#64748B' }}>Industry</Typography><Typography variant="body2" sx={{ color: '#F1F5F9' }}>{selectedEmployer.industry || 'N/A'}</Typography></Box>
              <Box><Typography variant="caption" sx={{ color: '#64748B' }}>Size</Typography><Typography variant="body2" sx={{ color: '#F1F5F9' }}>{selectedEmployer.companySize || 'N/A'}</Typography></Box>
              <Box><Typography variant="caption" sx={{ color: '#64748B' }}>Website</Typography><Typography variant="body2" sx={{ color: '#60A5FA' }}>{selectedEmployer.website || 'N/A'}</Typography></Box>
              <Box><Typography variant="caption" sx={{ color: '#64748B' }}>Verification</Typography><Box><StatusBadge status={selectedEmployer.verificationStatus || (selectedEmployer.isVerified ? 'verified' : 'pending')} /></Box></Box>
              <Box><Typography variant="caption" sx={{ color: '#64748B' }}>Subscription</Typography><Box><StatusBadge status={selectedEmployer.subscription?.plan || selectedEmployer.plan || 'free'} /></Box></Box>
              <Box><Typography variant="caption" sx={{ color: '#64748B' }}>Owner</Typography><Typography variant="body2" sx={{ color: '#F1F5F9' }}>{selectedEmployer.owner?.name || selectedEmployer.name || 'N/A'}</Typography></Box>
              <Box><Typography variant="caption" sx={{ color: '#64748B' }}>Joined</Typography><Typography variant="body2" sx={{ color: '#F1F5F9' }}>{formatDate(selectedEmployer.createdAt)}</Typography></Box>
            </Box>
          )}
          {detailTab === 1 && (
            employerJobs.length > 0 ? (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ color: '#64748B', borderBottom: '1px solid rgba(255,255,255,0.06)', fontWeight: 600 }}>Title</TableCell>
                      <TableCell sx={{ color: '#64748B', borderBottom: '1px solid rgba(255,255,255,0.06)', fontWeight: 600 }}>Status</TableCell>
                      <TableCell sx={{ color: '#64748B', borderBottom: '1px solid rgba(255,255,255,0.06)', fontWeight: 600 }}>Applications</TableCell>
                      <TableCell sx={{ color: '#64748B', borderBottom: '1px solid rgba(255,255,255,0.06)', fontWeight: 600 }}>Posted</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {employerJobs.map((job) => (
                      <TableRow key={job._id || job.id} hover sx={{ '&:hover': { bgcolor: 'rgba(255,255,255,0.03)' } }}>
                        <TableCell sx={{ color: '#F1F5F9', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>{job.title}</TableCell>
                        <TableCell sx={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}><StatusBadge status={job.status} /></TableCell>
                        <TableCell sx={{ color: '#94A3B8', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>{job.applicationCount || 0}</TableCell>
                        <TableCell sx={{ color: '#94A3B8', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>{formatDate(job.createdAt)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : <Typography sx={{ color: '#64748B', textAlign: 'center', py: 4 }}>No jobs posted</Typography>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 2, borderTop: '1px solid rgba(255,255,255,0.06)' }}>
          {!selectedEmployer?.isVerified && selectedEmployer?.verificationStatus !== 'verified' && (
            <>
              <Button color="success" startIcon={<CheckCircleIcon />} onClick={() => { handleVerify(selectedEmployer._id || selectedEmployer.id); setDetailOpen(false); }}
                sx={{ color: '#4ADE80' }}>Verify</Button>
              <Button color="error" startIcon={<CancelIcon />} onClick={() => setRejectDialogOpen(true)} sx={{ color: '#F87171' }}>Reject</Button>
            </>
          )}
          <Button onClick={() => setDetailOpen(false)} sx={{ color: '#94A3B8' }}>Close</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={rejectDialogOpen} onClose={() => setRejectDialogOpen(false)} maxWidth="sm" fullWidth
        PaperProps={{ sx: { bgcolor: '#1E293B', color: '#F1F5F9', borderRadius: 3 } }}>
        <DialogTitle>Reject Employer</DialogTitle>
        <DialogContent>
          <TextField fullWidth multiline rows={3} label="Rejection Reason" value={rejectReason} onChange={(e) => setRejectReason(e.target.value)}
            sx={{ mt: 2, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRejectDialogOpen(false)} sx={{ color: '#94A3B8' }}>Cancel</Button>
          <Button onClick={handleReject} disabled={!rejectReason} color="error" sx={{ color: '#F87171' }}>Reject</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
