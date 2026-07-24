import api from './api';

export const getCompanyProfile = async () => {
  const { data } = await api.get('/employer/company');
  return data;
};

export const updateCompanyProfile = async (profileData) => {
  const { data } = await api.put('/employer/company', profileData);
  return data;
};

export const uploadCompanyLogo = async (file) => {
  const formData = new FormData();
  formData.append('logo', file);
  const { data } = await api.post('/employer/company/logo', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
};

export const uploadCompanyBanner = async (file) => {
  const formData = new FormData();
  formData.append('banner', file);
  const { data } = await api.post('/employer/company/banner', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
};

export const getCompanyVerificationStatus = async () => {
  const { data } = await api.get('/employer/company/verification');
  return data;
};

export const submitVerificationDocuments = async (documents) => {
  const formData = new FormData();
  documents.forEach((doc) => {
    formData.append('documents', doc);
  });
  const { data } = await api.post('/employer/company/verify', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
};

export const getTeamMembers = async () => {
  const { data } = await api.get('/employer/company/team');
  return data;
};

export const addTeamMember = async (memberData) => {
  const { data } = await api.post('/employer/company/team', memberData);
  return data;
};

export const removeTeamMember = async (memberId) => {
  const { data } = await api.delete(`/employer/company/team/${memberId}`);
  return data;
};

export const updateTeamMemberRole = async (memberId, role) => {
  const { data } = await api.put(`/employer/company/team/${memberId}`, { role });
  return data;
};

export default {
  getCompanyProfile,
  updateCompanyProfile,
  uploadCompanyLogo,
  uploadCompanyBanner,
  getCompanyVerificationStatus,
  submitVerificationDocuments,
  getTeamMembers,
  addTeamMember,
  removeTeamMember,
  updateTeamMemberRole,
};
