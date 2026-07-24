'use client';
import { Box, Card, CardContent, Typography, Button, List, ListItem, ListItemIcon, ListItemText, Chip } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import { formatCurrency } from '@/utils/formatters';

export default function SubscriptionCard({
  plan,
  current = false,
  onSelect,
  loading = false,
}) {
  return (
    <Card
      sx={{
        borderRadius: 4,
        position: 'relative',
        overflow: 'visible',
        transition: 'all 0.3s',
        border: current ? '2px solid' : '1px solid',
        borderColor: current ? 'primary.main' : 'divider',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 20px 60px rgba(99,102,241,0.15)',
        },
      }}
    >
      {current && (
        <Chip
          label="Current Plan"
          color="primary"
          size="small"
          sx={{
            position: 'absolute',
            top: -12,
            right: 16,
            fontWeight: 600,
            fontSize: '0.7rem',
            px: 1,
          }}
        />
      )}
      {plan.popular && !current && (
        <Chip
          label="Popular"
          color="warning"
          size="small"
          sx={{
            position: 'absolute',
            top: -12,
            right: 16,
            fontWeight: 600,
            fontSize: '0.7rem',
            px: 1,
          }}
        />
      )}
      <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
        <Box sx={{ textAlign: 'center', mb: 3 }}>
          <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>{plan.name}</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>{plan.description}</Typography>
          <Box sx={{ display: 'flex', alignItems: 'baseline', justifyContent: 'center', gap: 0.5 }}>
            <Typography variant="h3" sx={{ fontWeight: 800, color: 'primary.main' }}>
              {plan.price === 0 ? 'Free' : formatCurrency(plan.price, 'USD')}
            </Typography>
            {plan.price > 0 && (
              <Typography variant="body2" color="text.secondary">/{plan.interval || 'month'}</Typography>
            )}
          </Box>
        </Box>

        <List dense sx={{ mb: 3 }}>
          {(plan.features || []).map((feature, idx) => (
            <ListItem key={idx} sx={{ px: 0, py: 0.5 }}>
              <ListItemIcon sx={{ minWidth: 32 }}>
                {feature.included ? (
                  <CheckCircleIcon sx={{ fontSize: 18, color: 'success.main' }} />
                ) : (
                  <CancelIcon sx={{ fontSize: 18, color: 'text.disabled' }} />
                )}
              </ListItemIcon>
              <ListItemText
                primary={feature.name}
                primaryTypographyProps={{
                  variant: 'body2',
                  color: feature.included ? 'text.primary' : 'text.disabled',
                }}
              />
            </ListItem>
          ))}
        </List>

        <Button
          variant={current ? 'outlined' : 'contained'}
          fullWidth
          size="large"
          onClick={() => onSelect(plan)}
          disabled={loading || current}
          sx={{ borderRadius: 3, py: 1.5 }}
        >
          {current ? 'Current Plan' : loading ? 'Processing...' : plan.price === 0 ? 'Get Started' : 'Subscribe'}
        </Button>
      </CardContent>
    </Card>
  );
}
