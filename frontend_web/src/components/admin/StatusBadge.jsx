'use client';
import { Chip } from '@mui/material';

const darkStatusColors = {
  draft: { bg: 'rgba(107,114,128,0.2)', text: '#9CA3AF' },
  active: { bg: 'rgba(74,222,128,0.15)', text: '#4ADE80' },
  inactive: { bg: 'rgba(107,114,128,0.2)', text: '#9CA3AF' },
  banned: { bg: 'rgba(248,113,113,0.15)', text: '#F87171' },
  pending: { bg: 'rgba(251,191,36,0.15)', text: '#FBBF24' },
  verified: { bg: 'rgba(74,222,128,0.15)', text: '#4ADE80' },
  unverified: { bg: 'rgba(251,191,36,0.15)', text: '#FBBF24' },
  published: { bg: 'rgba(74,222,128,0.15)', text: '#4ADE80' },
  closed: { bg: 'rgba(251,191,36,0.15)', text: '#FBBF24' },
  filled: { bg: 'rgba(96,165,250,0.15)', text: '#60A5FA' },
  flagged: { bg: 'rgba(248,113,113,0.15)', text: '#F87171' },
  new: { bg: 'rgba(96,165,250,0.15)', text: '#60A5FA' },
  reviewing: { bg: 'rgba(251,191,36,0.15)', text: '#FBBF24' },
  shortlisted: { bg: 'rgba(74,222,128,0.15)', text: '#4ADE80' },
  interview_scheduled: { bg: 'rgba(74,222,128,0.15)', text: '#4ADE80' },
  interviewed: { bg: 'rgba(216,180,254,0.15)', text: '#D8B4FE' },
  offered: { bg: 'rgba(74,222,128,0.15)', text: '#4ADE80' },
  hired: { bg: 'rgba(96,165,250,0.15)', text: '#60A5FA' },
  rejected: { bg: 'rgba(248,113,113,0.15)', text: '#F87171' },
  withdrawn: { bg: 'rgba(107,114,128,0.2)', text: '#9CA3AF' },
  open: { bg: 'rgba(96,165,250,0.15)', text: '#60A5FA' },
  in_progress: { bg: 'rgba(251,191,36,0.15)', text: '#FBBF24' },
  resolved: { bg: 'rgba(74,222,128,0.15)', text: '#4ADE80' },
  low: { bg: 'rgba(74,222,128,0.15)', text: '#4ADE80' },
  medium: { bg: 'rgba(251,191,36,0.15)', text: '#FBBF24' },
  high: { bg: 'rgba(248,113,113,0.15)', text: '#F87171' },
  urgent: { bg: 'rgba(248,113,113,0.2)', text: '#F87171' },
  employee: { bg: 'rgba(96,165,250,0.15)', text: '#60A5FA' },
  employer: { bg: 'rgba(129,140,248,0.15)', text: '#818CF8' },
  admin: { bg: 'rgba(248,113,113,0.15)', text: '#F87171' },
  free: { bg: 'rgba(107,114,128,0.2)', text: '#9CA3AF' },
  basic: { bg: 'rgba(96,165,250,0.15)', text: '#60A5FA' },
  professional: { bg: 'rgba(129,140,248,0.15)', text: '#818CF8' },
  enterprise: { bg: 'rgba(251,191,36,0.15)', text: '#FBBF24' },
  subscribed: { bg: 'rgba(74,222,128,0.15)', text: '#4ADE80' },
  unsubscribed: { bg: 'rgba(107,114,128,0.2)', text: '#9CA3AF' },
};

export default function StatusBadge({ status, size = 'small', ...props }) {
  const config = darkStatusColors[status] || { bg: 'rgba(107,114,128,0.2)', text: '#9CA3AF' };
  const label = status ? status.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) : 'Unknown';

  return (
    <Chip
      label={label}
      size={size}
      sx={{
        backgroundColor: config.bg,
        color: config.text,
        fontWeight: 600, fontSize: size === 'small' ? '0.75rem' : '0.8125rem',
        borderRadius: '8px', border: 'none',
      }}
      {...props}
    />
  );
}
