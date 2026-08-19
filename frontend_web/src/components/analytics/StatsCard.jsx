'use client';
import { useState, useEffect, useRef } from 'react';
import {
  Box, Card, CardContent, Typography, Tooltip, Skeleton
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import { Area, AreaChart, ResponsiveContainer } from 'recharts';
import { STATS_COLOR_VARIANTS } from '@/utils/constants';

function useAnimatedCounter(target, duration = 1000) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);

  useEffect(() => {
    const targetNum = typeof target === 'string' ? parseFloat(target.replace(/[^0-9.-]/g, '')) : Number(target) || 0;
    if (targetNum === 0) { setCount(0); return; }
    if (typeof requestAnimationFrame !== 'function' || !document.hasFocus()) { setCount(targetNum); return; }
    const startTime = performance.now();
    const startValue = 0;

    const animate = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const current = startValue + (targetNum - startValue) * easeOut;
      setCount(current);
      if (progress < 1) requestAnimationFrame(animate);
    };

    requestAnimationFrame(animate);
    return () => { };
  }, [target, duration]);

  if (typeof target === 'string') {
    const match = target.match(/^([\d,.]+)(.*)$/);
    if (match) {
      const num = parseInt(match[1].replace(/,/g, ''), 10);
      if (isNaN(num)) return target;
      return `${Math.round(count)}${match[2]}`;
    }
    return target;
  }
  if (target >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
  if (target >= 1000) return `${(count / 1000).toFixed(1)}K`;
  return Math.round(count).toLocaleString();
}

export default function StatsCard({
  icon,
  label,
  value,
  trend,
  trendLabel,
  color = 'primary',
  variant = 'primary',
  bgColor,
  tooltipTitle,
  sparklineData,
  loading = false,
  prefix,
  suffix,
}) {
  const resolvedColor = STATS_COLOR_VARIANTS[variant] || STATS_COLOR_VARIANTS.primary;
  const iconBg = bgColor || resolvedColor.bg;
  const iconColor = resolvedColor.icon;

  const displayValue = useAnimatedCounter(loading ? 0 : value);

  if (loading) {
    return (
      <Card sx={{ borderRadius: 3 }}>
        <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
          <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
            <Box sx={{ flex: 1 }}>
              <Skeleton variant="text" width={80} height={20} sx={{ mb: 1 }} />
              <Skeleton variant="text" width={120} height={40} sx={{ mb: 1 }} />
              <Skeleton variant="text" width={100} height={20} />
            </Box>
            <Skeleton variant="rounded" width={56} height={56} sx={{ borderRadius: 3 }} />
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      sx={{
        borderRadius: 3,
        transition: 'all 0.2s',
        '&:hover': { transform: 'translateY(-2px)', boxShadow: 4 },
        position: 'relative',
        overflow: 'visible',
      }}
    >
      <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
              <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                {label}
              </Typography>
              {tooltipTitle && (
                <Tooltip title={tooltipTitle} arrow placement="top">
                  <InfoOutlinedIcon sx={{ fontSize: 14, color: 'text.disabled', cursor: 'help' }} />
                </Tooltip>
              )}
            </Box>
            <Typography variant="h4" sx={{ fontWeight: 700, mb: 1, fontVariantNumeric: 'tabular-nums' }}>
              {prefix}{displayValue}{suffix}
            </Typography>
            {trend != null && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                {trend >= 0 ? (
                  <TrendingUpIcon sx={{ fontSize: 18, color: 'success.main' }} />
                ) : (
                  <TrendingDownIcon sx={{ fontSize: 18, color: 'error.main' }} />
                )}
                <Typography
                  variant="caption"
                  sx={{ fontWeight: 600, color: trend >= 0 ? 'success.main' : 'error.main' }}
                >
                  {Math.abs(trend)}%
                </Typography>
                {trendLabel && (
                  <Typography variant="caption" color="text.secondary">{trendLabel}</Typography>
                )}
              </Box>
            )}
          </Box>
          <Box
            sx={{
              width: 56,
              height: 56,
              borderRadius: 3,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: iconBg,
              color: iconColor,
              flexShrink: 0,
            }}
          >
            {icon}
          </Box>
        </Box>

        {sparklineData && sparklineData.length > 0 && (
          <Box sx={{ mt: 2, height: 50 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={sparklineData}>
                <defs>
                  <linearGradient id={`sparkline-grad-${label.replace(/\s/g, '')}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={iconColor} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={iconColor} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke={iconColor}
                  strokeWidth={2}
                  fill={`url(#sparkline-grad-${label.replace(/\s/g, '')})`}
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
