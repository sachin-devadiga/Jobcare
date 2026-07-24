'use client';
import { useState, useEffect, useCallback } from 'react';
import { Box, Typography, TextField, Button, Chip, MenuItem, InputAdornment, Grid, Alert } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import BlockIcon from '@mui/icons-material/Block';
import VerifiedIcon from '@mui/icons-material/Verified';
import DeleteIcon from '@mui/icons-material/Delete';
import DataTable from '@/components/admin/DataTable';
import StatusBadge from '@/components/admin/StatusBadge';
import UserDetailDrawer from '@/components/admin/UserDetailDrawer';
import ConfirmDialog from '@/components/admin/ConfirmDialog';
import { formatDate } from '@/utils/formatters';
import adminService from '@/services/adminService';
import { toast } from 'react-toastify';
import fileSaver from 'file-saver';

export default function AdminUsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [verifiedFilter, setVerifiedFilter] = useState('all');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [total, setTotal] = useState(0);
  const [selected, setSelected] = useState([]);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [confirmDialog, setConfirmDialog] = useState({ open: false, type: '' });

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = { page: page + 1, limit: rowsPerPage, search, role: roleFilter !== 'all' ? roleFilter : undefined, status: statusFilter !== 'all' ? statusFilter : undefined, verified: verifiedFilter !== 'all' ? verifiedFilter === 'verified' : undefined };
      const { data } = await adminService.getUsers(params);
      setUsers(data.users || data.data || data || []);
      setTotal(data.total || data.count || data.pagination?.total || 0);
    } catch (err) {
      setError(err.message || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage, search, roleFilter, statusFilter, verifiedFilter]);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const handleBulkAction = async (action) => {
    try {
      await adminService.bulkUpdateUsers({ ids: selected, action });
      toast.success(`${selected.length} users updated`);
      setSelected([]);
      setConfirmDialog({ open: false, type: '' });
      fetchUsers();
    } catch (err) {
      toast.error(err.message || `Failed to ${action} users`);
    }
  };

  const handleExport = async () => {
    try {
      const res = await adminService.exportUsers({ search, role: roleFilter !== 'all' ? roleFilter : undefined, status: statusFilter !== 'all' ? statusFilter : undefined });
      const blob = new Blob([res.data], { type: 'text/csv' });
      fileSaver.saveAs(blob, `users_export_${new Date().toISOString().split('T')[0]}.csv`);
      toast.success('Users exported successfully');
    } catch (err) {
      toast.error('Failed to export users');
    }
  };

  const columns = [
    { key: 'name', label: 'Name', sortable: true, render: (row) => <Box><Typography variant="body2" sx={{ fontWeight: 600, color: '#F1F5F9' }}>{row.name || 'N/A'}</Typography><Typography variant="caption" sx={{ color: '#64748B' }}>{row.email}</Typography></Box> },
    { key: 'email', label: 'Email', render: (row) => <Typography variant="body2" sx={{ color: '#F1F5F9' }}>{row.email}</Typography> },
    { key: 'phone', label: 'Phone', render: (row) => <Typography variant="body2" sx={{ color: '#94A3B8' }}>{row.phone || '-'}</Typography> },
    { key: 'role', label: 'Role', render: (row) => <StatusBadge status={row.role} /> },
    { key: 'status', label: 'Status', render: (row) => <StatusBadge status={row.status} /> },
    { key: 'isVerified', label: 'Verified', render: (row) => row.isVerified ? <Chip label="Yes" size="small" sx={{ bgcolor: 'rgba(74,222,128,0.15)', color: '#4ADE80', fontWeight: 600 }} /> : <Chip label="No" size="small" sx={{ bgcolor: 'rgba(248,113,113,0.15)', color: '#F87171', fontWeight: 600 }} /> },
    { key: 'createdAt', label: 'Joined', sortable: true, render: (row) => <Typography variant="body2" sx={{ color: '#94A3B8' }}>{formatDate(row.createdAt)}</Typography> },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 700, color: '#F1F5F9' }}>User Management</Typography>
        <Button startIcon={<FileDownloadIcon />} onClick={handleExport}
          sx={{ color: '#94A3B8', '&:hover': { color: '#818CF8' } }}>Export CSV</Button>
      </Box>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <TextField fullWidth placeholder="Search by name, email, phone..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(0); }}
            sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' }, '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.2)' } } }}
            InputProps={{ startAdornment: <InputAdornment position="start"><SearchIcon sx={{ color: '#64748B' }} /></InputAdornment> }} />
        </Grid>
        <Grid item xs={6} md={2}>
          <TextField select fullWidth label="Role" value={roleFilter} onChange={(e) => { setRoleFilter(e.target.value); setPage(0); }}
            sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }}>
            <MenuItem value="all">All Roles</MenuItem>
            <MenuItem value="employee">Employee</MenuItem>
            <MenuItem value="employer">Employer</MenuItem>
            <MenuItem value="admin">Admin</MenuItem>
          </TextField>
        </Grid>
        <Grid item xs={6} md={2}>
          <TextField select fullWidth label="Status" value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(0); }}
            sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }}>
            <MenuItem value="all">All Status</MenuItem>
            <MenuItem value="active">Active</MenuItem>
            <MenuItem value="inactive">Inactive</MenuItem>
            <MenuItem value="banned">Banned</MenuItem>
          </TextField>
        </Grid>
        <Grid item xs={6} md={2}>
          <TextField select fullWidth label="Verification" value={verifiedFilter} onChange={(e) => { setVerifiedFilter(e.target.value); setPage(0); }}
            sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }}>
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="verified">Verified</MenuItem>
            <MenuItem value="unverified">Unverified</MenuItem>
          </TextField>
        </Grid>
      </Grid>

      {error && <Alert severity="error" sx={{ mb: 2, borderRadius: 2, bgcolor: 'rgba(248,113,113,0.15)', color: '#F87171' }}>{error}</Alert>}

      <DataTable
        columns={columns}
        rows={users}
        loading={loading}
        error={error}
        onRetry={fetchUsers}
        selectable
        selected={selected}
        onSelectionChange={setSelected}
        page={page}
        rowsPerPage={rowsPerPage}
        total={total}
        onPageChange={setPage}
        onRowsPerPageChange={setRowsPerPage}
        defaultSortBy="createdAt"
        defaultSortOrder="desc"
        onExport={handleExport}
        emptyTitle="No users found"
        emptyDescription="Try adjusting your search or filter criteria"
        bulkActions={
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Chip icon={<CheckCircleIcon />} label="Activate" size="small" onClick={() => setConfirmDialog({ open: true, type: 'activate' })} sx={{ color: '#4ADE80', bgcolor: 'rgba(74,222,128,0.15)', cursor: 'pointer', '&:hover': { bgcolor: 'rgba(74,222,128,0.25)' } }} />
            <Chip icon={<BlockIcon />} label="Deactivate" size="small" onClick={() => setConfirmDialog({ open: true, type: 'deactivate' })} sx={{ color: '#FBBF24', bgcolor: 'rgba(251,191,36,0.15)', cursor: 'pointer', '&:hover': { bgcolor: 'rgba(251,191,36,0.25)' } }} />
            <Chip icon={<VerifiedIcon />} label="Verify" size="small" onClick={() => setConfirmDialog({ open: true, type: 'verify' })} sx={{ color: '#60A5FA', bgcolor: 'rgba(96,165,250,0.15)', cursor: 'pointer', '&:hover': { bgcolor: 'rgba(96,165,250,0.25)' } }} />
            <Chip icon={<DeleteIcon />} label="Delete" size="small" onClick={() => setConfirmDialog({ open: true, type: 'delete' })} sx={{ color: '#F87171', bgcolor: 'rgba(248,113,113,0.15)', cursor: 'pointer', '&:hover': { bgcolor: 'rgba(248,113,113,0.25)' } }} />
          </Box>
        }
        onRowClick={(row) => { setSelectedUserId(row._id || row.id); setDrawerOpen(true); }}
      />

      <UserDetailDrawer open={drawerOpen} onClose={() => { setDrawerOpen(false); setSelectedUserId(null); }} userId={selectedUserId} onAction={fetchUsers} />

      <ConfirmDialog open={confirmDialog.open} onClose={() => setConfirmDialog({ open: false, type: '' })}
        onConfirm={() => handleBulkAction(confirmDialog.type)}
        title={`${confirmDialog.type.charAt(0).toUpperCase() + confirmDialog.type.slice(1)} Users`}
        message={`Are you sure you want to ${confirmDialog.type} ${selected.length} selected users?`}
        severity={confirmDialog.type === 'delete' ? 'error' : 'info'} />
    </Box>
  );
}
