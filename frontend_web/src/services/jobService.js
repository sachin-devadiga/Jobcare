import api from './api';

export const getJobs = async (params = {}) => {
  const { data } = await api.get('/employer/jobs', { params });
  return data;
};

export const getJobById = async (id) => {
  const { data } = await api.get(`/employer/jobs/${id}`);
  return data;
};

export const createJob = async (jobData) => {
  const { data } = await api.post('/employer/jobs', jobData);
  return data;
};

export const updateJob = async (id, jobData) => {
  const { data } = await api.put(`/employer/jobs/${id}`, jobData);
  return data;
};

export const deleteJob = async (id) => {
  const { data } = await api.delete(`/employer/jobs/${id}`);
  return data;
};

export const publishJob = async (id) => {
  const { data } = await api.put(`/employer/jobs/${id}/publish`);
  return data;
};

export const closeJob = async (id) => {
  const { data } = await api.put(`/employer/jobs/${id}/close`);
  return data;
};

export const archiveJob = async (id) => {
  const { data } = await api.put(`/employer/jobs/${id}/archive`);
  return data;
};

export const getJobStats = async (id) => {
  const { data } = await api.get(`/employer/jobs/${id}/stats`);
  return data;
};

export const getJobApplications = async (id, params = {}) => {
  const { data } = await api.get(`/employer/jobs/${id}/applications`, { params });
  return data;
};

export const duplicateJob = async (id) => {
  const { data } = await api.post(`/employer/jobs/${id}/duplicate`);
  return data;
};

export default {
  getJobs,
  getJobById,
  createJob,
  updateJob,
  deleteJob,
  publishJob,
  closeJob,
  archiveJob,
  getJobStats,
  getJobApplications,
  duplicateJob,
};
