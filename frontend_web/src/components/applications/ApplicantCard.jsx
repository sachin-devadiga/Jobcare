'use client';
import { Box, Card, CardContent, Typography, Avatar, Chip, IconButton, LinearProgress } from '@mui/material';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import StatusBadge from '@/components/common/StatusBadge';
import { getInitials, getAvatarColor } from '@/utils/helpers';
import { formatRelativeTime } from '@/utils/formatters';
import { useRouter } from 'next/navigation';

export default function ApplicantCard({ applicant }) {
  const router = useRouter();
  const name = applicant.name || applicant.fullName || 'Unknown';
  const matchScore = applicant.matchScore || applicant.aiScore || 0;

  return (
    <Card
      sx={{
        borderRadius: 3,
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        '&:hover': { transform: 'translateY(-2px)', boxShadow: 4 },
      }}
      onClick={() => router.push(`/employer/applicants/${applicant._id || applicant.id}`)}
    >
      <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
          <Avatar
            sx={{
              width: 52,
              height: 52,
              bgcolor: getAvatarColor(name),
              fontWeight: 600,
              fontSize: '1.1rem',
            }}
            src={applicant.avatar}
          >
            {getInitials(name)}
          </Avatar>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, truncate: true }}>
                {name}
              </Typography>
              <StatusBadge status={applicant.status} size="small" />
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
              {applicant.currentPosition || applicant.headline || 'Candidate'}
            </Typography>
            {applicant.location && (
              <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1.5 }}>
                <LocationOnIcon sx={{ fontSize: 14 }} />
                {applicant.location}
              </Typography>
            )}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Applied {formatRelativeTime(applicant.createdAt || applicant.appliedAt)}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
              {(applicant.skills || []).slice(0, 3).map((skill) => (
                <Chip key={skill} label={skill} size="small" variant="outlined" sx={{ borderRadius: 1.5, fontSize: '0.7rem' }} />
              ))}
              {(applicant.skills || []).length > 3 && (
                <Chip label={`+${applicant.skills.length - 3}`} size="small" sx={{ borderRadius: 1.5, fontSize: '0.7rem' }} />
              )}
            </Box>
          </Box>
        </Box>

        {matchScore > 0 && (
          <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="caption" color="text.secondary">AI Match Score</Typography>
              <Typography variant="caption" sx={{ fontWeight: 700, color: matchScore >= 70 ? 'success.main' : matchScore >= 40 ? 'warning.main' : 'text.secondary' }}>
                {matchScore}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={matchScore}
              sx={{
                height: 6,
                borderRadius: 3,
                bgcolor: 'rgba(0,0,0,0.05)',
                '& .MuiLinearProgress-bar': {
                  bgcolor: matchScore >= 70 ? 'success.main' : matchScore >= 40 ? 'warning.main' : 'text.disabled',
                  borderRadius: 3,
                },
              }}
            />
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
