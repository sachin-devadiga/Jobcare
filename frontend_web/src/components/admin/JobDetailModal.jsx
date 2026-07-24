'use client';
import { useState, useEffect } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions, Box, Typography,
  IconButton, Chip, Button, Divider, CircularProgress, LinearProgress, List, ListItem, ListItemText,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import FlagIcon from '@mui/icons-material/Flag';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import StarIcon from '@mui/icons-material/Star';
import DeleteIcon from '@mui/icons-material/Delete';
import adminService from '@/services/adminService';
import { formatDate, formatCurrency, formatJobType, formatExperienceLevel } from '@/utils/formatters';
import StatusBadge from './StatusBadge';
import { toast } from 'react-toastify';

export default function JobDetailModal({ open, onClose, jobId, onAction }) {
  const [job, setJob] = useState(null);
  const [flags, setFlags] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && jobId) {
      fetchJob();
    }
  }, [open, jobId]);

  const fetchJob = async () => {
    setLoading(true);
    try {
      const { data } = await adminService.getJobById(jobId);
      setJob(data);
      try {
        const flagsRes = await adminService.getJobFlags(jobId);
        setFlags(flagsRes.data || []);
      } catch {}
    } catch (err) {
      toast.error('Failed to load job details');
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (action) => {
    try {
      if (action === 'approve') await adminService.updateJobStatus(jobId, { status: 'published', moderated: true });
      else if (action === 'reject') await adminService.updateJobStatus(jobId, { status: 'closed', moderated: false });
      else if (action === 'feature') await adminService.bulkFeatureJobs([jobId]);
      else if (action === 'flag') await adminService.flagJob(jobId, { reason: 'Flagged by admin' });
      else if (action === 'remove') await adminService.bulkRemoveJobs([jobId]);
      toast.success(`Job ${action}d successfully`);
      onAction?.();
      fetchJob();
    } catch (err) {
      toast.error(err.message || `Failed to ${action} job`);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth
      PaperProps={{ sx: { bgcolor: '#1E293B', color: '#F1F5F9', borderRadius: 3 } }}>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>Job Details</Typography>
        <IconButton onClick={onClose} sx={{ color: '#64748B' }}><CloseIcon /></IconButton>
      </DialogTitle>

      <DialogContent sx={{ p: 0 }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}><CircularProgress /></Box>
        ) : job ? (
          <>
            <Box sx={{ p: 3, borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 700, mb: 0.5 }}>{job.title}</Typography>
                  <Typography variant="body2" sx={{ color: '#64748B' }}>{job.company?.companyName || job.companyName} &middot; {job.location}</Typography>
                </Box>
                <StatusBadge status={job.status} />
              </Box>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                <Chip label={formatJobType(job.type)} size="small" sx={{ bgcolor: 'rgba(96,165,250,0.15)', color: '#60A5FA', fontWeight: 500 }} />
                <Chip label={formatExperienceLevel(job.experienceLevel)} size="small" sx={{ bgcolor: 'rgba(129,140,248,0.15)', color: '#818CF8', fontWeight: 500 }} />
                {job.category && <Chip label={job.category.name || job.category} size="small" sx={{ bgcolor: 'rgba(74,222,128,0.15)', color: '#4ADE80', fontWeight: 500 }} />}
                {job.isFeatured && <Chip icon={<StarIcon />} label="Featured" size="small" sx={{ bgcolor: 'rgba(251,191,36,0.15)', color: '#FBBF24', fontWeight: 500 }} />}
                {job.isFlagged && <Chip icon={<FlagIcon />} label="Flagged" size="small" sx={{ bgcolor: 'rgba(248,113,113,0.15)', color: '#F87171', fontWeight: 500 }} />}
              </Box>
              {job.minSalary && (
                <Typography variant="body2" sx={{ color: '#4ADE80', fontWeight: 600 }}>
                  {formatCurrency(job.minSalary, job.currency)} - {formatCurrency(job.maxSalary, job.currency)}
                </Typography>
              )}
            </Box>

            {job.aiModerationScore != null && (
              <Box sx={{ px: 3, py: 2, borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.05em', fontSize: '0.75rem' }}>AI Moderation Score</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Box sx={{ flex: 1 }}>
                    <LinearProgress variant="determinate" value={job.aiModerationScore * 10}
                      sx={{ height: 8, borderRadius: 4, bgcolor: 'rgba(255,255,255,0.06)',
                        '& .MuiLinearProgress-bar': { bgcolor: job.aiModerationScore >= 7 ? '#4ADE80' : job.aiModerationScore >= 4 ? '#FBBF24' : '#F87171' } }} />
                  </Box>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: job.aiModerationScore >= 7 ? '#4ADE80' : job.aiModerationScore >= 4 ? '#FBBF24' : '#F87171' }}>
                    {job.aiModerationScore}/10
                  </Typography>
                </Box>
                {job.aiModerationNotes && (
                  <Typography variant="caption" sx={{ color: '#64748B', mt: 1, display: 'block' }}>{job.aiModerationNotes}</Typography>
                )}
              </Box>
            )}

            {flags.length > 0 && (
              <Box sx={{ px: 3, py: 2, borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.05em', fontSize: '0.75rem' }}>Reports / Flags</Typography>
                <List dense>
                  {flags.map((flag, i) => (
                    <ListItem key={i} sx={{ px: 0, py: 0.5 }}>
                      <ListItemText primary={flag.reason || 'Flagged'} secondary={`By ${flag.reportedBy?.name || 'Unknown'} on ${formatDate(flag.createdAt)}`}
                        primaryTypographyProps={{ variant: 'body2', color: '#F87171' }} secondaryTypographyProps={{ variant: 'caption', color: '#64748B' }} />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            <Box sx={{ px: 3, py: 2, borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.05em', fontSize: '0.75rem' }}>Description</Typography>
              <Typography variant="body2" sx={{ color: '#CBD5E1', whiteSpace: 'pre-wrap' }}>{job.description}</Typography>
            </Box>

            {job.requirements && (
              <Box sx={{ px: 3, py: 2, borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.05em', fontSize: '0.75rem' }}>Requirements</Typography>
                <Typography variant="body2" sx={{ color: '#CBD5E1', whiteSpace: 'pre-wrap' }}>{job.requirements}</Typography>
              </Box>
            )}

            <Box sx={{ px: 3, py: 2 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.05em', fontSize: '0.75rem' }}>Details</Typography>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                <Box><Typography variant="caption" sx={{ color: '#64748B' }}>Posted</Typography><Typography variant="body2" sx={{ color: '#F1F5F9' }}>{formatDate(job.createdAt)}</Typography></Box>
                <Box><Typography variant="caption" sx={{ color: '#64748B' }}>Applications</Typography><Typography variant="body2" sx={{ color: '#F1F5F9' }}>{job.applicationCount || job.applicationsCount || 0}</Typography></Box>
                <Box><Typography variant="caption" sx={{ color: '#64748B' }}>Views</Typography><Typography variant="body2" sx={{ color: '#F1F5F9' }}>{job.views || 0}</Typography></Box>
                <Box><Typography variant="caption" sx={{ color: '#64748B' }}>Category</Typography><Typography variant="body2" sx={{ color: '#F1F5F9' }}>{job.category?.name || job.category || 'N/A'}</Typography></Box>
              </Box>
            </Box>
          </>
        ) : null}
      </DialogContent>

      <DialogActions sx={{ p: 3, borderTop: '1px solid rgba(255,255,255,0.06)', gap: 1, flexWrap: 'wrap' }}>
        <Button size="small" variant="contained" color="success" startIcon={<CheckCircleIcon />} onClick={() => handleAction('approve')}>Approve</Button>
        <Button size="small" variant="contained" color="warning" startIcon={<CancelIcon />} onClick={() => handleAction('reject')}>Reject</Button>
        <Button size="small" variant="contained" color="info" startIcon={<StarIcon />} onClick={() => handleAction('feature')}>Feature</Button>
        <Button size="small" variant="contained" color="error" startIcon={<DeleteIcon />} onClick={() => handleAction('remove')}>Remove</Button>
      </DialogActions>
    </Dialog>
  );
}
