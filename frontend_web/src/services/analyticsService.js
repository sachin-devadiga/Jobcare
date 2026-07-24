import api from './api';

export const getDashboardStats = async (dateRange = '30d') => {
  const { data } = await api.get('/employer/analytics/dashboard', { params: { dateRange } });
  return data;
};

export const getJobAnalytics = async (jobId = null, params = {}) => {
  const url = jobId ? `/employer/analytics/jobs/${jobId}/performance` : '/employer/analytics/jobs';
  const { data } = await api.get(url, { params });
  return data;
};

export const getApplicationAnalytics = async (params = {}) => {
  const { data } = await api.get('/employer/analytics/applications', { params });
  return data;
};

export const getRevenueAnalytics = async (params = {}) => {
  const { data } = await api.get('/employer/analytics/revenue', { params });
  return data;
};

export const getJobPerformance = async (jobId, params = {}) => {
  const { data } = await api.get(`/employer/analytics/jobs/${jobId}/performance`, { params });
  return data;
};

export const getApplicationTrends = async (params = {}) => {
  const { data } = await api.get('/employer/analytics/application-trends', { params });
  return data;
};

export const getSourceAnalytics = async (params = {}) => {
  const { data } = await api.get('/employer/analytics/sources', { params });
  return data;
};

export const getDemographics = async (params = {}) => {
  const { data } = await api.get('/employer/analytics/demographics', { params });
  return data;
};

export const getSkillAnalytics = async (params = {}) => {
  const { data } = await api.get('/employer/analytics/skills', { params });
  return data;
};

export const getLocationAnalytics = async (params = {}) => {
  const { data } = await api.get('/employer/analytics/locations', { params });
  return data;
};

export const getTrendData = async (metric = 'applications', period = '30d') => {
  const { data } = await api.get('/employer/analytics/trends', { params: { metric, period } });
  return data;
};

export const exportAnalytics = async (format = 'csv', dateRange = '30d') => {
  const { data } = await api.get('/employer/analytics/export', {
    params: { format, dateRange },
    responseType: format === 'pdf' ? 'blob' : 'json',
  });
  return data;
};

export default {
  getDashboardStats,
  getJobAnalytics,
  getApplicationAnalytics,
  getRevenueAnalytics,
  getJobPerformance,
  getApplicationTrends,
  getSourceAnalytics,
  getDemographics,
  getSkillAnalytics,
  getLocationAnalytics,
  getTrendData,
  exportAnalytics,
};
