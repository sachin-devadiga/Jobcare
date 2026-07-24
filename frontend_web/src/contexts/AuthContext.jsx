'use client';
import { createContext, useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import * as authService from '@/services/authService';
import { toast } from 'react-toastify';

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const router = useRouter();

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    const token = Cookies.get('accessToken') || localStorage.getItem('accessToken');
    if (storedUser && token) {
      try {
        setUser(JSON.parse(storedUser));
      } catch {
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (credentials) => {
    setLoading(true);
    setError(null);
    try {
      const response = await authService.login(credentials);
      const { accessToken, refreshToken, user: userData } = response;
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
      localStorage.setItem('user', JSON.stringify(userData));
      Cookies.set('accessToken', accessToken, { expires: 7, secure: true, sameSite: 'strict' });
      Cookies.set('refreshToken', refreshToken, { expires: 30, secure: true, sameSite: 'strict' });
      setUser(userData);
      toast.success('Welcome back!');
      router.push('/employer/dashboard');
      return userData;
    } catch (err) {
      const message = err.message || 'Login failed';
      setError(message);
      toast.error(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [router]);

  const register = useCallback(async (userData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await authService.register(userData);
      const { accessToken, refreshToken, user: newUser } = response;
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
      localStorage.setItem('user', JSON.stringify(newUser));
      Cookies.set('accessToken', accessToken, { expires: 7, secure: true, sameSite: 'strict' });
      Cookies.set('refreshToken', refreshToken, { expires: 30, secure: true, sameSite: 'strict' });
      setUser(newUser);
      toast.success('Account created successfully!');
      router.push('/employer/dashboard');
      return newUser;
    } catch (err) {
      const message = err.message || 'Registration failed';
      setError(message);
      toast.error(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [router]);

  const logout = useCallback(() => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    Cookies.remove('accessToken');
    Cookies.remove('refreshToken');
    setUser(null);
    toast.info('Logged out');
    router.push('/auth/login');
  }, [router]);

  const forgotPassword = useCallback(async (email) => {
    setLoading(true);
    try {
      const response = await authService.forgotPassword(email);
      toast.success('Password reset email sent!');
      return response;
    } catch (err) {
      toast.error(err.message || 'Failed to send reset email');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const resetPassword = useCallback(async (token, password) => {
    setLoading(true);
    try {
      const response = await authService.resetPassword(token, password);
      toast.success('Password reset successful!');
      return response;
    } catch (err) {
      toast.error(err.message || 'Failed to reset password');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateUser = useCallback((userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  }, []);

  const clearError = useCallback(() => setError(null), []);

  const value = {
    user,
    loading,
    error,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    forgotPassword,
    resetPassword,
    updateUser,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
