'use client';
import { Box, Card, CardContent, Typography, Skeleton } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';

export default function StatsCard({ icon, label, value, subtitle, trend, color = '#818CF8', bgColor = 'rgba(129,140,248,0.1)', loading = false, onClick, prefix, suffix }) {
  if (loading) {
    return (
      <Card sx={{ borderRadius: 3, bgcolor: '#1E293B' }}>
        <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
          <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
            <Box sx={{ flex: 1 }}>
              <Skeleton variant="text" width={80} height={20} sx={{ mb: 1, bgcolor: 'rgba(255,255,255,0.08)' }} />
              <Skeleton variant="text" width={120} height={40} sx={{ mb: 1, bgcolor: 'rgba(255,255,255,0.08)' }} />
              <Skeleton variant="text" width={100} height={20} sx={{ bgcolor: 'rgba(255,255,255,0.08)' }} />
            </Box>
            <Skeleton variant="rounded" width={56} height={56} sx={{ borderRadius: 3, bgcolor: 'rgba(255,255,255,0.08)' }} />
          </Box>
        </CardContent>
      </Card>
    );
  }

  const displayValue = typeof value === 'number' && value >= 1000000
    ? `${(value / 1000000).toFixed(1)}M`
    : typeof value === 'number' && value >= 1000
      ? `${(value / 1000).toFixed(1)}K`
      : typeof value === 'number' ? value.toLocaleString() : value || '0';

  return (
    <Card
      onClick={onClick}
      sx={{
        borderRadius: 3, bgcolor: '#1E293B', cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.2s', '&:hover': onClick ? { transform: 'translateY(-2px)', boxShadow: '0 8px 25px rgba(0,0,0,0.3)' } : {},
      }}
    >
      <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography variant="body2" sx={{ color: '#64748B', fontWeight: 500, mb: 1 }}>{label}</Typography>
            <Typography variant="h4" sx={{ fontWeight: 700, mb: 1, fontVariantNumeric: 'tabular-nums', color: '#F1F5F9' }}>
              {prefix}{displayValue}{suffix}
            </Typography>
            {trend != null && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                {trend >= 0 ? <TrendingUpIcon sx={{ fontSize: 18, color: '#4ADE80' }} /> : <TrendingDownIcon sx={{ fontSize: 18, color: '#F87171' }} />}
                <Typography variant="caption" sx={{ fontWeight: 600, color: trend >= 0 ? '#4ADE80' : '#F87171' }}>
                  {Math.abs(trend)}%
                </Typography>
                {subtitle && <Typography variant="caption" sx={{ color: '#64748B' }}>{subtitle}</Typography>}
              </Box>
            )}
          </Box>
          <Box sx={{ width: 56, height: 56, borderRadius: 3, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor, color, flexShrink: 0 }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}
