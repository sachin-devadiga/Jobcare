import { useState, useEffect, useCallback } from 'react';
import { Box, Typography } from '@mui/material';
import DashboardLayout from '@/components/layout/DashboardLayout';
import CompanyProfileForm from '@/components/employer/CompanyProfileForm';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ErrorState from '@/components/common/ErrorState';
import * as companyService from '@/services/companyService';

export default function CompanyProfilePage() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const fetchProfile = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await companyService.getCompanyProfile();
      setProfile(response.data || response);
    } catch (err) {
      setError(err.message || 'Failed to load company profile');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  const handleSubmit = async (data) => {
    setSaving(true);
    try {
      const response = await companyService.updateCompanyProfile(data);
      setProfile(response.data || response);
    } catch {
      /* handled by service */
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <DashboardLayout><LoadingSpinner message="Loading company profile..." /></DashboardLayout>;
  if (error) return <DashboardLayout><ErrorState message={error} onRetry={fetchProfile} /></DashboardLayout>;

  return (
    <DashboardLayout>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>Company Profile</Typography>
        <Typography variant="body2" color="text.secondary">
          Manage your company information and branding
        </Typography>
      </Box>
      <CompanyProfileForm
        profile={profile}
        onSubmit={handleSubmit}
        loading={saving}
      />
    </DashboardLayout>
  );
}
