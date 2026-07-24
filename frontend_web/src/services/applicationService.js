import api from './api';

export const getApplications = async (params = {}) => {
  const { data } = await api.get('/employer/applications', { params });
  return data;
};

export const getApplicationById = async (id) => {
  const { data } = await api.get(`/employer/applications/${id}`);
  return data;
};

export const updateApplicationStatus = async (id, status, notes = '') => {
  const { data } = await api.put(`/employer/applications/${id}/status`, { status, notes });
  return data;
};

export const scheduleInterview = async (id, interviewData) => {
  const { data } = await api.post(`/employer/applications/${id}/schedule-interview`, interviewData);
  return data;
};

export const rescheduleInterview = async (id, interviewData) => {
  const { data } = await api.put(`/employer/applications/${id}/reschedule-interview`, interviewData);
  return data;
};

export const cancelInterview = async (id) => {
  const { data } = await api.put(`/employer/applications/${id}/cancel-interview`);
  return data;
};

export const addNote = async (id, note) => {
  const { data } = await api.post(`/employer/applications/${id}/notes`, { note });
  return data;
};

export const getNotes = async (id) => {
  const { data } = await api.get(`/employer/applications/${id}/notes`);
  return data;
};

export const rateApplicant = async (id, rating) => {
  const { data } = await api.put(`/employer/applications/${id}/rating`, { rating });
  return data;
};

export const getResume = async (id) => {
  const { data } = await api.get(`/employer/applications/${id}/resume`, {
    responseType: 'blob',
  });
  return data;
};

export const getVoiceResume = async (id) => {
  const { data } = await api.get(`/employer/applications/${id}/voice-resume`, {
    responseType: 'blob',
  });
  return data;
};

export const sendMessage = async (id, message) => {
  const { data } = await api.post(`/employer/applications/${id}/message`, { message });
  return data;
};

export default {
  getApplications,
  getApplicationById,
  updateApplicationStatus,
  scheduleInterview,
  rescheduleInterview,
  cancelInterview,
  addNote,
  getNotes,
  rateApplicant,
  getResume,
  getVoiceResume,
  sendMessage,
};
