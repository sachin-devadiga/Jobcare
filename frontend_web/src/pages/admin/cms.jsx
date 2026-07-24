'use client';
import { useState, useEffect, useCallback } from 'react';
import {
  Box, Typography, TextField, Button, Dialog, DialogTitle, DialogContent, DialogActions,
  Tabs, Tab, Grid, Card, CardContent, IconButton, Chip, Alert, Avatar, MenuItem,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import CampaignIcon from '@mui/icons-material/Campaign';
import BannerIcon from '@mui/icons-material/ViewCarousel';
import NotificationsIcon from '@mui/icons-material/Notifications';
import StarIcon from '@mui/icons-material/Star';
import WorkIcon from '@mui/icons-material/Work';
import adminService from '@/services/adminService';
import { toast } from 'react-toastify';
import { formatDate } from '@/utils/formatters';

const contentSectionKeys = ['about', 'privacy', 'terms', 'help'];

export default function AdminCMSPage() {
  const [tab, setTab] = useState(0);
  const [banners, setBanners] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [featuredCompanies, setFeaturedCompanies] = useState([]);
  const [featuredJobs, setFeaturedJobs] = useState([]);
  const [contentSections, setContentSections] = useState({});
  const [loading, setLoading] = useState(true);
  const [bannerDialogOpen, setBannerDialogOpen] = useState(false);
  const [editingBanner, setEditingBanner] = useState(null);
  const [bannerForm, setBannerForm] = useState({ title: '', subtitle: '', imageUrl: '', linkUrl: '', isActive: true });
  const [announcementForm, setAnnouncementForm] = useState({ title: '', message: '', type: 'info' });
  const [announceDialogOpen, setAnnounceDialogOpen] = useState(false);
  const [broadcastForm, setBroadcastForm] = useState({ title: '', message: '', type: 'info' });
  const [broadcastOpen, setBroadcastOpen] = useState(false);
  const [contentEditOpen, setContentEditOpen] = useState(false);
  const [editingSection, setEditingSection] = useState(null);
  const [sectionForm, setSectionForm] = useState({ title: '', content: '' });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [bannersRes, announcementsRes, companiesRes, jobsRes, sectionsRes] = await Promise.all([
        adminService.getBanners({ limit: 50 }),
        adminService.getAnnouncements({ limit: 50 }),
        adminService.getFeaturedCompanies({ limit: 50 }),
        adminService.getFeaturedJobs({ limit: 50 }),
        adminService.getContentSections(),
      ]);
      setBanners(bannersRes.data.banners || bannersRes.data || []);
      setAnnouncements(announcementsRes.data.announcements || announcementsRes.data || []);
      setFeaturedCompanies(companiesRes.data.companies || companiesRes.data || []);
      setFeaturedJobs(jobsRes.data.jobs || jobsRes.data || []);
      setContentSections(sectionsRes.data || {});
    } catch (err) { toast.error('Failed to load CMS data'); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleSaveBanner = async () => {
    if (!bannerForm.title) return;
    try {
      if (editingBanner) await adminService.updateBanner(editingBanner._id || editingBanner.id, bannerForm);
      else await adminService.createBanner(bannerForm);
      toast.success(editingBanner ? 'Banner updated' : 'Banner created');
      setBannerDialogOpen(false);
      setEditingBanner(null);
      setBannerForm({ title: '', subtitle: '', imageUrl: '', linkUrl: '', isActive: true });
      fetchData();
    } catch (err) { toast.error(err.message || 'Failed to save banner'); }
  };

  const handleDeleteBanner = async (banner) => {
    try {
      await adminService.deleteBanner(banner._id || banner.id);
      toast.success('Banner deleted');
      fetchData();
    } catch (err) { toast.error('Failed to delete banner'); }
  };

  const handleSaveAnnouncement = async () => {
    if (!announcementForm.title) return;
    try {
      await adminService.createAnnouncement(announcementForm);
      toast.success('Announcement created');
      setAnnounceDialogOpen(false);
      setAnnouncementForm({ title: '', message: '', type: 'info' });
      fetchData();
    } catch (err) { toast.error('Failed to create announcement'); }
  };

  const handleBroadcast = async () => {
    if (!broadcastForm.title) return;
    try {
      await adminService.broadcastNotification(broadcastForm);
      toast.success('Notification broadcasted to all users');
      setBroadcastOpen(false);
      setBroadcastForm({ title: '', message: '', type: 'info' });
    } catch (err) { toast.error('Failed to broadcast'); }
  };

  const handleSaveSection = async () => {
    if (!editingSection) return;
    try {
      await adminService.updateContentSection(editingSection, sectionForm);
      toast.success('Section updated');
      setContentEditOpen(false);
      fetchData();
    } catch (err) { toast.error('Failed to update section'); }
  };

  return (
    <Box>
      <Typography variant="h5" sx={{ fontWeight: 700, color: '#F1F5F9', mb: 3 }}>Content Management</Typography>

      <Tabs value={tab} onChange={(_, v) => setTab(v)}
        sx={{ mb: 3, '& .MuiTab-root': { color: '#64748B', textTransform: 'none' }, '& .Mui-selected': { color: '#818CF8' } }}>
        <Tab icon={<BannerIcon />} label="Banners" />
        <Tab icon={<CampaignIcon />} label="Announcements" />
        <Tab icon={<NotificationsIcon />} label="Broadcast" />
        <Tab icon={<StarIcon />} label="Featured Companies" />
        <Tab icon={<WorkIcon />} label="Featured Jobs" />
        <Tab label="Content Sections" />
      </Tabs>

      {tab === 0 && (
        <Box>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => { setEditingBanner(null); setBannerForm({ title: '', subtitle: '', imageUrl: '', linkUrl: '', isActive: true }); setBannerDialogOpen(true); }}
            sx={{ mb: 2, bgcolor: '#818CF8', '&:hover': { bgcolor: '#6366F1' } }}>Add Banner</Button>
          {banners.length === 0 ? (
            <Typography sx={{ color: '#64748B', textAlign: 'center', py: 8 }}>No banners yet</Typography>
          ) : (
            <Grid container spacing={2}>
              {banners.map((banner, i) => (
                <Grid item xs={12} sm={6} md={4} key={banner._id || banner.id || i}>
                  <Card sx={{ bgcolor: '#1E293B', borderRadius: 3 }}>
                    <Box sx={{ height: 140, borderRadius: '12px 12px 0 0', background: `url(${banner.imageUrl}) center/cover`, bgcolor: 'rgba(129,140,248,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      {!banner.imageUrl && <BannerIcon sx={{ fontSize: 48, color: '#64748B' }} />}
                    </Box>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <Box>
                          <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#F1F5F9' }}>{banner.title}</Typography>
                          <Typography variant="caption" sx={{ color: '#64748B' }}>{banner.subtitle}</Typography>
                        </Box>
                        <Box>
                          <IconButton size="small" onClick={() => { setEditingBanner(banner); setBannerForm({ title: banner.title, subtitle: banner.subtitle || '', imageUrl: banner.imageUrl || '', linkUrl: banner.linkUrl || '', isActive: banner.isActive }); setBannerDialogOpen(true); }} sx={{ color: '#60A5FA' }}><EditIcon fontSize="small" /></IconButton>
                          <IconButton size="small" onClick={() => handleDeleteBanner(banner)} sx={{ color: '#F87171' }}><DeleteIcon fontSize="small" /></IconButton>
                        </Box>
                      </Box>
                      <Box sx={{ mt: 1 }}>
                        <Chip label={banner.isActive ? 'Active' : 'Inactive'} size="small" sx={{ bgcolor: banner.isActive ? 'rgba(74,222,128,0.15)' : 'rgba(107,114,128,0.2)', color: banner.isActive ? '#4ADE80' : '#9CA3AF' }} />
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      )}

      {tab === 1 && (
        <Box>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => { setAnnouncementForm({ title: '', message: '', type: 'info' }); setAnnounceDialogOpen(true); }}
            sx={{ mb: 2, bgcolor: '#818CF8', '&:hover': { bgcolor: '#6366F1' } }}>Create Announcement</Button>
          {announcements.length === 0 ? (
            <Typography sx={{ color: '#64748B', textAlign: 'center', py: 8 }}>No announcements yet</Typography>
          ) : announcements.map((ann, i) => (
            <Card key={ann._id || ann.id || i} sx={{ bgcolor: '#1E293B', borderRadius: 3, mb: 2 }}>
              <CardContent sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#F1F5F9' }}>{ann.title}</Typography>
                  <Typography variant="body2" sx={{ color: '#94A3B8', mt: 0.5 }}>{ann.message}</Typography>
                  <Typography variant="caption" sx={{ color: '#64748B', mt: 1, display: 'block' }}>{formatDate(ann.createdAt)}</Typography>
                </Box>
                <Chip label={ann.type} size="small" sx={{ bgcolor: `rgba(${ann.type === 'info' ? '96,165,250' : ann.type === 'warning' ? '251,191,36' : '248,113,113'},0.15)`, color: ann.type === 'info' ? '#60A5FA' : ann.type === 'warning' ? '#FBBF24' : '#F87171' }} />
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      {tab === 2 && (
        <Card sx={{ bgcolor: '#1E293B', borderRadius: 3, p: 3 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#F1F5F9', mb: 2 }}>Broadcast Notification to All Users</Typography>
          <TextField fullWidth label="Title" value={broadcastForm.title} onChange={(e) => setBroadcastForm({ ...broadcastForm, title: e.target.value })}
            sx={{ mb: 2, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
          <TextField fullWidth multiline rows={4} label="Message" value={broadcastForm.message} onChange={(e) => setBroadcastForm({ ...broadcastForm, message: e.target.value })}
            sx={{ mb: 2, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
          <TextField select fullWidth label="Type" value={broadcastForm.type} onChange={(e) => setBroadcastForm({ ...broadcastForm, type: e.target.value })}
            sx={{ mb: 2, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }}>
            <MenuItem value="info">Info</MenuItem>
            <MenuItem value="warning">Warning</MenuItem>
            <MenuItem value="success">Success</MenuItem>
            <MenuItem value="error">Error</MenuItem>
          </TextField>
          <Button variant="contained" onClick={handleBroadcast} disabled={!broadcastForm.title || !broadcastForm.message}
            sx={{ bgcolor: '#818CF8', '&:hover': { bgcolor: '#6366F1' } }}>Send Broadcast</Button>
        </Card>
      )}

      {tab === 3 && (
        <Box>
          <Typography variant="subtitle2" sx={{ color: '#94A3B8', mb: 2 }}>Currently featured companies will be highlighted on the app home screen.</Typography>
          {featuredCompanies.length === 0 ? <Typography sx={{ color: '#64748B', py: 4 }}>No featured companies</Typography>
            : featuredCompanies.map((company, i) => (
              <Card key={company._id || company.id || i} sx={{ bgcolor: '#1E293B', borderRadius: 3, mb: 2 }}>
                <CardContent sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Avatar src={company.logo} sx={{ width: 48, height: 48, bgcolor: 'rgba(129,140,248,0.15)' }}>{company.companyName?.[0] || 'C'}</Avatar>
                    <Box>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#F1F5F9' }}>{company.companyName || company.name}</Typography>
                      <Typography variant="caption" sx={{ color: '#64748B' }}>Featured since {formatDate(company.featuredAt || company.createdAt)}</Typography>
                    </Box>
                  </Box>
                  <Button size="small" color="error" onClick={async () => { try { await adminService.removeFeaturedCompany(company._id || company.id); fetchData(); toast.success('Removed'); } catch {} }}
                    sx={{ color: '#F87171' }}>Remove</Button>
                </CardContent>
              </Card>
            ))}
        </Box>
      )}

      {tab === 4 && (
        <Box>
          <Typography variant="subtitle2" sx={{ color: '#94A3B8', mb: 2 }}>Featured jobs appear in a dedicated section on the home screen.</Typography>
          {featuredJobs.length === 0 ? <Typography sx={{ color: '#64748B', py: 4 }}>No featured jobs</Typography>
            : featuredJobs.map((job, i) => (
              <Card key={job._id || job.id || i} sx={{ bgcolor: '#1E293B', borderRadius: 3, mb: 2 }}>
                <CardContent sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#F1F5F9' }}>{job.title}</Typography>
                    <Typography variant="caption" sx={{ color: '#64748B' }}>{job.company?.companyName || job.companyName}</Typography>
                  </Box>
                  <Button size="small" color="error" onClick={async () => { try { await adminService.removeFeaturedJob(job._id || job.id); fetchData(); toast.success('Removed'); } catch {} }}
                    sx={{ color: '#F87171' }}>Remove</Button>
                </CardContent>
              </Card>
            ))}
        </Box>
      )}

      {tab === 5 && (
        <Grid container spacing={2}>
          {contentSectionKeys.map((key) => {
            const section = contentSections[key] || {};
            return (
              <Grid item xs={12} md={6} key={key}>
                <Card sx={{ bgcolor: '#1E293B', borderRadius: 3 }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#F1F5F9', textTransform: 'capitalize' }}>{key}</Typography>
                      <IconButton size="small" onClick={() => { setEditingSection(key); setSectionForm({ title: section.title || '', content: section.content || '' }); setContentEditOpen(true); }} sx={{ color: '#60A5FA' }}>
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Box>
                    <Typography variant="body2" sx={{ color: '#94A3B8' }}>{section.title || 'No title set'}</Typography>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}

      <Dialog open={bannerDialogOpen} onClose={() => setBannerDialogOpen(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { bgcolor: '#1E293B', color: '#F1F5F9', borderRadius: 3 } }}>
        <DialogTitle>{editingBanner ? 'Edit Banner' : 'Add Banner'}</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Title" value={bannerForm.title} onChange={(e) => setBannerForm({ ...bannerForm, title: e.target.value })} sx={{ mt: 2, mb: 2, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
          <TextField fullWidth label="Subtitle" value={bannerForm.subtitle} onChange={(e) => setBannerForm({ ...bannerForm, subtitle: e.target.value })} sx={{ mb: 2, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
          <TextField fullWidth label="Image URL" value={bannerForm.imageUrl} onChange={(e) => setBannerForm({ ...bannerForm, imageUrl: e.target.value })} sx={{ mb: 2, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
          <TextField fullWidth label="Link URL" value={bannerForm.linkUrl} onChange={(e) => setBannerForm({ ...bannerForm, linkUrl: e.target.value })} sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBannerDialogOpen(false)} sx={{ color: '#94A3B8' }}>Cancel</Button>
          <Button onClick={handleSaveBanner} disabled={!bannerForm.title} variant="contained" sx={{ bgcolor: '#818CF8', '&:hover': { bgcolor: '#6366F1' } }}>Save</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={announceDialogOpen} onClose={() => setAnnounceDialogOpen(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { bgcolor: '#1E293B', color: '#F1F5F9', borderRadius: 3 } }}>
        <DialogTitle>Create Announcement</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Title" value={announcementForm.title} onChange={(e) => setAnnouncementForm({ ...announcementForm, title: e.target.value })} sx={{ mt: 2, mb: 2, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
          <TextField fullWidth multiline rows={3} label="Message" value={announcementForm.message} onChange={(e) => setAnnouncementForm({ ...announcementForm, message: e.target.value })} sx={{ mb: 2, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAnnounceDialogOpen(false)} sx={{ color: '#94A3B8' }}>Cancel</Button>
          <Button onClick={handleSaveAnnouncement} disabled={!announcementForm.title} variant="contained" sx={{ bgcolor: '#818CF8', '&:hover': { bgcolor: '#6366F1' } }}>Create</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={contentEditOpen} onClose={() => setContentEditOpen(false)} maxWidth="md" fullWidth PaperProps={{ sx: { bgcolor: '#1E293B', color: '#F1F5F9', borderRadius: 3 } }}>
        <DialogTitle>Edit {editingSection?.charAt(0).toUpperCase() + editingSection?.slice(1)} Section</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Section Title" value={sectionForm.title} onChange={(e) => setSectionForm({ ...sectionForm, title: e.target.value })}
            sx={{ mt: 2, mb: 2, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
          <TextField fullWidth multiline rows={12} label="Content (HTML/Markdown)" value={sectionForm.content} onChange={(e) => setSectionForm({ ...sectionForm, content: e.target.value })}
            sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setContentEditOpen(false)} sx={{ color: '#94A3B8' }}>Cancel</Button>
          <Button onClick={handleSaveSection} variant="contained" sx={{ bgcolor: '#818CF8', '&:hover': { bgcolor: '#6366F1' } }}>Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
