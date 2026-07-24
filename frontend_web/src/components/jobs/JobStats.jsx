'use client';
import { Box, Card, CardContent, Typography, Grid, LinearProgress } from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import PeopleIcon from '@mui/icons-material/People';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import ThumbUpIcon from '@mui/icons-material/ThumbUp';
import { formatNumber } from '@/utils/formatters';

export default function JobStats({ stats }) {
  if (!stats) return null;

  const statCards = [
    { icon: <VisibilityIcon />, label: 'Views', value: formatNumber(stats.views || 0), color: '#6366F1', bg: 'rgba(99,102,241,0.1)' },
    { icon: <PeopleIcon />, label: 'Applications', value: formatNumber(stats.applications || 0), color: '#22C55E', bg: 'rgba(34,197,94,0.1)' },
    { icon: <BookmarkIcon />, label: 'Saves', value: formatNumber(stats.saves || 0), color: '#F59E0B', bg: 'rgba(245,158,11,0.1)' },
    { icon: <ThumbUpIcon />, label: 'Interviews', value: formatNumber(stats.interviews || 0), color: '#EC4899', bg: 'rgba(236,72,153,0.1)' },
  ];

  return (
    <Card sx={{ borderRadius: 3, mb: 3 }}>
      <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>Job Performance</Typography>
        <Grid container spacing={3}>
          {statCards.map((stat, idx) => (
            <Grid item xs={6} sm={3} key={idx}>
              <Box sx={{ textAlign: 'center' }}>
                <Box sx={{ width: 48, height: 48, borderRadius: 2, bgcolor: stat.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', mx: 'auto', mb: 1, color: stat.color }}>
                  {stat.icon}
                </Box>
                <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>{stat.value}</Typography>
                <Typography variant="body2" color="text.secondary">{stat.label}</Typography>
              </Box>
            </Grid>
          ))}
        </Grid>

        {stats.conversionRate != null && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              Application Conversion Rate: {stats.conversionRate}%
            </Typography>
            <LinearProgress
              variant="determinate"
              value={Math.min(stats.conversionRate, 100)}
              sx={{ height: 8, borderRadius: 4, bgcolor: 'rgba(99,102,241,0.1)' }}
            />
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
