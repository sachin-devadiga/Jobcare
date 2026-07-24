'use client';
import { Box, Typography, Button } from '@mui/material';
import InboxOutlinedIcon from '@mui/icons-material/InboxOutlined';

export default function EmptyState({
  icon = <InboxOutlinedIcon sx={{ fontSize: 64 }} />,
  title = 'No data found',
  description = 'There are no items to display at the moment.',
  action,
  actionLabel = 'Create New',
  onAction,
}) {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        py: 8,
        px: 3,
        textAlign: 'center',
      }}
    >
      <Box sx={{ color: 'text.disabled', mb: 2, opacity: 0.6 }}>
        {icon}
      </Box>
      <Typography variant="h6" color="text.primary" sx={{ mb: 1, fontWeight: 600 }}>
        {title}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3, maxWidth: 400 }}>
        {description}
      </Typography>
      {action && onAction && (
        <Button variant="contained" onClick={onAction} sx={{ borderRadius: 3 }}>
          {actionLabel}
        </Button>
      )}
    </Box>
  );
}
