'use client';
import { useState, useEffect, useCallback } from 'react';
import * as applicationService from '@/services/applicationService';
import { toast } from 'react-toastify';

export function useApplications(initialParams = {}) {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    total: 0,
    totalPages: 0,
  });
  const [params, setParams] = useState(initialParams);

  const fetchApplications = useCallback(async (queryParams = params) => {
    setLoading(true);
    setError(null);
    try {
      const response = await applicationService.getApplications(queryParams);
      setApplications(response.data || response.applications || []);
      setPagination({
        page: response.page || queryParams.page || 1,
        limit: response.limit || queryParams.limit || 10,
        total: response.total || 0,
        totalPages: response.totalPages || 0,
      });
    } catch (err) {
      setError(err.message || 'Failed to fetch applications');
      setApplications([]);
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    fetchApplications();
  }, [fetchApplications]);

  const updateStatus = useCallback(async (id, status, notes = '') => {
    try {
      const response = await applicationService.updateApplicationStatus(id, status, notes);
      setApplications((prev) =>
        prev.map((a) => (a._id === id || a.id === id ? (response.data || response) : a))
      );
      toast.success(`Application status updated to ${status.replace(/_/g, ' ')}`);
      return response.data || response;
    } catch (err) {
      toast.error(err.message || 'Failed to update status');
      throw err;
    }
  }, []);

  const scheduleInterview = useCallback(async (id, interviewData) => {
    try {
      const response = await applicationService.scheduleInterview(id, interviewData);
      setApplications((prev) =>
        prev.map((a) => (a._id === id || a.id === id ? (response.data || response) : a))
      );
      toast.success('Interview scheduled successfully!');
      return response.data || response;
    } catch (err) {
      toast.error(err.message || 'Failed to schedule interview');
      throw err;
    }
  }, []);

  const rescheduleInterview = useCallback(async (id, interviewData) => {
    try {
      const response = await applicationService.rescheduleInterview(id, interviewData);
      setApplications((prev) =>
        prev.map((a) => (a._id === id || a.id === id ? (response.data || response) : a))
      );
      toast.success('Interview rescheduled!');
      return response.data || response;
    } catch (err) {
      toast.error(err.message || 'Failed to reschedule interview');
      throw err;
    }
  }, []);

  const cancelInterview = useCallback(async (id) => {
    try {
      const response = await applicationService.cancelInterview(id);
      setApplications((prev) =>
        prev.map((a) => (a._id === id || a.id === id ? (response.data || response) : a))
      );
      toast.success('Interview cancelled!');
      return response.data || response;
    } catch (err) {
      toast.error(err.message || 'Failed to cancel interview');
      throw err;
    }
  }, []);

  const addNote = useCallback(async (id, note) => {
    try {
      const response = await applicationService.addNote(id, note);
      toast.success('Note added!');
      return response.data || response;
    } catch (err) {
      toast.error(err.message || 'Failed to add note');
      throw err;
    }
  }, []);

  const setPage = useCallback((page) => {
    setParams((prev) => ({ ...prev, page }));
  }, []);

  const setFilters = useCallback((filters) => {
    setParams((prev) => ({ ...prev, ...filters, page: 1 }));
  }, []);

  const refresh = useCallback(() => {
    fetchApplications(params);
  }, [fetchApplications, params]);

  return {
    applications,
    loading,
    error,
    pagination,
    params,
    updateStatus,
    scheduleInterview,
    rescheduleInterview,
    cancelInterview,
    addNote,
    setPage,
    setFilters,
    refresh,
  };
}
