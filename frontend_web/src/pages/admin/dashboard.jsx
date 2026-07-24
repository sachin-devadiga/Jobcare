'use client';
import { useState, useEffect, useCallback } from 'react';
import { Box, Grid, Typography, Card, CardContent, Skeleton, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, Button, Paper, Alert } from '@mui/material';
import PeopleIcon from '@mui/icons-material/People';
import BusinessIcon from '@mui/icons-material/Business';
import WorkIcon from '@mui/icons-material/Work';
import DescriptionIcon from '@mui/icons-material/Description';
import PaymentsIcon from '@mui/icons-material/Payments';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import RefreshIcon from '@mui/icons-material/Refresh';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, LineChart, Line, PieChart, Pie, Cell, Legend } from 'recharts';
import StatsCard from '@/components/admin/StatsCard';
import StatusBadge from '@/components/admin/StatusBadge';
import { formatDate, formatRelativeTime, formatCurrency } from '@/utils/formatters';
import adminService from '@/services/adminService';
import { toast } from 'react-toastify';

const CHART_COLORS = ['#818CF8', '#A78BFA', '#F472B6', '#FB923C', '#FBBF24', '#4ADE80', '#2DD4BF', '#38BDF8'];

export default function AdminDashboardPage() {
  const [stats, setStats] = useState(null);
  const [userGrowth, setUserGrowth] = useState([]);
  const [jobTrends, setJobTrends] = useState([]);
  const [applicationFunnel, setApplicationFunnel] = useState([]);
  const [revenueData, setRevenueData] = useState([]);
  const [recentUsers, setRecentUsers] = useState([]);
  const [systemHealth, setSystemHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsRes, growthRes, jobsRes, funnelRes, revenueRes, usersRes, healthRes] = await Promise.all([
        adminService.getDashboardStats(),
        adminService.getUserGrowth({ days: 30 }),
        adminService.getJobTrends({ days: 30 }),
        adminService.getApplicationFunnel(),
        adminService.getRevenueData({ months: 12 }),
        adminService.getRecentRegistrations({ limit: 10 }),
        adminService.getSystemHealth(),
      ]);
      setStats(statsRes.data);
      setUserGrowth(growthRes.data || []);
      setJobTrends(jobsRes.data || []);
      setApplicationFunnel(funnelRes.data || []);
      setRevenueData(revenueRes.data || []);
      setRecentUsers(usersRes.data || []);
      setSystemHealth(healthRes.data);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard');
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 700, color: '#F1F5F9' }}>Admin Dashboard</Typography>
        <Button startIcon={<RefreshIcon />} onClick={fetchData} disabled={loading}
          sx={{ color: '#94A3B8', '&:hover': { color: '#818CF8' } }}>Refresh</Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2, borderRadius: 2, bgcolor: 'rgba(248,113,113,0.15)', color: '#F87171' }}>{error}</Alert>}

      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <StatsCard icon={<PeopleIcon />} label="Total Users" value={stats?.totalUsers} trend={stats?.userTrend} loading={loading} color="#60A5FA" bgColor="rgba(96,165,250,0.1)" />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <StatsCard icon={<BusinessIcon />} label="Total Employers" value={stats?.totalEmployers} trend={stats?.employerTrend} loading={loading} color="#818CF8" bgColor="rgba(129,140,248,0.1)" />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <StatsCard icon={<WorkIcon />} label="Total Jobs" value={stats?.totalJobs} trend={stats?.jobTrend} loading={loading} color="#4ADE80" bgColor="rgba(74,222,128,0.1)" />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <StatsCard icon={<DescriptionIcon />} label="Applications" value={stats?.totalApplications} trend={stats?.applicationTrend} loading={loading} color="#F472B6" bgColor="rgba(244,114,182,0.1)" />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <StatsCard icon={<PaymentsIcon />} label="Revenue" value={stats?.totalRevenue} trend={stats?.revenueTrend} loading={loading} color="#FBBF24" bgColor="rgba(251,191,36,0.1)" prefix="$" />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <StatsCard icon={<TrendingUpIcon />} label="Active Today" value={stats?.activeUsersToday} trend={stats?.activeTrend} loading={loading} color="#2DD4BF" bgColor="rgba(45,212,191,0.1)" />
        </Grid>
      </Grid>

      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        <Grid item xs={12} md={8}>
          <Card sx={{ bgcolor: '#1E293B', borderRadius: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#F1F5F9', mb: 2 }}>User Growth (Last 30 Days)</Typography>
              {loading ? (
                <Skeleton variant="rounded" height={300} sx={{ bgcolor: 'rgba(255,255,255,0.06)', borderRadius: 2 }} />
              ) : userGrowth.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={userGrowth}>
                    <defs><linearGradient id="userGrowthGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#818CF8" stopOpacity={0.3} /><stop offset="95%" stopColor="#818CF8" stopOpacity={0} /></linearGradient></defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                    <XAxis dataKey="date" tick={{ fill: '#64748B', fontSize: 12 }} tickLine={false} />
                    <YAxis tick={{ fill: '#64748B', fontSize: 12 }} tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={{ backgroundColor: '#1E293B', border: 'none', borderRadius: 8, color: '#F1F5F9' }} />
                    <Area type="monotone" dataKey="users" stroke="#818CF8" strokeWidth={2} fill="url(#userGrowthGrad)" />
                  </AreaChart>
                </ResponsiveContainer>
              ) : <Typography sx={{ color: '#64748B', textAlign: 'center', py: 8 }}>No data available</Typography>}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ bgcolor: '#1E293B', borderRadius: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#F1F5F9', mb: 2 }}>Application Funnel</Typography>
              {loading ? (
                <Skeleton variant="rounded" height={300} sx={{ bgcolor: 'rgba(255,255,255,0.06)', borderRadius: 2 }} />
              ) : applicationFunnel.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie data={applicationFunnel} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={3} dataKey="value">
                      {applicationFunnel.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: '#1E293B', border: 'none', borderRadius: 8, color: '#F1F5F9' }} />
                    <Legend wrapperStyle={{ fontSize: 12, color: '#94A3B8' }} />
                  </PieChart>
                </ResponsiveContainer>
              ) : <Typography sx={{ color: '#64748B', textAlign: 'center', py: 8 }}>No data available</Typography>}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card sx={{ bgcolor: '#1E293B', borderRadius: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#F1F5F9', mb: 2 }}>Job Postings Trend (Last 30 Days)</Typography>
              {loading ? (
                <Skeleton variant="rounded" height={250} sx={{ bgcolor: 'rgba(255,255,255,0.06)', borderRadius: 2 }} />
              ) : jobTrends.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={jobTrends}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                    <XAxis dataKey="date" tick={{ fill: '#64748B', fontSize: 12 }} tickLine={false} />
                    <YAxis tick={{ fill: '#64748B', fontSize: 12 }} tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={{ backgroundColor: '#1E293B', border: 'none', borderRadius: 8, color: '#F1F5F9' }} />
                    <Bar dataKey="jobs" fill="#818CF8" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : <Typography sx={{ color: '#64748B', textAlign: 'center', py: 6 }}>No data available</Typography>}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={{ bgcolor: '#1E293B', borderRadius: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#F1F5F9', mb: 2 }}>Revenue (Monthly)</Typography>
              {loading ? (
                <Skeleton variant="rounded" height={250} sx={{ bgcolor: 'rgba(255,255,255,0.06)', borderRadius: 2 }} />
              ) : revenueData.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={revenueData}>
                    <defs><linearGradient id="revenueGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#FBBF24" stopOpacity={0.3} /><stop offset="95%" stopColor="#FBBF24" stopOpacity={0} /></linearGradient></defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                    <XAxis dataKey="month" tick={{ fill: '#64748B', fontSize: 12 }} tickLine={false} />
                    <YAxis tick={{ fill: '#64748B', fontSize: 12 }} tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={{ backgroundColor: '#1E293B', border: 'none', borderRadius: 8, color: '#F1F5F9' }} />
                    <Area type="monotone" dataKey="revenue" stroke="#FBBF24" strokeWidth={2} fill="url(#revenueGrad)" />
                  </AreaChart>
                </ResponsiveContainer>
              ) : <Typography sx={{ color: '#64748B', textAlign: 'center', py: 6 }}>No data available</Typography>}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={2.5}>
        <Grid item xs={12} md={7}>
          <Card sx={{ bgcolor: '#1E293B', borderRadius: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#F1F5F9', mb: 2 }}>Recent Registrations</Typography>
              {loading ? (
                <Skeleton variant="rounded" height={300} sx={{ bgcolor: 'rgba(255,255,255,0.06)', borderRadius: 2 }} />
              ) : recentUsers.length > 0 ? (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell sx={{ color: '#64748B', borderBottom: '1px solid rgba(255,255,255,0.06)', fontWeight: 600 }}>Name</TableCell>
                        <TableCell sx={{ color: '#64748B', borderBottom: '1px solid rgba(255,255,255,0.06)', fontWeight: 600 }}>Email</TableCell>
                        <TableCell sx={{ color: '#64748B', borderBottom: '1px solid rgba(255,255,255,0.06)', fontWeight: 600 }}>Role</TableCell>
                        <TableCell sx={{ color: '#64748B', borderBottom: '1px solid rgba(255,255,255,0.06)', fontWeight: 600 }}>Joined</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {recentUsers.map((user) => (
                        <TableRow key={user._id || user.id} hover sx={{ '&:hover': { bgcolor: 'rgba(255,255,255,0.03)' } }}>
                          <TableCell sx={{ color: '#F1F5F9', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>{user.name || 'N/A'}</TableCell>
                          <TableCell sx={{ color: '#F1F5F9', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>{user.email}</TableCell>
                          <TableCell sx={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}><StatusBadge status={user.role} /></TableCell>
                          <TableCell sx={{ color: '#64748B', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>{formatRelativeTime(user.createdAt)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : <Typography sx={{ color: '#64748B', textAlign: 'center', py: 6 }}>No recent registrations</Typography>}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={5}>
          <Card sx={{ bgcolor: '#1E293B', borderRadius: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#F1F5F9', mb: 2 }}>System Health</Typography>
              {loading ? (
                <Box>{[1, 2, 3, 4].map((i) => <Skeleton key={i} variant="rounded" height={48} sx={{ mb: 1, bgcolor: 'rgba(255,255,255,0.06)' }} />)}</Box>
              ) : systemHealth ? (
                <Box>
                  {[
                    { key: 'api', label: 'API Server', icon: '🟢' },
                    { key: 'database', label: 'Database', icon: '🟢' },
                    { key: 'redis', label: 'Redis Cache', icon: '🟢' },
                    { key: 'celery', label: 'Celery Workers', icon: '🟢' },
                  ].map((svc) => {
                    const status = systemHealth[svc.key];
                    const isHealthy = status === 'healthy' || status === 'connected' || status === 'running' || status === true;
                    return (
                      <Box key={svc.key} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', p: 2, borderRadius: 2, bgcolor: 'rgba(255,255,255,0.03)', mb: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                          <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: isHealthy ? '#4ADE80' : '#F87171' }} />
                          <Typography variant="body2" sx={{ color: '#F1F5F9', fontWeight: 500 }}>{svc.label}</Typography>
                        </Box>
                        <Chip label={isHealthy ? 'Healthy' : 'Unhealthy'} size="small"
                          sx={{ bgcolor: isHealthy ? 'rgba(74,222,128,0.15)' : 'rgba(248,113,113,0.15)', color: isHealthy ? '#4ADE80' : '#F87171', fontWeight: 600 }} />
                      </Box>
                    );
                  })}
                </Box>
              ) : <Typography sx={{ color: '#64748B', textAlign: 'center', py: 6 }}>Health data unavailable</Typography>}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={2.5} sx={{ mt: 1 }}>
        <Grid item xs={12}>
          <Card sx={{ bgcolor: '#1E293B', borderRadius: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#F1F5F9', mb: 2 }}>Quick Actions</Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                {[
                  { label: 'Add New Admin', icon: <PersonAddIcon />, href: '/admin/settings' },
                  { label: 'Review Flagged Jobs', icon: <WorkIcon />, href: '/admin/jobs?status=flagged' },
                  { label: 'Verify Employers', icon: <BusinessIcon />, href: '/admin/employers?status=pending' },
                  { label: 'View Reports', icon: <DescriptionIcon />, href: '/admin/analytics' },
                  { label: 'Manage Banners', icon: <TrendingUpIcon />, href: '/admin/cms' },
                ].map((action) => (
                  <Button key={action.label} variant="outlined" startIcon={action.icon} href={action.href}
                    sx={{ borderColor: 'rgba(255,255,255,0.12)', color: '#94A3B8', '&:hover': { borderColor: '#818CF8', color: '#818CF8', bgcolor: 'rgba(129,140,248,0.08)' } }}>
                    {action.label}
                  </Button>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
