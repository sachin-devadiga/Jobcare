import api from './api';

export const login = async (credentials) => {
  const { data } = await api.post('/auth/login', credentials);
  return data;
};

export const register = async (userData) => {
  const { data } = await api.post('/auth/register', userData);
  return data;
};

export const refreshToken = async (refreshToken) => {
  const { data } = await api.post('/auth/refresh-token', { refreshToken });
  return data;
};

export const forgotPassword = async (email) => {
  const { data } = await api.post('/auth/forgot-password', { email });
  return data;
};

export const resetPassword = async (token, password) => {
  const { data } = await api.post('/auth/reset-password', { token, password });
  return data;
};

export const verifyEmail = async (token) => {
  const { data } = await api.post('/auth/verify-email', { token });
  return data;
};

export const getProfile = async () => {
  const { data } = await api.get('/auth/profile');
  return data;
};

export const updateProfile = async (profileData) => {
  const { data } = await api.put('/auth/profile', profileData);
  return data;
};

export const changePassword = async (currentPassword, newPassword) => {
  const { data } = await api.put('/auth/change-password', { currentPassword, newPassword });
  return data;
};

export const loginWithGoogle = async (idToken) => {
  const { data } = await api.post('/auth/google', { idToken });
  return data;
};

export const loginWithLinkedIn = async (code) => {
  const { data } = await api.post('/auth/linkedin', { code });
  return data;
};

export default {
  login,
  register,
  refreshToken,
  forgotPassword,
  resetPassword,
  verifyEmail,
  getProfile,
  updateProfile,
  changePassword,
  loginWithGoogle,
  loginWithLinkedIn,
};
