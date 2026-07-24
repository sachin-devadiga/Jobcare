'use client';
import { useState, useEffect, useCallback } from 'react';
import * as jobService from '@/services/jobService';
import { toast } from 'react-toastify';

export function useJobs(initialParams = {}) {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    total: 0,
    totalPages: 0,
  });
  const [params, setParams] = useState(initialParams);

  const fetchJobs = useCallback(async (queryParams = params) => {
    setLoading(true);
    setError(null);
    try {
      const response = await jobService.getJobs(queryParams);
      setJobs(response.data || response.jobs || []);
      setPagination({
        page: response.page || queryParams.page || 1,
        limit: response.limit || queryParams.limit || 10,
        total: response.total || 0,
        totalPages: response.totalPages || 0,
      });
    } catch (err) {
      setError(err.message || 'Failed to fetch jobs');
      setJobs([]);
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  const createJob = useCallback(async (jobData) => {
    try {
      const response = await jobService.createJob(jobData);
      setJobs((prev) => [response.data || response, ...prev]);
      toast.success('Job created successfully!');
      return response.data || response;
    } catch (err) {
      toast.error(err.message || 'Failed to create job');
      throw err;
    }
  }, []);

  const updateJob = useCallback(async (id, jobData) => {
    try {
      const response = await jobService.updateJob(id, jobData);
      setJobs((prev) => prev.map((j) => (j._id === id || j.id === id ? (response.data || response) : j)));
      toast.success('Job updated successfully!');
      return response.data || response;
    } catch (err) {
      toast.error(err.message || 'Failed to update job');
      throw err;
    }
  }, []);

  const deleteJob = useCallback(async (id) => {
    try {
      await jobService.deleteJob(id);
      setJobs((prev) => prev.filter((j) => j._id !== id && j.id !== id));
      toast.success('Job deleted successfully!');
    } catch (err) {
      toast.error(err.message || 'Failed to delete job');
      throw err;
    }
  }, []);

  const publishJob = useCallback(async (id) => {
    try {
      const response = await jobService.publishJob(id);
      setJobs((prev) => prev.map((j) => (j._id === id || j.id === id ? (response.data || response) : j)));
      toast.success('Job published successfully!');
      return response.data || response;
    } catch (err) {
      toast.error(err.message || 'Failed to publish job');
      throw err;
    }
  }, []);

  const closeJob = useCallback(async (id) => {
    try {
      const response = await jobService.closeJob(id);
      setJobs((prev) => prev.map((j) => (j._id === id || j.id === id ? (response.data || response) : j)));
      toast.success('Job closed successfully!');
      return response.data || response;
    } catch (err) {
      toast.error(err.message || 'Failed to close job');
      throw err;
    }
  }, []);

  const archiveJob = useCallback(async (id) => {
    try {
      const response = await jobService.archiveJob(id);
      setJobs((prev) => prev.map((j) => (j._id === id || j.id === id ? (response.data || response) : j)));
      toast.success('Job archived successfully!');
      return response.data || response;
    } catch (err) {
      toast.error(err.message || 'Failed to archive job');
      throw err;
    }
  }, []);

  const duplicateJob = useCallback(async (id) => {
    try {
      const response = await jobService.duplicateJob(id);
      setJobs((prev) => [response.data || response, ...prev]);
      toast.success('Job duplicated successfully!');
      return response.data || response;
    } catch (err) {
      toast.error(err.message || 'Failed to duplicate job');
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
    fetchJobs(params);
  }, [fetchJobs, params]);

  return {
    jobs,
    loading,
    error,
    pagination,
    params,
    createJob,
    updateJob,
    deleteJob,
    publishJob,
    closeJob,
    archiveJob,
    duplicateJob,
    setPage,
    setFilters,
    refresh,
  };
}
