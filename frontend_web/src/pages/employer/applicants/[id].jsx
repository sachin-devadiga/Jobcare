import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/router';
import { Box, Button } from '@mui/material';
import DashboardLayout from '@/components/layout/DashboardLayout';
import ApplicantDetail from '@/components/applications/ApplicantDetail';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ErrorState from '@/components/common/ErrorState';
import * as applicationService from '@/services/applicationService';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

export default function ApplicantDetailPage() {
  const router = useRouter();
  const { id } = router.query;
  const [applicant, setApplicant] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchApplicant = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const response = await applicationService.getApplicationById(id);
      setApplicant(response.data || response);
    } catch (err) {
      setError(err.message || 'Failed to load applicant');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchApplicant();
  }, [fetchApplicant]);

  const handleStatusUpdate = async (applicantId, status, notes) => {
    try {
      const response = await applicationService.updateApplicationStatus(applicantId, status, notes);
      setApplicant(response.data || response);
    } catch {
      /* handled by service */
    }
  };

  const handleScheduleInterview = async (applicantId, data) => {
    try {
      const response = await applicationService.scheduleInterview(applicantId, data);
      setApplicant(response.data || response);
    } catch {
      /* handled by service */
    }
  };

  const handleAddNote = async (applicantId, note) => {
    try {
      const response = await applicationService.addNote(applicantId, note);
      setApplicant(response.data || response);
    } catch {
      /* handled by service */
    }
  };

  if (loading) return <DashboardLayout><LoadingSpinner message="Loading applicant details..." /></DashboardLayout>;
  if (error) return <DashboardLayout><ErrorState message={error} onRetry={fetchApplicant} /></DashboardLayout>;
  if (!applicant) return null;

  return (
    <DashboardLayout>
      <Box sx={{ mb: 2 }}>
        <Button startIcon={<ArrowBackIcon />} onClick={() => router.push('/employer/applicants')} variant="text">
          Back to Applicants
        </Button>
      </Box>
      <ApplicantDetail
        applicant={applicant}
        onStatusUpdate={handleStatusUpdate}
        onScheduleInterview={handleScheduleInterview}
        onAddNote={handleAddNote}
      />
    </DashboardLayout>
  );
}
