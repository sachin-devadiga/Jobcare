'use client';
import { useState } from 'react';
import {
  Card, CardContent, Typography, Box, Chip, IconButton, Menu, MenuItem,
  ListItemIcon, Divider, Tooltip, LinearProgress,
} from '@mui/material';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import PublishIcon from '@mui/icons-material/Publish';
import CloseIcon from '@mui/icons-material/Close';
import ArchiveIcon from '@mui/icons-material/Archive';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import VisibilityIcon from '@mui/icons-material/Visibility';
import PeopleIcon from '@mui/icons-material/People';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import StatusBadge from '@/components/common/StatusBadge';
import { formatRelativeTime, formatJobType, formatSalaryRange, formatNumber } from '@/utils/formatters';
import { useRouter } from 'next/navigation';

export default function JobCard({ job, onEdit, onDelete, onPublish, onClose, onArchive, onDuplicate }) {
  const [anchorEl, setAnchorEl] = useState(null);
  const router = useRouter();

  const menuItems = [
    { label: 'Edit', icon: <EditIcon fontSize="small" />, action: () => onEdit?.(job._id || job.id), show: true },
    { label: 'Publish', icon: <PublishIcon fontSize="small" />, action: () => onPublish?.(job._id || job.id), show: job.status === 'draft' || job.status === 'closed' },
    { label: 'Close', icon: <CloseIcon fontSize="small" />, action: () => onClose?.(job._id || job.id), show: job.status === 'published' },
    { label: 'Archive', icon: <ArchiveIcon fontSize="small" />, action: () => onArchive?.(job._id || job.id), show: job.status !== 'archived' },
    { label: 'Duplicate', icon: <ContentCopyIcon fontSize="small" />, action: () => onDuplicate?.(job._id || job.id), show: true },
    { label: 'Delete', icon: <DeleteIcon fontSize="small" />, action: () => onDelete?.(job._id || job.id), show: true, color: 'error.main' },
  ];

  const stats = [
    { icon: <VisibilityIcon sx={{ fontSize: 16 }} />, value: formatNumber(job.views || 0), label: 'Views' },
    { icon: <PeopleIcon sx={{ fontSize: 16 }} />, value: formatNumber(job.applications || 0), label: 'Applications' },
    { icon: <BookmarkIcon sx={{ fontSize: 16 }} />, value: formatNumber(job.saves || 0), label: 'Saves' },
  ];

  return (
    <Card
      sx={{
        borderRadius: 3,
        transition: 'all 0.2s ease',
        cursor: 'pointer',
        '&:hover': { transform: 'translateY(-2px)', boxShadow: 4 },
      }}
      onClick={() => router.push(`/employer/jobs/${job._id || job.id}`)}
    >
      <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1.5 }}>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, fontSize: '1.05rem', truncate: true }}>
                {job.title}
              </Typography>
              <StatusBadge status={job.status} />
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
              <LocationOnIcon sx={{ fontSize: 16 }} />
              {job.location} &middot; {formatJobType(job.type)}
            </Typography>
          </Box>
          <IconButton
            size="small"
            onClick={(e) => { e.stopPropagation(); setAnchorEl(e.currentTarget); }}
            sx={{ flexShrink: 0 }}
          >
            <MoreVertIcon fontSize="small" />
          </IconButton>
        </Box>

        {job.minSalary && (
          <Typography variant="body2" color="primary" sx={{ fontWeight: 600, mb: 1.5 }}>
            {formatSalaryRange(job.minSalary, job.maxSalary, job.currency)}
          </Typography>
        )}

        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
          {(job.skills || []).slice(0, 4).map((skill) => (
            <Chip key={skill} label={skill} size="small" variant="outlined" sx={{ borderRadius: 1.5, fontSize: '0.75rem' }} />
          ))}
          {(job.skills || []).length > 4 && (
            <Chip label={`+${job.skills.length - 4}`} size="small" sx={{ borderRadius: 1.5, fontSize: '0.75rem' }} />
          )}
        </Box>

        <Divider sx={{ my: 1.5 }} />

        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            {stats.map((stat, idx) => (
              <Tooltip key={idx} title={stat.label}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Box sx={{ color: 'text.secondary', display: 'flex' }}>{stat.icon}</Box>
                  <Typography variant="caption" sx={{ fontWeight: 600 }}>{stat.value}</Typography>
                </Box>
              </Tooltip>
            ))}
          </Box>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <CalendarTodayIcon sx={{ fontSize: 14 }} />
            {formatRelativeTime(job.createdAt)}
          </Typography>
        </Box>
      </CardContent>

      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)} onClick={() => setAnchorEl(null)}>
        {menuItems.filter(m => m.show).map((item) => (
          <MenuItem
            key={item.label}
            onClick={(e) => { e.stopPropagation(); item.action(); }}
            sx={item.color ? { color: item.color } : {}}
          >
            <ListItemIcon sx={item.color ? { color: item.color } : {}}>{item.icon}</ListItemIcon>
            {item.label}
          </MenuItem>
        ))}
      </Menu>
    </Card>
  );
}
