import { useState } from 'react';
import { Box, Typography, Button, Grid, Pagination } from '@mui/material';
import DashboardLayout from '@/components/layout/DashboardLayout';
import JobCard from '@/components/jobs/JobCard';
import JobFilters from '@/components/jobs/JobFilters';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ErrorState from '@/components/common/ErrorState';
import EmptyState from '@/components/common/EmptyState';
import ConfirmDialog from '@/components/common/ConfirmDialog';
import { useJobs } from '@/hooks/useJobs';
import AddIcon from '@mui/icons-material/Add';
import { useRouter } from 'next/router';

export default function JobsPage() {
  const router = useRouter();
  const { jobs, loading, error, pagination, deleteJob, publishJob, closeJob, archiveJob, duplicateJob, setPage, setFilters, refresh } = useJobs();
  const [search, setSearch] = useState('');
  const [filters, setLocalFilters] = useState({});
  const [confirmDelete, setConfirmDelete] = useState(null);

  const handleFilterChange = (newFilters) => {
    setLocalFilters(newFilters);
    setFilters(newFilters);
  };

  const handleSearch = (term) => {
    setSearch(term);
    setFilters({ ...filters, search: term });
  };

  const handleDelete = async (id) => {
    setConfirmDelete(id);
  };

  const confirmDeleteJob = async () => {
    if (confirmDelete) {
      await deleteJob(confirmDelete);
      setConfirmDelete(null);
    }
  };

  if (error && !jobs.length) {
    return (
      <DashboardLayout>
        <ErrorState message={error} onRetry={refresh} />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>Manage Jobs</Typography>
          <Typography variant="body2" color="text.secondary">{pagination.total} jobs found</Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => router.push('/employer/post-job')} sx={{ borderRadius: 3 }}>
          Post New Job
        </Button>
      </Box>

      <JobFilters
        filters={{ ...filters, search }}
        onFilterChange={handleFilterChange}
        onSearch={handleSearch}
      />

      {loading ? (
        <LoadingSpinner message="Loading jobs..." fullPage={false} />
      ) : jobs.length === 0 ? (
        <EmptyState
          title="No jobs found"
          description={search || Object.keys(filters).length > 0 ? 'Try adjusting your filters.' : 'Post your first job to start hiring.'}
          action
          actionLabel="Post a Job"
          onAction={() => router.push('/employer/post-job')}
        />
      ) : (
        <>
          <Grid container spacing={3}>
            {jobs.map((job) => (
              <Grid item xs={12} md={6} lg={4} key={job._id || job.id}>
                <JobCard
                  job={job}
                  onEdit={(id) => router.push(`/employer/jobs/${id}`)}
                  onDelete={handleDelete}
                  onPublish={publishJob}
                  onClose={closeJob}
                  onArchive={archiveJob}
                  onDuplicate={duplicateJob}
                />
              </Grid>
            ))}
          </Grid>

          {pagination.totalPages > 1 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <Pagination
                count={pagination.totalPages}
                page={pagination.page}
                onChange={(_, p) => setPage(p)}
                color="primary"
                shape="rounded"
              />
            </Box>
          )}
        </>
      )}

      <ConfirmDialog
        open={!!confirmDelete}
        onClose={() => setConfirmDelete(null)}
        onConfirm={confirmDeleteJob}
        title="Delete Job"
        message="Are you sure you want to delete this job? This action cannot be undone."
        severity="error"
        confirmText="Delete"
      />
    </DashboardLayout>
  );
}
