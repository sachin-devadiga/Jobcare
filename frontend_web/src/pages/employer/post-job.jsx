import { useState } from 'react';
import { Box, Typography } from '@mui/material';
import DashboardLayout from '@/components/layout/DashboardLayout';
import JobForm from '@/components/jobs/JobForm';
import { useJobs } from '@/hooks/useJobs';

export default function PostJobPage() {
  const { createJob, loading } = useJobs();

  const handleSubmit = async (data) => {
    await createJob(data);
  };

  const handleSaveDraft = async (data) => {
    await createJob({ ...data, status: 'draft' });
  };

  return (
    <DashboardLayout>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>
          Post a New Job
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Create a new job posting and attract top talent.
        </Typography>
      </Box>
      <JobForm
        onSubmit={handleSubmit}
        onSaveDraft={handleSaveDraft}
        loading={loading}
      />
    </DashboardLayout>
  );
}
