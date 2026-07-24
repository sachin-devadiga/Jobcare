'use client';
import { useState, useEffect, useCallback } from 'react';
import * as analyticsService from '@/services/analyticsService';

export function useAnalytics() {
  const [dashboardStats, setDashboardStats] = useState(null);
  const [jobAnalytics, setJobAnalytics] = useState(null);
  const [applicationAnalytics, setApplicationAnalytics] = useState(null);
  const [revenueAnalytics, setRevenueAnalytics] = useState(null);
  const [applicationTrends, setApplicationTrends] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardStats = useCallback(async () => {
    try {
      const response = await analyticsService.getDashboardStats();
      setDashboardStats(response.data || response);
    } catch (err) {
      setError(err.message || 'Failed to fetch dashboard stats');
    }
  }, []);

  const fetchJobAnalytics = useCallback(async (params = {}) => {
    try {
      const response = await analyticsService.getJobAnalytics(params);
      setJobAnalytics(response.data || response);
    } catch (err) {
      setError(err.message || 'Failed to fetch job analytics');
    }
  }, []);

  const fetchApplicationAnalytics = useCallback(async (params = {}) => {
    try {
      const response = await analyticsService.getApplicationAnalytics(params);
      setApplicationAnalytics(response.data || response);
    } catch (err) {
      setError(err.message || 'Failed to fetch application analytics');
    }
  }, []);

  const fetchRevenueAnalytics = useCallback(async (params = {}) => {
    try {
      const response = await analyticsService.getRevenueAnalytics(params);
      setRevenueAnalytics(response.data || response);
    } catch (err) {
      setError(err.message || 'Failed to fetch revenue analytics');
    }
  }, []);

  const fetchApplicationTrends = useCallback(async (params = {}) => {
    try {
      const response = await analyticsService.getApplicationTrends(params);
      setApplicationTrends(response.data || response);
    } catch (err) {
      setError(err.message || 'Failed to fetch application trends');
    }
  }, []);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    await Promise.allSettled([
      fetchDashboardStats(),
      fetchJobAnalytics(),
      fetchApplicationAnalytics(),
      fetchRevenueAnalytics(),
      fetchApplicationTrends(),
    ]);
    setLoading(false);
  }, [fetchDashboardStats, fetchJobAnalytics, fetchApplicationAnalytics, fetchRevenueAnalytics, fetchApplicationTrends]);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  return {
    dashboardStats,
    jobAnalytics,
    applicationAnalytics,
    revenueAnalytics,
    applicationTrends,
    loading,
    error,
    fetchDashboardStats,
    fetchJobAnalytics,
    fetchApplicationAnalytics,
    fetchRevenueAnalytics,
    fetchApplicationTrends,
    refresh: fetchAll,
  };
}
