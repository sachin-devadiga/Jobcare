import { useState, useEffect, useCallback } from 'react';
import { Box, Grid, Typography, Card, CardContent, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Chip, Button } from '@mui/material';
import DashboardLayout from '@/components/layout/DashboardLayout';
import SubscriptionCard from '@/components/employer/SubscriptionCard';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ErrorState from '@/components/common/ErrorState';
import * as paymentService from '@/services/paymentService';
import { formatCurrency, formatDate } from '@/utils/formatters';

export default function SubscriptionsPage() {
  const [plans, setPlans] = useState([]);
  const [currentSub, setCurrentSub] = useState(null);
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [plansRes, subRes, invRes] = await Promise.all([
        paymentService.getPlans(),
        paymentService.getCurrentSubscription(),
        paymentService.getInvoices({ limit: 10 }),
      ]);
      setPlans(plansRes.data || plansRes || []);
      setCurrentSub(subRes.data || subRes);
      setInvoices(invRes.data || invRes.invoices || []);
    } catch (err) {
      setError(err.message || 'Failed to load subscription data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleSelectPlan = async (plan) => {
    try {
      if (plan.price === 0) {
        await paymentService.subscribe(plan._id || plan.id, null);
        await fetchData();
      } else {
        /* redirect to checkout */
        const session = await paymentService.createCheckoutSession(plan._id || plan.id, 'monthly');
        if (session.url) window.location.href = session.url;
      }
    } catch {
      /* handled by service */
    }
  };

  if (loading) return <DashboardLayout><LoadingSpinner message="Loading plans..." /></DashboardLayout>;
  if (error) return <DashboardLayout><ErrorState message={error} onRetry={fetchData} /></DashboardLayout>;

  return (
    <DashboardLayout>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>Subscriptions</Typography>
        <Typography variant="body2" color="text.secondary">Choose the best plan for your hiring needs</Typography>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {plans.map((plan) => (
          <Grid item xs={12} sm={6} lg={3} key={plan._id || plan.id}>
            <SubscriptionCard
              plan={plan}
              current={currentSub?.plan?._id === plan._id || currentSub?.plan?.id === plan.id}
              onSelect={handleSelectPlan}
            />
          </Grid>
        ))}
      </Grid>

      {currentSub && (
        <Card sx={{ borderRadius: 3, mb: 4 }}>
          <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
                  Current Plan: {currentSub.plan?.name || 'Free'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {currentSub.status === 'active' ? 'Active' : currentSub.status} &middot; Renews {formatDate(currentSub.renewalDate || currentSub.endDate)}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Chip label={currentSub.status} color={currentSub.status === 'active' ? 'success' : 'default'} size="small" />
                {currentSub.status === 'active' && (
                  <Button variant="outlined" size="small" color="error">Cancel</Button>
                )}
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

      <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>Billing History</Typography>
      <Paper sx={{ borderRadius: 3, overflow: 'hidden' }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Invoice</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Amount</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Download</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {invoices.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">No invoices yet</TableCell>
                </TableRow>
              ) : (
                invoices.map((inv) => (
                  <TableRow key={inv._id || inv.id}>
                    <TableCell>{inv.invoiceNumber || `#${(inv._id || inv.id).slice(-6)}`}</TableCell>
                    <TableCell>{formatDate(inv.createdAt)}</TableCell>
                    <TableCell>{formatCurrency(inv.amount, inv.currency)}</TableCell>
                    <TableCell>
                      <Chip label={inv.status} size="small" color={inv.status === 'paid' ? 'success' : 'default'} />
                    </TableCell>
                    <TableCell>
                      <Button size="small" variant="text">PDF</Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </DashboardLayout>
  );
}
