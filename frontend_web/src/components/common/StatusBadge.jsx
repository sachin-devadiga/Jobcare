'use client';
import { Chip } from '@mui/material';
import { getStatusColor, getStatusLabel } from '@/utils/helpers';

export default function StatusBadge({ status, size = 'small', ...props }) {
  const color = getStatusColor(status);
  const label = getStatusLabel(status);

  return (
    <Chip
      label={label}
      size={size}
      sx={{
        backgroundColor: `${color}18`,
        color: color,
        fontWeight: 600,
        fontSize: size === 'small' ? '0.75rem' : '0.8125rem',
        borderRadius: '8px',
        border: `1px solid ${color}30`,
        '&:hover': { backgroundColor: `${color}25` },
      }}
      {...props}
    />
  );
}
