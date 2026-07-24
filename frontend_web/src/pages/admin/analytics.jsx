'use client';
import { useState, useEffect, useCallback } from 'react';
import { Box, Typography, TextField, Button, MenuItem, Grid, Card, CardContent, Skeleton, FormControl, InputLabel, Select } from '@mui/material';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, LineChart, Line, PieChart, Pie, Cell, Legend } from 'recharts';
import adminService from '@/services/adminService';
import { toast } from 'react-toastify';
import fileSaver from 'file-saver';

const CHART_COLORS = ['#818CF8', '#A78BFA', '#F472B6', '#FB923C', '#FBBF24', '#4ADE80', '#2DD4BF', '#38BDF8', '#6366F1', '#EC4899'];

export default function AdminAnalyticsPage() {
  const [dateRange, setDateRange] = useState('30d');
  const [customFrom, setCustomFrom] = useState('');
  const [customTo, setCustomTo] = useState('');
  const [loading, setLoading] = useState(true);
  const [userAcquisition, setUserAcquisition] = useState([]);
  const [jobTrends, setJobTrends] = useState([]);
  const [appFunnel, setAppFunnel] = useState([]);
  const [categoryPop, setCategoryPop] = useState([]);
  const [locationData, setLocationData] = useState([]);
  const [salaryData, setSalaryData] = useState([]);
  const [employerActivity, setEmployerActivity] = useState([]);

  const getParams = () => {
    if (dateRange === 'custom' && customFrom && customTo) {
      return { dateFrom: customFrom, dateTo: customTo };
    }
    return { days: parseInt(dateRange) || 30 };
  };

  const fetchAnalytics = useCallback(async () => {
    setLoading(true);
    try {
      const params = getParams();
      const [acq, jobs, funnel, cat, loc, sal, emp] = await Promise.all([
        adminService.getUserAcquisition(params),
        adminService.getJobAnalytics(params),
        adminService.getApplicationAnalytics(params),
        adminService.getCategoryAnalytics(),
        adminService.getLocationAnalytics(),
        adminService.getSalaryAnalytics(),
        adminService.getEmployerAnalytics(params),
      ]);
      setUserAcquisition(acq.data || []);
      setJobTrends(jobs.data || []);
      setAppFunnel(funnel.data || []);
      setCategoryPop(cat.data || []);
      setLocationData(loc.data || []);
      setSalaryData(sal.data || []);
      setEmployerActivity(emp.data || []);
    } catch (err) {
      toast.error('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  }, [dateRange, customFrom, customTo]);

  useEffect(() => { fetchAnalytics(); }, [fetchAnalytics]);

  const handleExport = async (format = 'csv') => {
    try {
      const res = await adminService.exportReport({ ...getParams(), format });
      const blob = new Blob([res.data], { type: format === 'csv' ? 'text/csv' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      fileSaver.saveAs(blob, `analytics_report_${new Date().toISOString().split('T')[0]}.${format}`);
      toast.success('Report exported');
    } catch (err) {
      toast.error('Failed to export report');
    }
  };

  const ChartCard = ({ title, children, height = 300 }) => (
    <Card sx={{ bgcolor: '#1E293B', borderRadius: 3, height: '100%' }}>
      <CardContent sx={{ p: 3 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#F1F5F9', mb: 2 }}>{title}</Typography>
        {loading ? <Skeleton variant="rounded" height={height - 60} sx={{ bgcolor: 'rgba(255,255,255,0.06)', borderRadius: 2 }} /> : children}
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 2 }}>
        <Typography variant="h5" sx={{ fontWeight: 700, color: '#F1F5F9' }}>Analytics</Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
          <TextField select size="small" value={dateRange} onChange={(e) => setDateRange(e.target.value)}
            sx={{ minWidth: 150, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } } }}>
            <MenuItem value="7d">Last 7 days</MenuItem>
            <MenuItem value="30d">Last 30 days</MenuItem>
            <MenuItem value="90d">Last 90 days</MenuItem>
            <MenuItem value="1y">Last year</MenuItem>
            <MenuItem value="custom">Custom range</MenuItem>
          </TextField>
          {dateRange === 'custom' && (
            <>
              <TextField type="date" size="small" value={customFrom} onChange={(e) => setCustomFrom(e.target.value)}
                sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } } }} />
              <TextField type="date" size="small" value={customTo} onChange={(e) => setCustomTo(e.target.value)}
                sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } } }} />
            </>
          )}
          <Button variant="contained" size="small" onClick={fetchAnalytics} sx={{ bgcolor: '#818CF8', '&:hover': { bgcolor: '#6366F1' } }}>Apply</Button>
          <Button startIcon={<FileDownloadIcon />} size="small" onClick={() => handleExport('csv')}
            sx={{ color: '#94A3B8', '&:hover': { color: '#818CF8' } }}>Export CSV</Button>
        </Box>
      </Box>

      <Grid container spacing={2.5}>
        <Grid item xs={12} md={6}>
          <ChartCard title="User Acquisition">
            {userAcquisition.length > 0 ? (
              <ResponsiveContainer width="100%" height={240}>
                <AreaChart data={userAcquisition}>
                  <defs><linearGradient id="uaGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#818CF8" stopOpacity={0.3} /><stop offset="95%" stopColor="#818CF8" stopOpacity={0} /></linearGradient></defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis dataKey="date" tick={{ fill: '#64748B', fontSize: 12 }} tickLine={false} />
                  <YAxis tick={{ fill: '#64748B', fontSize: 12 }} tickLine={false} axisLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: '#1E293B', border: 'none', borderRadius: 8, color: '#F1F5F9' }} />
                  <Area type="monotone" dataKey="users" stroke="#818CF8" strokeWidth={2} fill="url(#uaGrad)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : <Typography sx={{ color: '#64748B', textAlign: 'center', py: 6 }}>No data</Typography>}
          </ChartCard>
        </Grid>

        <Grid item xs={12} md={6}>
          <ChartCard title="Job Posting Trends">
            {jobTrends.length > 0 ? (
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={jobTrends}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis dataKey="date" tick={{ fill: '#64748B', fontSize: 12 }} tickLine={false} />
                  <YAxis tick={{ fill: '#64748B', fontSize: 12 }} tickLine={false} axisLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: '#1E293B', border: 'none', borderRadius: 8, color: '#F1F5F9' }} />
                  <Bar dataKey="jobs" fill="#818CF8" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : <Typography sx={{ color: '#64748B', textAlign: 'center', py: 6 }}>No data</Typography>}
          </ChartCard>
        </Grid>

        <Grid item xs={12} md={6}>
          <ChartCard title="Application Conversion Funnel">
            {appFunnel.length > 0 ? (
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={appFunnel} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis type="number" tick={{ fill: '#64748B', fontSize: 12 }} tickLine={false} />
                  <YAxis dataKey="name" type="category" tick={{ fill: '#64748B', fontSize: 12 }} tickLine={false} width={120} />
                  <Tooltip contentStyle={{ backgroundColor: '#1E293B', border: 'none', borderRadius: 8, color: '#F1F5F9' }} />
                  <Bar dataKey="value" fill="#818CF8" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : <Typography sx={{ color: '#64748B', textAlign: 'center', py: 6 }}>No data</Typography>}
          </ChartCard>
        </Grid>

        <Grid item xs={12} md={6}>
          <ChartCard title="Category Popularity">
            {categoryPop.length > 0 ? (
              <ResponsiveContainer width="100%" height={240}>
                <PieChart>
                  <Pie data={categoryPop} cx="50%" cy="50%" outerRadius={80} paddingAngle={2} dataKey="value" nameKey="name">
                    {categoryPop.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: '#1E293B', border: 'none', borderRadius: 8, color: '#F1F5F9' }} />
                  <Legend wrapperStyle={{ fontSize: 12, color: '#94A3B8' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : <Typography sx={{ color: '#64748B', textAlign: 'center', py: 6 }}>No data</Typography>}
          </ChartCard>
        </Grid>

        <Grid item xs={12} md={6}>
          <ChartCard title="Location-Based Job Distribution">
            {locationData.length > 0 ? (
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={locationData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis type="number" tick={{ fill: '#64748B', fontSize: 12 }} tickLine={false} />
                  <YAxis dataKey="location" type="category" tick={{ fill: '#64748B', fontSize: 12 }} tickLine={false} width={120} />
                  <Tooltip contentStyle={{ backgroundColor: '#1E293B', border: 'none', borderRadius: 8, color: '#F1F5F9' }} />
                  <Bar dataKey="count" fill="#38BDF8" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : <Typography sx={{ color: '#64748B', textAlign: 'center', py: 6 }}>No data</Typography>}
          </ChartCard>
        </Grid>

        <Grid item xs={12} md={6}>
          <ChartCard title="Salary Trends">
            {salaryData.length > 0 ? (
              <ResponsiveContainer width="100%" height={240}>
                <LineChart data={salaryData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis dataKey="category" tick={{ fill: '#64748B', fontSize: 12 }} tickLine={false} />
                  <YAxis tick={{ fill: '#64748B', fontSize: 12 }} tickLine={false} axisLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: '#1E293B', border: 'none', borderRadius: 8, color: '#F1F5F9' }} />
                  <Line type="monotone" dataKey="average" stroke="#4ADE80" strokeWidth={2} dot={{ r: 4, fill: '#4ADE80' }} />
                  <Line type="monotone" dataKey="median" stroke="#FBBF24" strokeWidth={2} dot={{ r: 4, fill: '#FBBF24' }} />
                </LineChart>
              </ResponsiveContainer>
            ) : <Typography sx={{ color: '#64748B', textAlign: 'center', py: 6 }}>No data</Typography>}
          </ChartCard>
        </Grid>

        <Grid item xs={12}>
          <ChartCard title="Employer Activity Metrics" height={250}>
            {employerActivity.length > 0 ? (
              <ResponsiveContainer width="100%" height={190}>
                <AreaChart data={employerActivity}>
                  <defs><linearGradient id="empActGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#A78BFA" stopOpacity={0.3} /><stop offset="95%" stopColor="#A78BFA" stopOpacity={0} /></linearGradient></defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis dataKey="date" tick={{ fill: '#64748B', fontSize: 12 }} tickLine={false} />
                  <YAxis tick={{ fill: '#64748B', fontSize: 12 }} tickLine={false} axisLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: '#1E293B', border: 'none', borderRadius: 8, color: '#F1F5F9' }} />
                  <Area type="monotone" dataKey="activeEmployers" stroke="#A78BFA" strokeWidth={2} fill="url(#empActGrad)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : <Typography sx={{ color: '#64748B', textAlign: 'center', py: 4 }}>No data</Typography>}
          </ChartCard>
        </Grid>
      </Grid>
    </Box>
  );
}
