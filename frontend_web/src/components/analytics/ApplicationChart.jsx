'use client';
import { useState } from 'react';
import {
  Box, Card, CardContent, Typography, useTheme, IconButton, Skeleton,
  Tooltip as MuiTooltip
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Cell, LabelList,
} from 'recharts';
import { CHART_COLORS } from '@/utils/constants';

const DEFAULT_FUNNEL_COLORS = [
  '#6366F1', '#7C3AED', '#8B5CF6', '#A78BFA', '#C4B5FD',
  '#22C55E', '#F59E0B', '#EF4444',
];

function FunnelTooltip({ active, payload, label, conversionRates }) {
  if (active && payload && payload.length) {
    const entry = payload[0];
    const idx = entry.payload.index;
    const prevRate = idx > 0 ? conversionRates[idx - 1] : null;
    return (
      <Box
        sx={{
          bgcolor: 'background.paper', p: 1.5, borderRadius: 2, boxShadow: 3,
          border: '1px solid', borderColor: 'divider', minWidth: 160,
        }}
      >
        <Typography variant="caption" sx={{ fontWeight: 600, display: 'block', mb: 0.5 }}>
          {label}
        </Typography>
        <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: entry.color }}>
          <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: entry.color }} />
          {entry.name}: <strong>{entry.value.toLocaleString()}</strong>
        </Typography>
        {prevRate !== null && (
          <Typography variant="caption" sx={{ display: 'block', mt: 0.5, color: 'text.secondary' }}>
            Conversion: <strong>{prevRate}%</strong>
          </Typography>
        )}
      </Box>
    );
  }
  return null;
}

function ChartSkeleton({ height }) {
  return (
    <Box sx={{ height, display: 'flex', flexDirection: 'column', gap: 1, p: 1 }}>
      <Skeleton variant="rounded" width="80%" height={20} />
      {[0, 1, 2, 3, 4].map((i) => (
        <Skeleton key={i} variant="rounded" width={`${100 - i * 12}%`} height={32} />
      ))}
    </Box>
  );
}

export default function ApplicationChart({
  data,
  title = 'Application Funnel',
  height = 350,
  loading = false,
  onDrillDown,
  funnelColors = DEFAULT_FUNNEL_COLORS,
  showConversionLabels = true,
}) {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const [drillLevel, setDrillLevel] = useState(null);

  const hasDrillData = data.some((d) => d.children && d.children.length > 0);

  const displayData = drillLevel
    ? (data.find((d) => d.name === drillLevel)?.children || data)
    : data;

  const maxVal = Math.max(...displayData.map((d) => d.value || 0), 1);

  const conversionRates = displayData.map((d, idx) => {
    if (idx === 0) return 100;
    const prev = displayData[idx - 1]?.value || 1;
    return Math.round(((d.value || 0) / prev) * 100);
  });

  const handleClick = (entry) => {
    if (entry && entry.children && entry.children.length > 0) {
      setDrillLevel(entry.name);
      if (onDrillDown) onDrillDown(entry);
    }
  };

  const handleBack = () => {
    setDrillLevel(null);
  };

  if (loading) {
    return (
      <Card sx={{ borderRadius: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>{title}</Typography>
          <ChartSkeleton height={height} />
        </CardContent>
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card sx={{ borderRadius: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>{title}</Typography>
          <Box sx={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography color="text.secondary">No application data available</Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ borderRadius: 3 }}>
      <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {drillLevel && (
              <IconButton size="small" onClick={handleBack} sx={{ mr: 0.5 }}>
                <ArrowBackIcon fontSize="small" />
              </IconButton>
            )}
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              {drillLevel ? `${title} - ${drillLevel}` : title}
            </Typography>
          </Box>
          <MuiTooltip title="Shows the conversion funnel across application stages. Click a stage to drill down." arrow>
            <InfoOutlinedIcon sx={{ fontSize: 18, color: 'text.disabled' }} />
          </MuiTooltip>
        </Box>

        <Box sx={{ height }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={displayData}
              layout="vertical"
              margin={{ top: 5, right: 30, left: 90, bottom: 5 }}
              onClick={(e) => {
                if (e && e.activePayload) handleClick(e.activePayload[0]?.payload);
              }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke={isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.06)'}
                horizontal={false}
              />
              <XAxis
                type="number"
                tick={{ fontSize: 12, fill: theme.palette.text.secondary }}
                axisLine={false}
                tickLine={false}
                domain={[0, maxVal * 1.15]}
              />
              <YAxis
                dataKey="name"
                type="category"
                tick={{ fontSize: 12, fill: theme.palette.text.secondary }}
                axisLine={false}
                tickLine={false}
                width={80}
              />
              <Tooltip content={<FunnelTooltip conversionRates={conversionRates} />} cursor={{ fill: isDark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.03)' }} />
              <Bar
                dataKey="value"
                name="Applications"
                radius={[0, 8, 8, 0]}
                maxBarSize={40}
                cursor={hasDrillData ? 'pointer' : 'default'}
                onClick={(entry) => handleClick(entry)}
              >
                {displayData.map((entry, idx) => (
                  <Cell
                    key={idx}
                    fill={entry.color || funnelColors[idx % funnelColors.length]}
                    fillOpacity={1 - idx * 0.06}
                    stroke={entry.color || funnelColors[idx % funnelColors.length]}
                    strokeWidth={0}
                  />
                ))}
                <LabelList
                  dataKey="value"
                  position="right"
                  style={{ fontSize: 12, fontWeight: 600, fill: theme.palette.text.secondary }}
                />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Box>

        {showConversionLabels && conversionRates.length > 0 && (
          <Box
            sx={{
              display: 'flex', gap: 1, flexWrap: 'wrap', mt: 2, pt: 2,
              borderTop: '1px solid', borderColor: 'divider',
            }}
          >
            {conversionRates.map((rate, idx) => (
              idx > 0 && (
                <Box
                  key={idx}
                  sx={{
                    display: 'flex', alignItems: 'center', gap: 0.75,
                    px: 1.25, py: 0.5, borderRadius: 2,
                    bgcolor: rate >= 70 ? 'success.main' : rate >= 40 ? 'warning.main' : 'error.main',
                    color: '#fff',
                  }}
                >
                  <Typography variant="caption" sx={{ fontWeight: 600, fontSize: '0.7rem' }}>
                    {displayData[idx - 1]?.name} → {displayData[idx]?.name}
                  </Typography>
                  <Typography variant="caption" sx={{ fontWeight: 700, fontSize: '0.7rem' }}>
                    {rate}%
                  </Typography>
                </Box>
              )
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
