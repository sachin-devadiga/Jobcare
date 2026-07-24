import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/router';
import { Box, Typography, Button, Grid, Chip, Tabs, Tab, Divider } from '@mui/material';
import DashboardLayout from '@/components/layout/DashboardLayout';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ErrorState from '@/components/common/ErrorState';
import StatusBadge from '@/components/common/StatusBadge';
import JobStats from '@/components/jobs/JobStats';
import ApplicantCard from '@/components/applications/ApplicantCard';
import * as jobService from '@/services/jobService';
import * as applicationService from '@/services/applicationService';
import { formatSalaryRange, formatRelativeTime } from '@/utils/formatters';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import EditIcon from '@mui/icons-material/Edit';

export default function JobDetailPage() {
  const router = useRouter();
  const { id } = router.query;
  const [job, setJob] = useState(null);
  const [stats, setStats] = useState(null);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tab, setTab] = useState(0);

  const fetchData = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const [jobRes, statsRes, appsRes] = await Promise.all([
        jobService.getJobById(id),
        jobService.getJobStats(id),
        jobService.getJobApplications(id),
      ]);
      setJob(jobRes.data || jobRes);
      setStats(statsRes.data || statsRes);
      setApplications(appsRes.data || appsRes.applications || []);
    } catch (err) {
      setError(err.message || 'Failed to load job details');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (loading) return <DashboardLayout><LoadingSpinner message="Loading job details..." /></DashboardLayout>;
  if (error) return <DashboardLayout><ErrorState message={error} onRetry={fetchData} /></DashboardLayout>;
  if (!job) return null;

  return (
    <DashboardLayout>
      <Box sx={{ mb: 3 }}>
        <Button startIcon={<ArrowBackIcon />} onClick={() => router.push('/employer/jobs')} variant="text" sx={{ mb: 1 }}>
          Back to Jobs
        </Button>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 0.5 }}>
              <Typography variant="h4" sx={{ fontWeight: 700 }}>{job.title}</Typography>
              <StatusBadge status={job.status} />
            </Box>
            <Typography variant="body2" color="text.secondary">
              {job.location} &middot; {job.type?.replace(/_/g, ' ')} &middot; {job.experienceLevel?.replace(/_/g, ' ')}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button variant="outlined" startIcon={<EditIcon />} sx={{ borderRadius: 3 }}>
              Edit Job
            </Button>
          </Box>
        </Box>
      </Box>

      <JobStats stats={stats} />

      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 3 }}>
        {job.minSalary && (
          <Chip label={formatSalaryRange(job.minSalary, job.maxSalary, job.currency)} variant="outlined" />
        )}
        <Chip label={`${job.applications || 0} applicants`} variant="outlined" />
        <Chip label={`Created ${formatRelativeTime(job.createdAt)}`} variant="outlined" />
      </Box>

      <Box sx={{ mb: 3 }}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
          <Tab label={`Applicants (${applications.length})`} />
          <Tab label="Description" />
        </Tabs>
        <Divider />
      </Box>

      {tab === 0 && (
        applications.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 6 }}>
            <Typography color="text.secondary">No applicants yet</Typography>
          </Box>
        ) : (
          <Grid container spacing={3}>
            {applications.map((app) => (
              <Grid item xs={12} sm={6} lg={4} key={app._id || app.id}>
                <ApplicantCard applicant={app} />
              </Grid>
            ))}
          </Grid>
        )
      )}

      {tab === 1 && (
        <Box sx={{ maxWidth: 800 }}>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>Description</Typography>
          <Typography variant="body2" sx={{ mb: 3, whiteSpace: 'pre-wrap' }}>{job.description}</Typography>

          {job.responsibilities && (
            <>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>Responsibilities</Typography>
              <Typography variant="body2" sx={{ mb: 3, whiteSpace: 'pre-wrap' }}>{job.responsibilities}</Typography>
            </>
          )}

          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>Requirements</Typography>
          <Typography variant="body2" sx={{ mb: 3, whiteSpace: 'pre-wrap' }}>{job.requirements}</Typography>

          {job.benefits && (
            <>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>Benefits</Typography>
              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>{job.benefits}</Typography>
            </>
          )}

          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>Skills Required</Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {(job.skills || []).map((skill) => (
                <Chip key={skill} label={skill} variant="outlined" />
              ))}
            </Box>
          </Box>
        </Box>
      )}
    </DashboardLayout>
  );
}
