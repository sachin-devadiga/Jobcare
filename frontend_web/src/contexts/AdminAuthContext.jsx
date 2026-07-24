'use client';
import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import adminService from '@/services/adminService';
import { toast } from 'react-toastify';

export const AdminAuthContext = createContext(null);

export function AdminAuthProvider({ children }) {
  const [admin, setAdmin] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [otpSent, setOtpSent] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const storedAdmin = localStorage.getItem('admin');
    const token = Cookies.get('adminAccessToken') || localStorage.getItem('adminAccessToken');
    if (storedAdmin && token) {
      try {
        setAdmin(JSON.parse(storedAdmin));
      } catch {
        localStorage.removeItem('admin');
      }
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (credentials) => {
    setLoading(true);
    setError(null);
    try {
      const response = await adminService.login(credentials);
      const data = response.data;
      if (data.otpRequired) {
        setOtpSent(true);
        toast.info('OTP sent to your registered email');
        return { otpRequired: true, tempToken: data.tempToken };
      }
      const { accessToken, refreshToken, admin: adminData } = data;
      localStorage.setItem('adminAccessToken', accessToken);
      localStorage.setItem('adminRefreshToken', refreshToken);
      localStorage.setItem('admin', JSON.stringify(adminData));
      Cookies.set('adminAccessToken', accessToken, { expires: 7, secure: true, sameSite: 'strict' });
      Cookies.set('adminRefreshToken', refreshToken, { expires: 30, secure: true, sameSite: 'strict' });
      setAdmin(adminData);
      toast.success('Welcome to Admin Panel');
      router.push('/admin/dashboard');
      return adminData;
    } catch (err) {
      const message = err.message || 'Login failed';
      setError(message);
      toast.error(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [router]);

  const verifyOtp = useCallback(async (data) => {
    setLoading(true);
    setError(null);
    try {
      const response = await adminService.verifyOtp(data);
      const { accessToken, refreshToken, admin: adminData } = response.data;
      localStorage.setItem('adminAccessToken', accessToken);
      localStorage.setItem('adminRefreshToken', refreshToken);
      localStorage.setItem('admin', JSON.stringify(adminData));
      Cookies.set('adminAccessToken', accessToken, { expires: 7, secure: true, sameSite: 'strict' });
      Cookies.set('adminRefreshToken', refreshToken, { expires: 30, secure: true, sameSite: 'strict' });
      setAdmin(adminData);
      setOtpSent(false);
      toast.success('OTP verified successfully');
      router.push('/admin/dashboard');
      return adminData;
    } catch (err) {
      const message = err.message || 'OTP verification failed';
      setError(message);
      toast.error(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [router]);

  const logout = useCallback(() => {
    localStorage.removeItem('adminAccessToken');
    localStorage.removeItem('adminRefreshToken');
    localStorage.removeItem('admin');
    Cookies.remove('adminAccessToken');
    Cookies.remove('adminRefreshToken');
    setAdmin(null);
    setOtpSent(false);
    toast.info('Logged out');
    router.push('/admin/login');
  }, [router]);

  const clearError = useCallback(() => setError(null), []);

  const value = {
    admin,
    loading,
    error,
    otpSent,
    isAuthenticated: !!admin,
    login,
    verifyOtp,
    logout,
    clearError,
  };

  return <AdminAuthContext.Provider value={value}>{children}</AdminAuthContext.Provider>;
}

export const useAdminAuth = () => {
  const context = useContext(AdminAuthContext);
  if (!context) throw new Error('useAdminAuth must be used within AdminAuthProvider');
  return context;
};
