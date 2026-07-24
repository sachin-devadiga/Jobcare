'use client';
import { useState, useEffect, useCallback } from 'react';
import {
  Box, Typography, TextField, Button, Switch, Card, CardContent, Grid, Tabs, Tab,
  Dialog, DialogTitle, DialogContent, DialogActions, Chip, Alert, IconButton, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Select, MenuItem, FormControlLabel,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import adminService from '@/services/adminService';
import { toast } from 'react-toastify';
import { formatDateTime } from '@/utils/formatters';

export default function AdminSettingsPage() {
  const [tab, setTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState({});
  const [featureToggles, setFeatureToggles] = useState([]);
  const [emailTemplates, setEmailTemplates] = useState([]);
  const [apiKeys, setApiKeys] = useState([]);
  const [securitySettings, setSecuritySettings] = useState({});
  const [systemLogs, setSystemLogs] = useState([]);
  const [admins, setAdmins] = useState([]);
  const [maintenanceMode, setMaintenanceMode] = useState(false);
  const [apiKeyDialogOpen, setApiKeyDialogOpen] = useState(false);
  const [newApiKeyName, setNewApiKeyName] = useState('');
  const [adminDialogOpen, setAdminDialogOpen] = useState(false);
  const [newAdmin, setNewAdmin] = useState({ name: '', email: '', password: '' });
  const [emailEditOpen, setEmailEditOpen] = useState(false);
  const [editingEmail, setEditingEmail] = useState(null);
  const [emailForm, setEmailForm] = useState({ subject: '', body: '' });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const results = await Promise.allSettled([
        adminService.getSettings(),
        adminService.getFeatureToggles(),
        adminService.getEmailTemplates(),
        adminService.getApiKeys(),
        adminService.getSecuritySettings(),
        adminService.getSystemLogs({ limit: 100 }),
        adminService.getAdmins(),
      ]);
      if (results[0].status === 'fulfilled') setSettings(results[0].value.data || {});
      if (results[1].status === 'fulfilled') setFeatureToggles(results[1].value.data?.toggles || results[1].value.data || []);
      if (results[2].status === 'fulfilled') setEmailTemplates(results[2].value.data?.templates || results[2].value.data || []);
      if (results[3].status === 'fulfilled') setApiKeys(results[3].value.data?.keys || results[3].value.data || []);
      if (results[4].status === 'fulfilled') setSecuritySettings(results[4].value.data || {});
      if (results[5].status === 'fulfilled') setSystemLogs(results[5].value.data?.logs || results[5].value.data || []);
      if (results[6].status === 'fulfilled') setAdmins(results[6].value.data?.admins || results[6].value.data || []);
    } catch {} finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleSaveSettings = async () => {
    try {
      await adminService.updateSettings(settings);
      toast.success('Settings saved');
    } catch (err) { toast.error('Failed to save settings'); }
  };

  const handleToggleFeature = async (key, enabled) => {
    try {
      await adminService.updateFeatureToggle(key, { enabled });
      toast.success('Feature toggle updated');
      fetchData();
    } catch (err) { toast.error('Failed to update'); }
  };

  const handleCreateApiKey = async () => {
    if (!newApiKeyName) return;
    try {
      await adminService.createApiKey({ name: newApiKeyName });
      toast.success('API key created');
      setApiKeyDialogOpen(false);
      setNewApiKeyName('');
      fetchData();
    } catch (err) { toast.error('Failed to create API key'); }
  };

  const handleRevokeApiKey = async (id) => {
    try {
      await adminService.revokeApiKey(id);
      toast.success('API key revoked');
      fetchData();
    } catch (err) { toast.error('Failed to revoke'); }
  };

  const handleSaveSecurity = async () => {
    try {
      await adminService.updateSecuritySettings(securitySettings);
      toast.success('Security settings saved');
    } catch (err) { toast.error('Failed to save'); }
  };

  const handleToggleMaintenance = async () => {
    try {
      await adminService.toggleMaintenanceMode({ enabled: !maintenanceMode });
      setMaintenanceMode(!maintenanceMode);
      toast.success(`Maintenance mode ${!maintenanceMode ? 'enabled' : 'disabled'}`);
    } catch (err) { toast.error('Failed to toggle'); }
  };

  const handleCreateAdmin = async () => {
    if (!newAdmin.name || !newAdmin.email || !newAdmin.password) return;
    try {
      await adminService.createAdmin(newAdmin);
      toast.success('Admin created');
      setAdminDialogOpen(false);
      setNewAdmin({ name: '', email: '', password: '' });
      fetchData();
    } catch (err) { toast.error('Failed to create admin'); }
  };

  const handleRemoveAdmin = async (id) => {
    try {
      await adminService.removeAdmin(id);
      toast.success('Admin removed');
      fetchData();
    } catch (err) { toast.error('Failed to remove'); }
  };

  if (loading) return <Typography sx={{ color: '#64748B', textAlign: 'center', py: 8 }}>Loading settings...</Typography>;

  return (
    <Box>
      <Typography variant="h5" sx={{ fontWeight: 700, color: '#F1F5F9', mb: 3 }}>System Settings</Typography>

      <Tabs value={tab} onChange={(_, v) => setTab(v)}
        sx={{ mb: 3, '& .MuiTab-root': { color: '#64748B', textTransform: 'none' }, '& .Mui-selected': { color: '#818CF8' } }}>
        <Tab label="General" />
        <Tab label="Features" />
        <Tab label="Email Templates" />
        <Tab label="API Keys" />
        <Tab label="Security" />
        <Tab label="System Logs" />
        <Tab label="Admins" />
      </Tabs>

      {tab === 0 && (
        <Card sx={{ bgcolor: '#1E293B', borderRadius: 3 }}>
          <CardContent sx={{ p: 3 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#F1F5F9', mb: 3 }}>General Settings</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField fullWidth label="App Name" value={settings.appName || ''} onChange={(e) => setSettings({ ...settings, appName: e.target.value })}
                  sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField fullWidth label="Contact Email" value={settings.contactEmail || ''} onChange={(e) => setSettings({ ...settings, contactEmail: e.target.value })}
                  sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField fullWidth label="Support Email" value={settings.supportEmail || ''} onChange={(e) => setSettings({ ...settings, supportEmail: e.target.value })}
                  sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField fullWidth label="Max File Size (MB)" type="number" value={settings.maxFileSize || ''} onChange={(e) => setSettings({ ...settings, maxFileSize: parseInt(e.target.value) })}
                  sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
              </Grid>
            </Grid>
            <Box sx={{ mt: 3 }}>
              <FormControlLabel control={<Switch checked={maintenanceMode} onChange={handleToggleMaintenance} sx={{ '& .MuiSwitch-track': { bgcolor: maintenanceMode ? '#F87171 !important' : 'rgba(255,255,255,0.12)' }, '& .Mui-checked': { color: '#F87171' } }} />}
                label={<Typography variant="body2" sx={{ color: maintenanceMode ? '#F87171' : '#F1F5F9', fontWeight: 500 }}>Maintenance Mode</Typography>} />
              {maintenanceMode && <Alert severity="warning" sx={{ mt: 2, borderRadius: 2, bgcolor: 'rgba(251,191,36,0.1)', color: '#FBBF24' }}>Maintenance mode is enabled. Users cannot access the platform.</Alert>}
            </Box>
            <Button variant="contained" onClick={handleSaveSettings} sx={{ mt: 3, bgcolor: '#818CF8', '&:hover': { bgcolor: '#6366F1' } }}>Save Settings</Button>
          </CardContent>
        </Card>
      )}

      {tab === 1 && (
        <Card sx={{ bgcolor: '#1E293B', borderRadius: 3 }}>
          <CardContent sx={{ p: 3 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#F1F5F9', mb: 3 }}>Feature Toggles</Typography>
            {featureToggles.length === 0 ? (
              <Typography sx={{ color: '#64748B', py: 4, textAlign: 'center' }}>No feature toggles available</Typography>
            ) : featureToggles.map((feature, i) => (
              <Box key={feature.key || i} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 2, borderRadius: 2, bgcolor: 'rgba(255,255,255,0.03)', mb: 1 }}>
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: 500, color: '#F1F5F9' }}>{feature.label || feature.key}</Typography>
                  <Typography variant="caption" sx={{ color: '#64748B' }}>{feature.description || feature.key}</Typography>
                </Box>
                <Switch checked={feature.enabled} onChange={(e) => handleToggleFeature(feature.key, e.target.checked)}
                  sx={{ '& .MuiSwitch-track': { bgcolor: 'rgba(255,255,255,0.12)' } }} />
              </Box>
            ))}
          </CardContent>
        </Card>
      )}

      {tab === 2 && (
        <Box>
          {emailTemplates.length === 0 ? (
            <Typography sx={{ color: '#64748B', py: 8, textAlign: 'center' }}>No email templates configured</Typography>
          ) : emailTemplates.map((template, i) => (
            <Card key={template.key || i} sx={{ bgcolor: '#1E293B', borderRadius: 3, mb: 2 }}>
              <CardContent sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#F1F5F9' }}>{template.name || template.key}</Typography>
                  <Typography variant="caption" sx={{ color: '#64748B' }}>Subject: {template.subject || 'N/A'}</Typography>
                </Box>
                <Button size="small" onClick={() => { setEditingEmail(template); setEmailForm({ subject: template.subject || '', body: template.body || '' }); setEmailEditOpen(true); }}
                  sx={{ color: '#60A5FA' }}>Edit</Button>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      {tab === 3 && (
        <Box>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setApiKeyDialogOpen(true)}
            sx={{ mb: 2, bgcolor: '#818CF8', '&:hover': { bgcolor: '#6366F1' } }}>Create API Key</Button>
          {apiKeys.length === 0 ? (
            <Typography sx={{ color: '#64748B', py: 4, textAlign: 'center' }}>No API keys created</Typography>
          ) : (
            <TableContainer component={Card} sx={{ bgcolor: '#1E293B', borderRadius: 3 }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ color: '#64748B', borderBottom: '1px solid rgba(255,255,255,0.06)', fontWeight: 600 }}>Name</TableCell>
                    <TableCell sx={{ color: '#64748B', borderBottom: '1px solid rgba(255,255,255,0.06)', fontWeight: 600 }}>Key</TableCell>
                    <TableCell sx={{ color: '#64748B', borderBottom: '1px solid rgba(255,255,255,0.06)', fontWeight: 600 }}>Status</TableCell>
                    <TableCell sx={{ color: '#64748B', borderBottom: '1px solid rgba(255,255,255,0.06)', fontWeight: 600 }}>Created</TableCell>
                    <TableCell sx={{ color: '#64748B', borderBottom: '1px solid rgba(255,255,255,0.06)', fontWeight: 600 }}>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {apiKeys.map((key, i) => (
                    <TableRow key={key._id || key.id || i} hover sx={{ '&:hover': { bgcolor: 'rgba(255,255,255,0.03)' } }}>
                      <TableCell sx={{ color: '#F1F5F9', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>{key.name}</TableCell>
                      <TableCell sx={{ color: '#64748B', borderBottom: '1px solid rgba(255,255,255,0.04)', fontFamily: 'monospace' }}>
                        {key.key?.slice(0, 16)}...
                        <IconButton size="small" onClick={() => { navigator.clipboard.writeText(key.key); toast.success('Copied'); }} sx={{ color: '#64748B', ml: 1 }}><ContentCopyIcon fontSize="small" /></IconButton>
                      </TableCell>
                      <TableCell sx={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}><Chip label={key.isActive ? 'Active' : 'Revoked'} size="small" sx={{ bgcolor: key.isActive ? 'rgba(74,222,128,0.15)' : 'rgba(107,114,128,0.2)', color: key.isActive ? '#4ADE80' : '#9CA3AF' }} /></TableCell>
                      <TableCell sx={{ color: '#94A3B8', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>{formatDateTime(key.createdAt)}</TableCell>
                      <TableCell sx={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                        {key.isActive && <Button size="small" color="error" onClick={() => handleRevokeApiKey(key._id || key.id)} sx={{ color: '#F87171' }}>Revoke</Button>}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Box>
      )}

      {tab === 4 && (
        <Card sx={{ bgcolor: '#1E293B', borderRadius: 3 }}>
          <CardContent sx={{ p: 3 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#F1F5F9', mb: 3 }}>Security Settings</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField fullWidth type="number" label="Minimum Password Length" value={securitySettings.minPasswordLength || 8} onChange={(e) => setSecuritySettings({ ...securitySettings, minPasswordLength: parseInt(e.target.value) })}
                  sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField fullWidth type="number" label="Session Timeout (minutes)" value={securitySettings.sessionTimeout || 60} onChange={(e) => setSecuritySettings({ ...securitySettings, sessionTimeout: parseInt(e.target.value) })}
                  sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField fullWidth type="number" label="Max Login Attempts" value={securitySettings.maxLoginAttempts || 5} onChange={(e) => setSecuritySettings({ ...securitySettings, maxLoginAttempts: parseInt(e.target.value) })}
                  sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField fullWidth type="number" label="Rate Limit (requests/min)" value={securitySettings.rateLimit || 100} onChange={(e) => setSecuritySettings({ ...securitySettings, rateLimit: parseInt(e.target.value) })}
                  sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel control={<Switch checked={securitySettings.requireOtp || false} onChange={(e) => setSecuritySettings({ ...securitySettings, requireOtp: e.target.checked })} sx={{ '& .MuiSwitch-track': { bgcolor: 'rgba(255,255,255,0.12)' } }} />}
                  label={<Typography variant="body2" sx={{ color: '#F1F5F9' }}>Require OTP for Admin Login</Typography>} />
              </Grid>
            </Grid>
            <Button variant="contained" onClick={handleSaveSecurity} sx={{ mt: 3, bgcolor: '#818CF8', '&:hover': { bgcolor: '#6366F1' } }}>Save Security Settings</Button>
          </CardContent>
        </Card>
      )}

      {tab === 5 && (
        <Card sx={{ bgcolor: '#1E293B', borderRadius: 3 }}>
          <CardContent sx={{ p: 3 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#F1F5F9', mb: 2 }}>System Logs</Typography>
            {systemLogs.length === 0 ? (
              <Typography sx={{ color: '#64748B', textAlign: 'center', py: 4 }}>No system logs available</Typography>
            ) : (
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ color: '#64748B', borderBottom: '1px solid rgba(255,255,255,0.06)', fontWeight: 600 }}>Time</TableCell>
                      <TableCell sx={{ color: '#64748B', borderBottom: '1px solid rgba(255,255,255,0.06)', fontWeight: 600 }}>Level</TableCell>
                      <TableCell sx={{ color: '#64748B', borderBottom: '1px solid rgba(255,255,255,0.06)', fontWeight: 600 }}>Action</TableCell>
                      <TableCell sx={{ color: '#64748B', borderBottom: '1px solid rgba(255,255,255,0.06)', fontWeight: 600 }}>User</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {systemLogs.slice(0, 50).map((log, i) => (
                      <TableRow key={log._id || log.id || i} hover sx={{ '&:hover': { bgcolor: 'rgba(255,255,255,0.03)' } }}>
                        <TableCell sx={{ color: '#94A3B8', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>{formatDateTime(log.createdAt)}</TableCell>
                        <TableCell sx={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                          <Chip label={log.level || log.severity || 'info'} size="small"
                            sx={{ bgcolor: (log.level === 'error' || log.severity === 'error') ? 'rgba(248,113,113,0.15)' : 'rgba(96,165,250,0.15)', color: (log.level === 'error' || log.severity === 'error') ? '#F87171' : '#60A5FA' }} />
                        </TableCell>
                        <TableCell sx={{ color: '#F1F5F9', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>{log.action || log.message}</TableCell>
                        <TableCell sx={{ color: '#64748B', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>{log.user?.name || log.user || '-'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>
      )}

      {tab === 6 && (
        <Box>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setAdminDialogOpen(true)}
            sx={{ mb: 2, bgcolor: '#818CF8', '&:hover': { bgcolor: '#6366F1' } }}>Add Admin</Button>
          {admins.length === 0 ? (
            <Typography sx={{ color: '#64748B', py: 4, textAlign: 'center' }}>No admin accounts found</Typography>
          ) : admins.map((admin, i) => (
            <Card key={admin._id || admin.id || i} sx={{ bgcolor: '#1E293B', borderRadius: 3, mb: 2 }}>
              <CardContent sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#F1F5F9' }}>{admin.name}</Typography>
                  <Typography variant="caption" sx={{ color: '#64748B' }}>{admin.email}</Typography>
                </Box>
                <IconButton onClick={() => handleRemoveAdmin(admin._id || admin.id)} sx={{ color: '#F87171' }}><DeleteIcon /></IconButton>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      <Dialog open={apiKeyDialogOpen} onClose={() => setApiKeyDialogOpen(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { bgcolor: '#1E293B', color: '#F1F5F9', borderRadius: 3 } }}>
        <DialogTitle>Create API Key</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Key Name" value={newApiKeyName} onChange={(e) => setNewApiKeyName(e.target.value)}
            sx={{ mt: 2, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApiKeyDialogOpen(false)} sx={{ color: '#94A3B8' }}>Cancel</Button>
          <Button onClick={handleCreateApiKey} disabled={!newApiKeyName} variant="contained" sx={{ bgcolor: '#818CF8', '&:hover': { bgcolor: '#6366F1' } }}>Create</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={adminDialogOpen} onClose={() => setAdminDialogOpen(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { bgcolor: '#1E293B', color: '#F1F5F9', borderRadius: 3 } }}>
        <DialogTitle>Add Admin User</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Name" value={newAdmin.name} onChange={(e) => setNewAdmin({ ...newAdmin, name: e.target.value })} sx={{ mt: 2, mb: 2, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
          <TextField fullWidth label="Email" type="email" value={newAdmin.email} onChange={(e) => setNewAdmin({ ...newAdmin, email: e.target.value })} sx={{ mb: 2, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
          <TextField fullWidth label="Password" type="password" value={newAdmin.password} onChange={(e) => setNewAdmin({ ...newAdmin, password: e.target.value })} sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAdminDialogOpen(false)} sx={{ color: '#94A3B8' }}>Cancel</Button>
          <Button onClick={handleCreateAdmin} disabled={!newAdmin.name || !newAdmin.email || !newAdmin.password} variant="contained" sx={{ bgcolor: '#818CF8', '&:hover': { bgcolor: '#6366F1' } }}>Add Admin</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={emailEditOpen} onClose={() => setEmailEditOpen(false)} maxWidth="md" fullWidth PaperProps={{ sx: { bgcolor: '#1E293B', color: '#F1F5F9', borderRadius: 3 } }}>
        <DialogTitle>Edit Email Template: {editingEmail?.name || editingEmail?.key}</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Subject" value={emailForm.subject} onChange={(e) => setEmailForm({ ...emailForm, subject: e.target.value })}
            sx={{ mt: 2, mb: 2, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
          <TextField fullWidth multiline rows={12} label="Email Body (HTML)" value={emailForm.body} onChange={(e) => setEmailForm({ ...emailForm, body: e.target.value })}
            sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEmailEditOpen(false)} sx={{ color: '#94A3B8' }}>Cancel</Button>
          <Button onClick={async () => { try { await adminService.updateEmailTemplate(editingEmail.key || editingEmail._id, emailForm); toast.success('Template updated'); setEmailEditOpen(false); fetchData(); } catch {} }}
            variant="contained" sx={{ bgcolor: '#818CF8', '&:hover': { bgcolor: '#6366F1' } }}>Save Template</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
