import { useState } from 'react';
import {
  Box, Typography, Paper, Grid, TextField, Button, Divider, Switch,
  FormControlLabel, Select, MenuItem, FormControl, InputLabel,
} from '@mui/material';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { useAuth } from '@/hooks/useAuth';
import { useForm } from 'react-hook-form';
import { toast } from 'react-toastify';

export default function SettingsPage() {
  const { user, updateUser } = useAuth();
  const [saving, setSaving] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      name: user?.name || '',
      email: user?.email || '',
      phone: user?.phone || '',
      timezone: user?.timezone || 'UTC',
      language: user?.language || 'en',
    },
  });

  const [notifications, setNotifications] = useState({
    emailNotifications: true,
    newApplications: true,
    interviewReminders: true,
    marketingEmails: false,
    weeklyDigest: true,
    candidateUpdates: true,
  });

  const handleSaveProfile = async (data) => {
    setSaving(true);
    try {
      await new Promise((r) => setTimeout(r, 1000));
      updateUser({ ...user, ...data });
      toast.success('Settings saved successfully!');
    } catch {
      toast.error('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  return (
    <DashboardLayout>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>Settings</Typography>
        <Typography variant="body2" color="text.secondary">Manage your account and preferences</Typography>
      </Box>

      <Box component="form" onSubmit={handleSubmit(handleSaveProfile)}>
        <Paper sx={{ p: 3, mb: 3, borderRadius: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>Profile Settings</Typography>
          <Grid container spacing={2.5}>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth label="Name" {...register('name')} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth label="Email" {...register('email')} disabled />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth label="Phone" {...register('phone')} />
            </Grid>
            <Grid item xs={12} sm={3}>
              <FormControl fullWidth>
                <InputLabel>Timezone</InputLabel>
                <Select label="Timezone" defaultValue={user?.timezone || 'UTC'} {...register('timezone')}>
                  <MenuItem value="UTC">UTC</MenuItem>
                  <MenuItem value="EST">EST</MenuItem>
                  <MenuItem value="PST">PST</MenuItem>
                  <MenuItem value="IST">IST (India)</MenuItem>
                  <MenuItem value="GMT">GMT</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={3}>
              <FormControl fullWidth>
                <InputLabel>Language</InputLabel>
                <Select label="Language" defaultValue={user?.language || 'en'} {...register('language')}>
                  <MenuItem value="en">English</MenuItem>
                  <MenuItem value="es">Spanish</MenuItem>
                  <MenuItem value="fr">French</MenuItem>
                  <MenuItem value="de">German</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
            <Button variant="contained" type="submit" disabled={saving}>
              {saving ? 'Saving...' : 'Save Changes'}
            </Button>
          </Box>
        </Paper>
      </Box>

      <Paper sx={{ p: 3, mb: 3, borderRadius: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>Notification Preferences</Typography>
        <Grid container spacing={2}>
          {Object.entries(notifications).map(([key, val]) => (
            <Grid item xs={12} sm={6} key={key}>
              <FormControlLabel
                control={
                  <Switch
                    checked={val}
                    onChange={(e) => setNotifications((prev) => ({ ...prev, [key]: e.target.checked }))}
                  />
                }
                label={key.replace(/([A-Z])/g, ' $1').replace(/^./, (s) => s.toUpperCase())}
                sx={{ '& .MuiTypography-root': { fontSize: '0.875rem' } }}
              />
            </Grid>
          ))}
        </Grid>
      </Paper>

      <Paper sx={{ p: 3, borderRadius: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 3, color: 'error.main' }}>Danger Zone</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Once you delete your account, there is no going back. Please be certain.
        </Typography>
        <Button variant="outlined" color="error">Delete Account</Button>
      </Paper>
    </DashboardLayout>
  );
}
