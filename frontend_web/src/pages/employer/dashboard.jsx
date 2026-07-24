import { useState, useEffect, useCallback } from 'react';
import {
  Box, Grid, Typography, Button, Card, CardContent, IconButton, Avatar,
  Chip, Tooltip, Alert, LinearProgress, Skeleton, Stack,
} from '@mui/material';
import DashboardLayout from '@/components/layout/DashboardLayout';
import StatsCard from '@/components/analytics/StatsCard';
import JobChart from '@/components/analytics/JobChart';
import DataTable from '@/components/common/DataTable';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ErrorState from '@/components/common/ErrorState';
import StatusBadge from '@/components/common/StatusBadge';
import { useAnalytics } from '@/hooks/useAnalytics';
import { useAuth } from '@/hooks/useAuth';
import {
  formatCurrency, formatRelativeTime, formatNumber, formatDate,
} from '@/utils/formatters';
import WorkIcon from '@mui/icons-material/Work';
import PeopleIcon from '@mui/icons-material/People';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import ChatIcon from '@mui/icons-material/Chat';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import AddIcon from '@mui/icons-material/Add';
import VisibilityIcon from '@mui/icons-material/Visibility';
import RefreshIcon from '@mui/icons-material/Refresh';
import TodayIcon from '@mui/icons-material/Today';
import HandshakeIcon from '@mui/icons-material/Handshake';
import SpeedIcon from '@mui/icons-material/Speed';
import { useRouter } from 'next/router';

export default function DashboardPage() {
  const router = useRouter();
  const { dashboardStats, loading, error, refresh } = useAnalytics();
  const { user } = useAuth();
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      await refresh();
    } finally {
      setTimeout(() => setRefreshing(false), 600);
    }
  }, [refresh]);

  const employerName = user?.companyName || user?.name || user?.email || 'there';
  const profileComplete = user?.profileComplete ?? true;

  if (loading && !dashboardStats) {
    return (
      <DashboardLayout>
        <Box sx={{ mb: 3 }}>
          <Skeleton variant="text" width={200} height={40} />
          <Skeleton variant="text" width={300} height={20} />
        </Box>
        <Grid container spacing={3} sx={{ mb: 3 }}>
          {[1, 2, 3, 4].map((i) => (
            <Grid item xs={12} sm={6} lg={3} key={i}>
              <StatsCard loading />
            </Grid>
          ))}
        </Grid>
        <Grid container spacing={3}>
          <Grid item xs={12} lg={8}>
            <Skeleton variant="rounded" width="100%" height={350} sx={{ borderRadius: 3 }} />
          </Grid>
          <Grid item xs={12} lg={4}>
            <Skeleton variant="rounded" width="100%" height={350} sx={{ borderRadius: 3 }} />
          </Grid>
        </Grid>
      </DashboardLayout>
    );
  }

  if (error && !dashboardStats) {
    return <DashboardLayout><ErrorState message={error} onRetry={handleRefresh} /></DashboardLayout>;
  }

  const stats = dashboardStats || {};

  const statCards = [
    {
      icon: <WorkIcon sx={{ fontSize: 24 }} />,
      label: 'Active Jobs',
      value: formatNumber(stats.activeJobs || 0),
      trend: stats.jobsTrend,
      trendLabel: 'vs last period',
      variant: 'primary',
      tooltipTitle: 'Total currently active job listings',
      sparklineData: stats.jobsSparkline,
    },
    {
      icon: <PeopleIcon sx={{ fontSize: 24 }} />,
      label: 'Total Applicants',
      value: formatNumber(stats.totalApplicants || 0),
      trend: stats.applicantsTrend,
      trendLabel: 'vs last period',
      variant: 'success',
      tooltipTitle: 'Total applicants across all jobs',
      sparklineData: stats.applicantsSparkline,
    },
    {
      icon: <CalendarMonthIcon sx={{ fontSize: 24 }} />,
      label: 'Interviews Today',
      value: formatNumber(stats.interviewsToday || 0),
      variant: 'warning',
      tooltipTitle: 'Scheduled interviews for today',
    },
    {
      icon: <ChatIcon sx={{ fontSize: 24 }} />,
      label: 'New Messages',
      value: formatNumber(stats.newMessages || 0),
      trend: stats.messagesTrend,
      trendLabel: 'vs last period',
      variant: 'pink',
      tooltipTitle: 'Unread messages in your inbox',
      sparklineData: stats.messagesSparkline,
    },
  ];

  const recentJobs = (stats.recentJobs || []).map((job) => ({
    ...job,
    statusEl: <StatusBadge status={job.status} />,
    salary: formatCurrency(job.minSalary, job.currency),
    created: formatRelativeTime(job.createdAt),
  }));

  const jobColumns = [
    {
      key: 'title', label: 'Job Title', sortable: true,
      render: (row) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box
            sx={{
              width: 8, height: 8, borderRadius: '50%',
              bgcolor: row.status === 'published' ? 'success.main' : row.status === 'closed' ? 'error.main' : 'warning.main',
              flexShrink: 0,
            }}
          />
          <Typography variant="body2" sx={{ fontWeight: 600 }}>{row.title}</Typography>
        </Box>
      ),
    },
    { key: 'statusEl', label: 'Status' },
    { key: 'applications', label: 'Apps', sortable: true },
    { key: 'views', label: 'Views', sortable: true },
    { key: 'salary', label: 'Salary' },
    { key: 'created', label: 'Created', sortable: true },
  ];

  const recentApplications = (stats.recentApplications || []).map((app) => ({
    ...app,
    statusEl: <StatusBadge status={app.status} />,
    name: (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Avatar sx={{ width: 28, height: 28, fontSize: '0.75rem', bgcolor: 'primary.main' }}>
          {(app.name || 'U').charAt(0)}
        </Avatar>
        <Typography variant="body2" sx={{ fontWeight: 500 }}>{app.name || 'Unknown'}</Typography>
      </Box>
    ),
    applied: formatRelativeTime(app.createdAt || app.appliedAt),
  }));

  const appColumns = [
    { key: 'name', label: 'Applicant', sortable: true },
    { key: 'jobTitle', label: 'Job', sortable: true },
    { key: 'statusEl', label: 'Status' },
    { key: 'matchScore', label: 'Match', sortable: true },
    { key: 'applied', label: 'Applied', sortable: true },
  ];

  const jobPerformance = (stats.jobPerformance || []).slice(0, 5).map((jp) => ({
    ...jp,
    statusEl: <StatusBadge status={jp.status} />,
    hireRate: jp.views > 0 ? `${((jp.hires || 0) / jp.views * 100).toFixed(1)}%` : '0%',
  }));

  const perfColumns = [
    { key: 'title', label: 'Job Title', sortable: true, render: (row) => <Typography variant="body2" sx={{ fontWeight: 500 }}>{row.title}</Typography> },
    { key: 'views', label: 'Views', sortable: true },
    { key: 'applications', label: 'Apps', sortable: true },
    { key: 'interviews', label: 'Interviews', sortable: true },
    { key: 'hires', label: 'Hires', sortable: true },
    { key: 'hireRate', label: 'Hire Rate', sortable: true },
  ];

  const activities = stats.recentActivity || [];
  const quickActions = [
    {
      icon: <AddIcon />, label: 'Post a Job', desc: 'Create a new listing',
      color: '#6366F1', onClick: () => router.push('/employer/post-job'),
    },
    {
      icon: <PeopleIcon />, label: 'View Applicants', desc: 'Review candidates',
      color: '#22C55E', onClick: () => router.push('/employer/applicants'),
    },
    {
      icon: <TrendingUpIcon />, label: 'Analytics', desc: 'View reports',
      color: '#F59E0B', onClick: () => router.push('/employer/analytics'),
    },
    {
      icon: <VisibilityIcon />, label: 'Manage Jobs', desc: 'Edit listings',
      color: '#EC4899', onClick: () => router.push('/employer/jobs'),
    },
    {
      icon: <TodayIcon />, label: 'Schedule', desc: 'Manage interviews',
      color: '#14B8A6', onClick: () => router.push('/employer/applicants'),
    },
    {
      icon: <HandshakeIcon />, label: 'Messages', desc: 'Contact candidates',
      color: '#F97316', onClick: () => router.push('/employer/messages'),
    },
  ];

  const metricsCards = [
    { label: 'Total Jobs', value: formatNumber(stats.activeJobs || 0), color: '#6366F1' },
    { label: 'Total Apps', value: formatNumber(stats.totalApplicants || 0), color: '#22C55E' },
    { label: 'Hire Rate', value: stats.hireRate ? `${stats.hireRate}%` : '0%', color: '#14B8A6' },
    { label: 'Avg Time to Hire', value: stats.avgTimeToHire ? `${stats.avgTimeToHire}d` : '-', color: '#F59E0B' },
  ];

  return (
    <DashboardLayout>
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>
            Welcome back, {employerName}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Here&apos;s your hiring overview for today.
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh dashboard data">
            <IconButton onClick={handleRefresh} disabled={loading || refreshing} sx={{ animation: refreshing ? 'spin 1s linear infinite' : 'none' }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {!profileComplete && (
        <Alert
          severity="info"
          sx={{ mb: 3, borderRadius: 2 }}
          action={
            <Button size="small" variant="outlined" onClick={() => router.push('/employer/company-profile')}>
              Complete Profile
            </Button>
          }
        >
          <Typography variant="body2" sx={{ fontWeight: 500 }}>Your profile is incomplete</Typography>
          <Typography variant="caption">Add company details to attract more applicants.</Typography>
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
            data={stats.applicationTrends || []}
            title="Application Trends"
            type="line"
            loading={loading}
            showTypeToggle
            showDownload
            dateFormat="MMM d"
            dataKeys={[
              { key: 'applications', color: '#6366F1', name: 'Applications' },
              { key: 'interviews', color: '#22C55E', name: 'Interviews' },
            ]}
          />
        </Grid>
        <Grid item xs={12} lg={4}>
          <Card sx={{ borderRadius: 3, height: '100%' }}>
            <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>Quick Actions</Typography>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1.5 }}>
                {quickActions.map((action, idx) => (
                  <Box
                    key={idx}
                    onClick={action.onClick}
                    sx={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: 0.75,
                      p: 1.5,
                      borderRadius: 3,
                      border: '1px dashed',
                      borderColor: 'divider',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      '&:hover': { borderColor: action.color, bgcolor: `${action.color}08`, transform: 'translateY(-2px)' },
                    }}
                  >
                    <Box
                      sx={{
                        width: 40, height: 40, borderRadius: 2,
                        bgcolor: `${action.color}15`, display: 'flex',
                        alignItems: 'center', justifyContent: 'center',
                        color: action.color,
                      }}
                    >
                      {action.icon}
                    </Box>
                    <Typography variant="caption" sx={{ fontWeight: 600, textAlign: 'center', lineHeight: 1.2 }}>
                      {action.label}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} lg={7}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>Recent Applications</Typography>
                <Button size="small" variant="text" onClick={() => router.push('/employer/applicants')}>View All</Button>
              </Box>
              <DataTable
                columns={appColumns}
                rows={recentApplications.slice(0, 5)}
                emptyTitle="No applications yet"
                emptyDescription="Applications from candidates will appear here."
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} lg={5}>
          <Card sx={{ borderRadius: 3, height: '100%' }}>
            <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>Recent Activity</Typography>
              {activities.length === 0 ? (
                <Box sx={{ py: 4, textAlign: 'center' }}>
                  <Typography color="text.secondary" variant="body2">No recent activity</Typography>
                  <Typography color="text.disabled" variant="caption">Activity from your jobs and applicants will show here.</Typography>
                </Box>
              ) : (
                <Box sx={{ maxHeight: 360, overflowY: 'auto' }}>
                  {activities.slice(0, 15).map((activity, idx) => (
                    <Box
                      key={idx}
                      sx={{
                        display: 'flex', alignItems: 'flex-start', gap: 1.5, py: 1.25,
                        borderBottom: idx < Math.min(activities.length, 15) - 1 ? '1px solid' : 'none',
                        borderColor: 'divider',
                      }}
                    >
                      <Box
                        sx={{
                          width: 8, height: 8, borderRadius: '50%',
                          bgcolor: activity.type === 'application' ? 'primary.main'
                            : activity.type === 'interview' ? 'warning.main'
                            : activity.type === 'hire' ? 'success.main'
                            : 'text.disabled',
                          mt: 0.6, flexShrink: 0,
                        }}
                      />
                      <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>{activity.message}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {formatRelativeTime(activity.createdAt)}
                        </Typography>
                      </Box>
                    </Box>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={7}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>Job Performance Overview</Typography>
                <Button size="small" variant="text" onClick={() => router.push('/employer/analytics')}>Full Report</Button>
              </Box>
              <DataTable
                columns={perfColumns}
                rows={jobPerformance}
                emptyTitle="No job data"
                emptyDescription="Post jobs to see performance metrics."
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} lg={5}>
          <Card sx={{ borderRadius: 3, height: '100%' }}>
            <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>Key Metrics</Typography>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                {metricsCards.map((mc, idx) => (
                  <Box
                    key={idx}
                    sx={{
                      p: 2, borderRadius: 3,
                      bgcolor: `${mc.color}08`,
                      border: '1px solid',
                      borderColor: `${mc.color}20`,
                    }}
                  >
                    <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
                      {mc.label}
                    </Typography>
                    <Typography variant="h5" sx={{ fontWeight: 700, color: mc.color, mt: 0.5 }}>
                      {mc.value}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </DashboardLayout>
  );
}
