import { useState, useEffect, useCallback, useRef } from 'react';
import {
  Box, Grid, Typography, MenuItem, TextField, Button, Card, CardContent,
  ToggleButtonGroup, ToggleButton, IconButton, Tooltip, Skeleton, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  TableSortLabel, Stack, Divider, Alert,
} from '@mui/material';
import DashboardLayout from '@/components/layout/DashboardLayout';
import StatsCard from '@/components/analytics/StatsCard';
import JobChart from '@/components/analytics/JobChart';
import ApplicationChart from '@/components/analytics/ApplicationChart';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ErrorState from '@/components/common/ErrorState';
import { useAnalytics } from '@/hooks/useAnalytics';
import { DATE_RANGE_PRESETS, CHART_COLORS } from '@/utils/constants';
import { formatNumber, formatPercentage, formatCurrency } from '@/utils/formatters';
import WorkIcon from '@mui/icons-material/Work';
import PeopleIcon from '@mui/icons-material/People';
import VisibilityIcon from '@mui/icons-material/Visibility';
import ThumbUpIcon from '@mui/icons-material/ThumbUp';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import RefreshIcon from '@mui/icons-material/Refresh';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import ScheduleIcon from '@mui/icons-material/Schedule';
import HandshakeIcon from '@mui/icons-material/Handshake';
import { format, subDays, startOfDay, endOfDay } from 'date-fns';
import { toast } from 'react-toastify';

function ChartSkeleton({ height = 300 }) {
  return (
    <Box sx={{ height, display: 'flex', flexDirection: 'column', gap: 1, p: 2 }}>
      <Skeleton variant="text" width="40%" height={24} />
      <Skeleton variant="rounded" width="100%" height={height - 80} />
      <Skeleton variant="text" width="60%" height={16} />
    </Box>
  );
}

export default function AnalyticsPage() {
  const {
    dashboardStats, jobAnalytics, applicationAnalytics, applicationTrends,
    loading, error, refresh,
  } = useAnalytics();
  const [period, setPeriod] = useState('30d');
  const [customStart, setCustomStart] = useState('');
  const [customEnd, setCustomEnd] = useState('');
  const [comparisonMode, setComparisonMode] = useState(false);
  const [jobSortKey, setJobSortKey] = useState('applications');
  const [jobSortDir, setJobSortDir] = useState('desc');
  const [refreshing, setRefreshing] = useState(false);
  const [exportingPdf, setExportingPdf] = useState(false);
  const reportRef = useRef(null);

  const handlePeriodChange = (val) => {
    setPeriod(val);
    setComparisonMode(false);
  };

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      await refresh();
      toast.success('Analytics refreshed');
    } catch {
      toast.error('Failed to refresh');
    } finally {
      setTimeout(() => setRefreshing(false), 600);
    }
  }, [refresh]);

  const handleExportPDF = async () => {
    setExportingPdf(true);
    try {
      const { default: jsPDF } = await import('jspdf');
      const { default: autoTable } = await import('jspdf-autotable');
      const doc = new jsPDF({ orientation: 'landscape' });
      const pageWidth = doc.internal.pageSize.getWidth();

      doc.setFontSize(18);
      doc.text('Analytics Report', 14, 20);
      doc.setFontSize(10);
      doc.text(`Generated: ${format(new Date(), 'MMM dd, yyyy h:mm a')}`, 14, 28);
      doc.text(`Period: ${DATE_RANGE_PRESETS.find((p) => p.value === period)?.label || period}`, 14, 34);

      const ds = dashboardStats || {};
      const metrics = [
        ['Total Views', formatNumber(ds.totalViews || 0)],
        ['Total Applications', formatNumber(ds.totalApplicants || 0)],
        ['Interviews', formatNumber(ds.totalInterviews || 0)],
        ['Active Jobs', formatNumber(ds.activeJobs || 0)],
      ];
      autoTable(doc, {
        startY: 42,
        head: [['Metric', 'Value']],
        body: metrics,
        theme: 'grid',
        headStyles: { fillColor: [99, 102, 241] },
      });

      const jobs = (jobAnalytics?.jobs || jobAnalytics || []).slice(0, 10);
      if (jobs.length > 0) {
        const jobRows = jobs.map((j) => [
          j.title || j.name || '-',
          j.views || 0,
          j.applications || 0,
          j.interviews || 0,
          j.hires || 0,
        ]);
        autoTable(doc, {
          startY: doc.lastAutoTable.finalY + 12,
          head: [['Job Title', 'Views', 'Apps', 'Interviews', 'Hires']],
          body: jobRows,
          theme: 'grid',
          headStyles: { fillColor: [99, 102, 241] },
        });
      }

      const funnelData = applicationAnalytics?.funnel || [];
      if (funnelData.length > 0) {
        const funnelRows = funnelData.map((f) => [f.name, f.value || 0]);
        autoTable(doc, {
          startY: doc.lastAutoTable.finalY + 12,
          head: [['Stage', 'Count']],
          body: funnelRows,
          theme: 'grid',
          headStyles: { fillColor: [99, 102, 241] },
        });
      }

      doc.save(`analytics_report_${format(new Date(), 'yyyy-MM-dd')}.pdf`);
      toast.success('Analytics report downloaded');
    } catch (err) {
      toast.error('Failed to export PDF');
    } finally {
      setExportingPdf(false);
    }
  };

  const handleJobSort = (key) => {
    if (jobSortKey === key) {
      setJobSortDir((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setJobSortKey(key);
      setJobSortDir('desc');
    }
  };

  if (loading && !dashboardStats) {
    return (
      <DashboardLayout>
        <Box sx={{ mb: 3 }}>
          <Skeleton variant="text" width={200} height={40} />
          <Skeleton variant="text" width={300} height={20} />
        </Box>
        <Grid container spacing={3} sx={{ mb: 3 }}>
          {[1, 2, 3, 4].map((i) => (
            <Grid item xs={12} sm={6} lg={3} key={i}><StatsCard loading /></Grid>
          ))}
        </Grid>
        <Grid container spacing={3}>
          <Grid item xs={12} lg={8}><ChartSkeleton height={320} /></Grid>
          <Grid item xs={12} lg={4}><ChartSkeleton height={320} /></Grid>
        </Grid>
      </DashboardLayout>
    );
  }

  if (error && !dashboardStats) {
    return <DashboardLayout><ErrorState message={error} onRetry={refresh} /></DashboardLayout>;
  }

  const ds = dashboardStats || {};
  const jobs = (jobAnalytics?.jobs || jobAnalytics || []).slice(0, 20);
  const funnelData = applicationAnalytics?.funnel || [];
  const locations = applicationAnalytics?.locations || ds.topLocations || [];
  const categories = applicationAnalytics?.categories || ds.topCategories || [];

  const statCards = [
    {
      icon: <WorkIcon sx={{ fontSize: 24 }} />,
      label: 'Active Jobs',
      value: formatNumber(ds.activeJobs || 0),
      trend: ds.jobsTrend,
      trendLabel: 'vs last period',
      variant: 'primary',
      tooltipTitle: 'Total currently active job listings',
      sparklineData: ds.jobsSparkline,
    },
    {
      icon: <PeopleIcon sx={{ fontSize: 24 }} />,
      label: 'Total Applications',
      value: formatNumber(ds.totalApplicants || 0),
      trend: ds.applicantsTrend,
      trendLabel: 'vs last period',
      variant: 'success',
      tooltipTitle: 'Total applications across all jobs',
      sparklineData: ds.applicantsSparkline,
    },
    {
      icon: <HandshakeIcon sx={{ fontSize: 24 }} />,
      label: 'Hire Rate',
      value: formatPercentage(ds.hireRate, 1),
      trend: ds.hireRateTrend,
      trendLabel: 'vs last period',
      variant: 'info',
      tooltipTitle: 'Percentage of applications that resulted in hires',
    },
    {
      icon: <ScheduleIcon sx={{ fontSize: 24 }} />,
      label: 'Avg Time to Hire',
      value: ds.avgTimeToHire ? `${ds.avgTimeToHire}d` : '-',
      trend: ds.timeToHireTrend ? -ds.timeToHireTrend : null,
      trendLabel: 'vs last period',
      variant: 'warning',
      tooltipTitle: 'Average days from application to hire',
    },
  ];

  const sortedJobs = [...jobs].sort((a, b) => {
    const aVal = a[jobSortKey] || 0;
    const bVal = b[jobSortKey] || 0;
    return jobSortDir === 'asc' ? aVal - bVal : bVal - aVal;
  });

  const previousPeriodStats = comparisonMode ? {
    views: ds.previousViews || 0,
    applications: ds.previousApplications || 0,
    interviews: ds.previousInterviews || 0,
    hires: ds.previousHires || 0,
  } : null;

  return (
    <DashboardLayout>
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>Analytics</Typography>
          <Typography variant="body2" color="text.secondary">Track your hiring performance</Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <TextField
            select
            size="small"
            value={period}
            onChange={(e) => handlePeriodChange(e.target.value)}
            sx={{ minWidth: 140 }}
          >
            {DATE_RANGE_PRESETS.map((opt) => (
              <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
            ))}
          </TextField>
          {period === 'custom' && (
            <>
              <TextField size="small" type="date" label="From" value={customStart}
                onChange={(e) => setCustomStart(e.target.value)} InputLabelProps={{ shrink: true }} />
              <TextField size="small" type="date" label="To" value={customEnd}
                onChange={(e) => setCustomEnd(e.target.value)} InputLabelProps={{ shrink: true }} />
            </>
          )}
          <Tooltip title="Compare with previous period">
            <Button
              size="small"
              variant={comparisonMode ? 'contained' : 'outlined'}
              onClick={() => setComparisonMode(!comparisonMode)}
            >
              Compare
            </Button>
          </Tooltip>
          <Tooltip title="Refresh">
            <IconButton onClick={handleRefresh} disabled={loading || refreshing}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Export as PDF">
            <IconButton onClick={handleExportPDF} disabled={exportingPdf}>
              <PictureAsPdfIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {comparisonMode && (
        <Alert severity="info" sx={{ mb: 3, borderRadius: 2 }}>
          <Typography variant="body2" sx={{ fontWeight: 500 }}>
            Comparing with previous period
          </Typography>
        </Alert>
      )}

      <Grid container spacing={3} sx={{ mb: 3 }}>
        {statCards.map((stat, idx) => (
          <Grid item xs={12} sm={6} lg={3} key={idx}>
            <StatsCard {...stat} />
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} lg={8}>
          <JobChart
            data={applicationTrends || []}
            title="Application Trends"
            type="line"
            loading={loading}
            showTypeToggle
            showDownload
            dateFormat="MMM d"
            dataKeys={[
              { key: 'applications', color: '#6366F1', name: 'Applications' },
              { key: 'views', color: '#F59E0B', name: 'Views' },
              { key: 'interviews', color: '#22C55E', name: 'Interviews' },
            ]}
          />
        </Grid>
        <Grid item xs={12} lg={4}>
          <ApplicationChart
            data={funnelData}
            title="Application Funnel"
            height={320}
            loading={loading}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} lg={7}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>Jobs Performance</Typography>
              {loading ? (
                <ChartSkeleton height={250} />
              ) : sortedJobs.length === 0 ? (
                <Box sx={{ py: 4, textAlign: 'center' }}>
                  <Typography color="text.secondary" variant="body2">No job data available</Typography>
                </Box>
              ) : (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell sx={{ fontWeight: 600, fontSize: '0.75rem' }}>Job Title</TableCell>
                        {['views', 'applications', 'interviews', 'hires'].map((key) => (
                          <TableCell key={key} align="right" sx={{ fontWeight: 600, fontSize: '0.75rem' }}>
                            <TableSortLabel
                              active={jobSortKey === key}
                              direction={jobSortKey === key ? jobSortDir : 'asc'}
                              onClick={() => handleJobSort(key)}
                            >
                              {key.charAt(0).toUpperCase() + key.slice(1)}
                            </TableSortLabel>
                          </TableCell>
                        ))}
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {sortedJobs.map((job, idx) => (
                        <TableRow key={job._id || job.id || idx} hover>
                          <TableCell sx={{ fontSize: '0.8rem', fontWeight: 500 }}>
                            {job.title || job.name || '-'}
                          </TableCell>
                          <TableCell align="right" sx={{ fontSize: '0.8rem' }}>{job.views || 0}</TableCell>
                          <TableCell align="right" sx={{ fontSize: '0.8rem' }}>{job.applications || 0}</TableCell>
                          <TableCell align="right" sx={{ fontSize: '0.8rem' }}>{job.interviews || 0}</TableCell>
                          <TableCell align="right" sx={{ fontSize: '0.8rem', fontWeight: 600 }}>{job.hires || 0}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} lg={5}>
          <Card sx={{ borderRadius: 3, height: '100%' }}>
            <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>Key Metrics</Typography>
              {loading ? (
                <ChartSkeleton height={200} />
              ) : (
                <Grid container spacing={2}>
                  {[
                    { label: 'Total Views', value: formatNumber(ds.totalViews || 0), color: CHART_COLORS[0] },
                    { label: 'Total Applications', value: formatNumber(ds.totalApplicants || 0), color: CHART_COLORS[6] },
                    { label: 'Hire Rate', value: formatPercentage(ds.hireRate, 1), color: CHART_COLORS[7] },
                    { label: 'Avg Time to Hire', value: ds.avgTimeToHire ? `${ds.avgTimeToHire}d` : '-', color: CHART_COLORS[4] },
                    { label: 'Interviews Scheduled', value: formatNumber(ds.totalInterviews || 0), color: CHART_COLORS[2] },
                    { label: 'Offers Made', value: formatNumber(ds.totalOffers || 0), color: CHART_COLORS[8] },
                  ].map((m, idx) => (
                    <Grid item xs={6} key={idx}>
                      <Box
                        sx={{
                          p: 1.5, borderRadius: 2,
                          bgcolor: `${m.color}10`,
                          border: '1px solid',
                          borderColor: `${m.color}25`,
                        }}
                      >
                        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
                          {m.label}
                        </Typography>
                        <Typography variant="h6" sx={{ fontWeight: 700, color: m.color, mt: 0.25 }}>
                          {m.value}
                        </Typography>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>Top Locations</Typography>
              {loading ? (
                <ChartSkeleton height={250} />
              ) : locations.length === 0 ? (
                <Box sx={{ py: 4, textAlign: 'center' }}>
                  <Typography color="text.secondary" variant="body2">No location data</Typography>
                </Box>
              ) : (
                <JobChart
                  data={locations}
                  type="bar"
                  height={250}
                  showDownload={false}
                  showTypeToggle={false}
                  dataKeys={[{ key: 'count', color: '#6366F1', name: 'Applications' }]}
                />
              )}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>Top Categories</Typography>
              {loading ? (
                <ChartSkeleton height={250} />
              ) : categories.length === 0 ? (
                <Box sx={{ py: 4, textAlign: 'center' }}>
                  <Typography color="text.secondary" variant="body2">No category data</Typography>
                </Box>
              ) : (
                <JobChart
                  data={categories}
                  type="bar"
                  height={250}
                  showDownload={false}
                  showTypeToggle={false}
                  dataKeys={[{ key: 'count', color: '#8B5CF6', name: 'Jobs' }]}
                />
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </DashboardLayout>
  );
}
