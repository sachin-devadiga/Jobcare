'use client';
import { useState, useEffect, useCallback } from 'react';
import { Box, Typography, TextField, Button, MenuItem, InputAdornment, Grid, Alert, Card, CardContent, Dialog, DialogTitle, DialogContent, DialogActions, Tabs, Tab } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import PaymentsIcon from '@mui/icons-material/Payments';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import DataTable from '@/components/admin/DataTable';
import StatusBadge from '@/components/admin/StatusBadge';
import StatsCard from '@/components/admin/StatsCard';
import { formatDate, formatDateTime, formatCurrency } from '@/utils/formatters';
import adminService from '@/services/adminService';
import { toast } from 'react-toastify';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function AdminPaymentsPage() {
  const [tab, setTab] = useState(0);
  const [transactions, setTransactions] = useState([]);
  const [subscriptions, setSubscriptions] = useState([]);
  const [payouts, setPayouts] = useState([]);
  const [revenueSummary, setRevenueSummary] = useState(null);
  const [revenueChart, setRevenueChart] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState('all');
  const [refundDialogOpen, setRefundDialogOpen] = useState(false);
  const [selectedPayment, setSelectedPayment] = useState(null);
  const [refundReason, setRefundReason] = useState('');

  const fetchPayments = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      if (tab === 2) {
        const { data } = await adminService.getPayouts({ page: page + 1, limit: rowsPerPage });
        setPayouts(data.payouts || data.data || []);
        setTotal(data.total || 0);
      } else {
        const params = { page: page + 1, limit: rowsPerPage, status: statusFilter !== 'all' ? statusFilter : undefined };
        const { data } = tab === 0 ? await adminService.getPayments(params) : await adminService.getSubscriptions(params);
        if (tab === 0) { setTransactions(data.payments || data.data || []); setTotal(data.total || 0); }
        else { setSubscriptions(data.subscriptions || data.data || []); setTotal(data.total || 0); }
      }
    } catch (err) {
      setError(err.message || 'Failed to load data');
    } finally { setLoading(false); }
  }, [tab, page, rowsPerPage, statusFilter]);

  useEffect(() => { fetchPayments(); }, [fetchPayments]);

  useEffect(() => {
    adminService.getRevenueSummary().then(({ data }) => setRevenueSummary(data)).catch(() => {});
    adminService.getRevenueChart({ months: 12 }).then(({ data }) => setRevenueChart(data || [])).catch(() => {});
  }, []);

  const handleRefund = async () => {
    if (!selectedPayment || !refundReason) return;
    try {
      await adminService.processRefund(selectedPayment._id || selectedPayment.id, { reason: refundReason });
      toast.success('Refund processed');
      setRefundDialogOpen(false);
      setRefundReason('');
      fetchPayments();
    } catch (err) { toast.error(err.message || 'Refund failed'); }
  };

  const paymentColumns = [
    { key: 'id', label: 'ID', render: (row) => <Typography variant="body2" sx={{ color: '#64748B', fontFamily: 'monospace' }}>#{row.transactionId || row._id?.slice(-8) || row.id?.slice(-8)}</Typography> },
    { key: 'user', label: 'User', render: (row) => <Typography variant="body2" sx={{ color: '#F1F5F9' }}>{row.user?.name || row.name || 'N/A'}</Typography> },
    { key: 'amount', label: 'Amount', render: (row) => <Typography variant="body2" sx={{ color: '#4ADE80', fontWeight: 600 }}>{formatCurrency(row.amount, row.currency)}</Typography> },
    { key: 'method', label: 'Method', render: (row) => <Typography variant="body2" sx={{ color: '#94A3B8' }}>{row.paymentMethod || row.method || '-'}</Typography> },
    { key: 'status', label: 'Status', render: (row) => <StatusBadge status={row.status} /> },
    { key: 'createdAt', label: 'Date', sortable: true, render: (row) => <Typography variant="body2" sx={{ color: '#94A3B8' }}>{formatDate(row.createdAt)}</Typography> },
    { key: 'actions', label: 'Actions', render: (row) => (
      row.status === 'completed' || row.status === 'paid' ? (
        <Button size="small" onClick={(e) => { e.stopPropagation(); setSelectedPayment(row); setRefundDialogOpen(true); }}
          sx={{ color: '#FBBF24', bgcolor: 'rgba(251,191,36,0.15)', '&:hover': { bgcolor: 'rgba(251,191,36,0.25)' } }}>Refund</Button>
      ) : '-'
    )},
  ];

  const subColumns = [
    { key: 'company', label: 'Company', render: (row) => <Typography variant="body2" sx={{ fontWeight: 600, color: '#F1F5F9' }}>{row.company?.companyName || row.companyName || row.employer?.companyName || 'N/A'}</Typography> },
    { key: 'plan', label: 'Plan', render: (row) => <StatusBadge status={row.plan} /> },
    { key: 'status', label: 'Status', render: (row) => <StatusBadge status={row.status} /> },
    { key: 'amount', label: 'Amount', render: (row) => <Typography variant="body2" sx={{ color: '#4ADE80' }}>{formatCurrency(row.amount, row.currency)}</Typography> },
    { key: 'endDate', label: 'Renewal', render: (row) => <Typography variant="body2" sx={{ color: '#94A3B8' }}>{formatDate(row.endDate)}</Typography> },
    { key: 'createdAt', label: 'Started', render: (row) => <Typography variant="body2" sx={{ color: '#94A3B8' }}>{formatDate(row.createdAt)}</Typography> },
  ];

  return (
    <Box>
      <Typography variant="h5" sx={{ fontWeight: 700, color: '#F1F5F9', mb: 3 }}>Payments & Revenue</Typography>

      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        <Grid item xs={6} md={3}>
          <StatsCard icon={<PaymentsIcon />} label="Total Revenue" value={revenueSummary?.totalRevenue} loading={!revenueSummary} color="#FBBF24" bgColor="rgba(251,191,36,0.1)" prefix="$" />
        </Grid>
        <Grid item xs={6} md={3}>
          <StatsCard icon={<TrendingUpIcon />} label="MRR" value={revenueSummary?.mrr} loading={!revenueSummary} color="#4ADE80" bgColor="rgba(74,222,128,0.1)" prefix="$" />
        </Grid>
        <Grid item xs={6} md={3}>
          <StatsCard icon={<TrendingUpIcon />} label="ARR" value={revenueSummary?.arr} loading={!revenueSummary} color="#818CF8" bgColor="rgba(129,140,248,0.1)" prefix="$" />
        </Grid>
        <Grid item xs={6} md={3}>
          <StatsCard icon={<PaymentsIcon />} label="Refunds" value={revenueSummary?.totalRefunds || 0} loading={!revenueSummary} color="#F87171" bgColor="rgba(248,113,113,0.1)" />
        </Grid>
      </Grid>

      {revenueChart.length > 0 && (
        <Card sx={{ bgcolor: '#1E293B', borderRadius: 3, mb: 3 }}>
          <CardContent sx={{ p: 3 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#F1F5F9', mb: 2 }}>Revenue Trend</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={revenueChart}>
                <defs><linearGradient id="revChartGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#FBBF24" stopOpacity={0.3} /><stop offset="95%" stopColor="#FBBF24" stopOpacity={0} /></linearGradient></defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="month" tick={{ fill: '#64748B', fontSize: 12 }} tickLine={false} />
                <YAxis tick={{ fill: '#64748B', fontSize: 12 }} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#1E293B', border: 'none', borderRadius: 8, color: '#F1F5F9' }} />
                <Area type="monotone" dataKey="revenue" stroke="#FBBF24" strokeWidth={2} fill="url(#revChartGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      <Tabs value={tab} onChange={(_, v) => { setTab(v); setPage(0); }}
        sx={{ mb: 2, '& .MuiTab-root': { color: '#64748B', textTransform: 'none' }, '& .Mui-selected': { color: '#818CF8' } }}>
        <Tab label="Transactions" />
        <Tab label="Subscriptions" />
        <Tab label="Payouts" />
      </Tabs>

      {tab === 0 && (
        <Box sx={{ mb: 2 }}>
          <TextField select fullWidth label="Status" value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(0); }}
            sx={{ maxWidth: 200, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }}>
            <MenuItem value="all">All Status</MenuItem>
            <MenuItem value="completed">Completed</MenuItem>
            <MenuItem value="pending">Pending</MenuItem>
            <MenuItem value="failed">Failed</MenuItem>
            <MenuItem value="refunded">Refunded</MenuItem>
          </TextField>
        </Box>
      )}

      {error && <Alert severity="error" sx={{ mb: 2, borderRadius: 2, bgcolor: 'rgba(248,113,113,0.15)', color: '#F87171' }}>{error}</Alert>}

      <DataTable columns={tab === 0 ? paymentColumns : tab === 1 ? subColumns : paymentColumns}
        rows={tab === 0 ? transactions : tab === 1 ? subscriptions : payouts}
        loading={loading} onRetry={fetchPayments}
        page={page} rowsPerPage={rowsPerPage} total={total}
        onPageChange={setPage} onRowsPerPageChange={setRowsPerPage}
        emptyTitle={`No ${tab === 0 ? 'transactions' : tab === 1 ? 'subscriptions' : 'payouts'} found`} />

      <Dialog open={refundDialogOpen} onClose={() => setRefundDialogOpen(false)} maxWidth="sm" fullWidth
        PaperProps={{ sx: { bgcolor: '#1E293B', color: '#F1F5F9', borderRadius: 3 } }}>
        <DialogTitle>Process Refund</DialogTitle>
        <DialogContent>
          {selectedPayment && (
            <Typography variant="body2" sx={{ color: '#94A3B8', mb: 2 }}>
              Refunding {formatCurrency(selectedPayment.amount, selectedPayment.currency)} for transaction #{selectedPayment.transactionId || selectedPayment._id?.slice(-8)}
            </Typography>
          )}
          <TextField fullWidth multiline rows={3} label="Refund Reason" value={refundReason} onChange={(e) => setRefundReason(e.target.value)}
            sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRefundDialogOpen(false)} sx={{ color: '#94A3B8' }}>Cancel</Button>
          <Button onClick={handleRefund} disabled={!refundReason} color="warning" sx={{ color: '#FBBF24' }}>Process Refund</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
