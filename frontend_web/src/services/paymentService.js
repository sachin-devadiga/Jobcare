import api from './api';

export const getPlans = async () => {
  const { data } = await api.get('/subscriptions/plans');
  return data;
};

export const getCurrentSubscription = async () => {
  const { data } = await api.get('/employer/subscription');
  return data;
};

export const subscribe = async (planId, paymentMethodId) => {
  const { data } = await api.post('/employer/subscribe', { planId, paymentMethodId });
  return data;
};

export const cancelSubscription = async () => {
  const { data } = await api.post('/employer/subscription/cancel');
  return data;
};

export const changePlan = async (planId) => {
  const { data } = await api.put('/employer/subscription/plan', { planId });
  return data;
};

export const getPaymentMethods = async () => {
  const { data } = await api.get('/employer/payment-methods');
  return data;
};

export const addPaymentMethod = async (paymentMethodId) => {
  const { data } = await api.post('/employer/payment-methods', { paymentMethodId });
  return data;
};

export const removePaymentMethod = async (paymentMethodId) => {
  const { data } = await api.delete(`/employer/payment-methods/${paymentMethodId}`);
  return data;
};

export const getInvoices = async (params = {}) => {
  const { data } = await api.get('/employer/invoices', { params });
  return data;
};

export const getInvoice = async (invoiceId) => {
  const { data } = await api.get(`/employer/invoices/${invoiceId}`);
  return data;
};

export const downloadInvoice = async (invoiceId) => {
  const { data } = await api.get(`/employer/invoices/${invoiceId}/download`, {
    responseType: 'blob',
  });
  return data;
};

export const createCheckoutSession = async (planId, interval) => {
  const { data } = await api.post('/employer/create-checkout-session', { planId, interval });
  return data;
};

export default {
  getPlans,
  getCurrentSubscription,
  subscribe,
  cancelSubscription,
  changePlan,
  getPaymentMethods,
  addPaymentMethod,
  removePaymentMethod,
  getInvoices,
  getInvoice,
  downloadInvoice,
  createCheckoutSession,
};
