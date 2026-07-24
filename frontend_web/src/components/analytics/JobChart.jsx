'use client';
import { useState, useRef, useCallback } from 'react';
import {
  Box, Card, CardContent, Typography, useTheme, IconButton, Menu, MenuItem,
  Button, Stack, Skeleton
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, AreaChart, Area, Legend, ReferenceLine,
} from 'recharts';
import { CHART_COLORS } from '@/utils/constants';
import { format } from 'date-fns';

const CHART_TYPES = ['bar', 'line', 'area'];

function CustomTooltip({ active, payload, label, dateFormat }) {
  if (active && payload && payload.length) {
    return (
      <Box
        sx={{
          bgcolor: 'background.paper',
          p: 1.5,
          borderRadius: 2,
          boxShadow: 3,
          border: '1px solid',
          borderColor: 'divider',
          minWidth: 140,
        }}
      >
        <Typography variant="caption" sx={{ fontWeight: 600, mb: 0.5, display: 'block', color: 'text.primary' }}>
          {dateFormat && label ? (() => { try { return format(new Date(label), dateFormat); } catch { return label; } })() : label}
        </Typography>
        {payload.map((entry, idx) => (
          <Typography
            key={idx}
            variant="caption"
            sx={{ color: entry.color, display: 'flex', alignItems: 'center', gap: 0.5, py: 0.25 }}
          >
            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: entry.color, flexShrink: 0 }} />
            {entry.name}: <strong>{typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value}</strong>
          </Typography>
        ))}
      </Box>
    );
  }
  return null;
}

function ChartSkeleton({ height }) {
  return (
    <Box sx={{ height, display: 'flex', flexDirection: 'column', gap: 1, p: 1 }}>
      <Skeleton variant="rounded" width="100%" height={20} />
      <Skeleton variant="rounded" width="100%" height={height - 60} />
      <Skeleton variant="rounded" width="60%" height={16} />
    </Box>
  );
}

export default function JobChart({
  data,
  title,
  type = 'bar',
  height = 300,
  dataKeys,
  showDownload = true,
  showTypeToggle = false,
  dateFormat,
  loading = false,
  emptyTitle = 'No data available',
  emptyDescription = 'There is no data to display for this period.',
  yAxisLabel,
  gradientIds,
}) {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const chartRef = useRef(null);
  const [chartType, setChartType] = useState(type);
  const [menuAnchor, setMenuAnchor] = useState(null);

  const effectiveKeys = dataKeys || [{ key: 'value', color: CHART_COLORS[0], name: 'Value' }];

  const handleDownloadPNG = useCallback(() => {
    const container = chartRef.current;
    if (!container) return;
    const svg = container.querySelector('svg');
    if (!svg) return;
    const svgData = new XMLSerializer().serializeToString(svg);
    const canvas = document.createElement('canvas');
    const rect = svg.getBoundingClientRect();
    canvas.width = rect.width * 2;
    canvas.height = rect.height * 2;
    const ctx = canvas.getContext('2d');
    ctx.scale(2, 2);
    const img = new Image();
    const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    img.onload = () => {
      ctx.fillStyle = theme.palette.background.paper;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, rect.width, rect.height);
      URL.revokeObjectURL(url);
      const link = document.createElement('a');
      link.download = `${(title || 'chart').replace(/\s+/g, '_').toLowerCase()}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
    };
    img.src = url;
  }, [title, theme]);

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
          <Box sx={{ height, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
            <Typography color="text.secondary" variant="body2">{emptyTitle}</Typography>
            <Typography color="text.disabled" variant="caption">{emptyDescription}</Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  const gridColor = isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.06)';
  const axisStyle = { fontSize: 12, fill: theme.palette.text.secondary };

  const renderChart = () => {
    switch (chartType) {
      case 'area':
        return (
          <AreaChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
            <XAxis dataKey="name" tick={axisStyle} axisLine={false} tickLine={false} />
            <YAxis tick={axisStyle} axisLine={false} tickLine={false} label={yAxisLabel ? { value: yAxisLabel, angle: -90, style: axisStyle } : undefined} />
            <Tooltip content={<CustomTooltip dateFormat={dateFormat} />} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            {effectiveKeys.map((dk, idx) => {
              const gradId = gradientIds?.[idx] || `areaGrad-${idx}`;
              return (
                <Area
                  key={dk.key}
                  type="monotone"
                  dataKey={dk.key}
                  name={dk.name || dk.key}
                  stroke={dk.color || CHART_COLORS[idx % CHART_COLORS.length]}
                  strokeWidth={2}
                  fill={`url(#${gradId})`}
                  dot={false}
                  activeDot={{ r: 5, strokeWidth: 0 }}
                />
              );
            })}
          </AreaChart>
        );
      case 'line':
        return (
          <LineChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
            <XAxis dataKey="name" tick={axisStyle} axisLine={false} tickLine={false} />
            <YAxis tick={axisStyle} axisLine={false} tickLine={false} label={yAxisLabel ? { value: yAxisLabel, angle: -90, style: axisStyle } : undefined} />
            <Tooltip content={<CustomTooltip dateFormat={dateFormat} />} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            {effectiveKeys.map((dk, idx) => (
              <Line
                key={dk.key}
                type="monotone"
                dataKey={dk.key}
                name={dk.name || dk.key}
                stroke={dk.color || CHART_COLORS[idx % CHART_COLORS.length]}
                strokeWidth={2}
                dot={{ r: 3, fill: dk.color || CHART_COLORS[idx % CHART_COLORS.length], strokeWidth: 0 }}
                activeDot={{ r: 6, strokeWidth: 0 }}
              />
            ))}
          </LineChart>
        );
      default:
        return (
          <BarChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
            <XAxis dataKey="name" tick={axisStyle} axisLine={false} tickLine={false} />
            <YAxis tick={axisStyle} axisLine={false} tickLine={false} label={yAxisLabel ? { value: yAxisLabel, angle: -90, style: axisStyle } : undefined} />
            <Tooltip content={<CustomTooltip dateFormat={dateFormat} />} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            {effectiveKeys.map((dk, idx) => (
              <Bar
                key={dk.key}
                dataKey={dk.key}
                name={dk.name || dk.key}
                fill={dk.color || CHART_COLORS[idx % CHART_COLORS.length]}
                radius={[4, 4, 0, 0]}
                maxBarSize={40}
              />
            ))}
          </BarChart>
        );
    }
  };

  return (
    <Card sx={{ borderRadius: 3 }}>
      <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>{title}</Typography>
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            {showTypeToggle && (
              <Stack direction="row" spacing={0.5}>
                {CHART_TYPES.map((t) => (
                  <Button
                    key={t}
                    size="small"
                    variant={chartType === t ? 'contained' : 'text'}
                    onClick={() => setChartType(t)}
                    sx={{ minWidth: 40, px: 1, fontSize: '0.7rem', textTransform: 'capitalize' }}
                  >
                    {t}
                  </Button>
                ))}
              </Stack>
            )}
            {showDownload && (
              <>
                <IconButton size="small" onClick={(e) => setMenuAnchor(e.currentTarget)}>
                  <MoreVertIcon fontSize="small" />
                </IconButton>
                <Menu anchorEl={menuAnchor} open={Boolean(menuAnchor)} onClose={() => setMenuAnchor(null)}>
                  <MenuItem onClick={() => { setMenuAnchor(null); handleDownloadPNG(); }} dense>
                    <DownloadIcon sx={{ mr: 1, fontSize: 18 }} /> Download as PNG
                  </MenuItem>
                </Menu>
              </>
            )}
          </Box>
        </Box>
        <Box sx={{ height, width: '100%' }} ref={chartRef}>
          <svg width={0} height={0}>
            <defs>
              {effectiveKeys.map((dk, idx) => (
                <linearGradient key={idx} id={gradientIds?.[idx] || `areaGrad-${idx}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={dk.color || CHART_COLORS[idx % CHART_COLORS.length]} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={dk.color || CHART_COLORS[idx % CHART_COLORS.length]} stopOpacity={0} />
                </linearGradient>
              ))}
            </defs>
          </svg>
          <ResponsiveContainer width="100%" height="100%">
            {renderChart()}
          </ResponsiveContainer>
        </Box>
      </CardContent>
    </Card>
  );
}
