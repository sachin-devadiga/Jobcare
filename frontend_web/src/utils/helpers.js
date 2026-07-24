import { clsx } from 'clsx';

export const cn = (...classes) => classes.filter(Boolean).join(' ');

export const debounce = (fn, delay = 300) => {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
};

export const throttle = (fn, limit = 300) => {
  let inThrottle;
  return (...args) => {
    if (!inThrottle) {
      fn(...args);
      inThrottle = true;
      setTimeout(() => { inThrottle = false; }, limit);
    }
  };
};

export const generateId = () => Math.random().toString(36).substr(2, 9);

export const getInitials = (name) => {
  if (!name) return '';
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
};

export const getAvatarColor = (name) => {
  if (!name) return '#6366F1';
  const colors = ['#6366F1', '#8B5CF6', '#EC4899', '#F43F5E', '#F97316', '#22C55E', '#14B8A6', '#06B6D4', '#3B82F6'];
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
};

export const getStatusColor = (status) => {
  const map = {
    draft: '#6B7280',
    published: '#059669',
    closed: '#D97706',
    filled: '#2563EB',
    archived: '#9CA3AF',
    new: '#2563EB',
    reviewing: '#D97706',
    shortlisted: '#059669',
    interview_scheduled: '#16A34A',
    interviewed: '#C026D3',
    offered: '#059669',
    hired: '#2563EB',
    rejected: '#DC2626',
    withdrawn: '#6B7280',
    active: '#059669',
    inactive: '#6B7280',
    pending: '#D97706',
    approved: '#059669',
    cancelled: '#DC2626',
  };
  return map[status] || '#6B7280';
};

export const getStatusLabel = (status) => {
  const map = {
    draft: 'Draft',
    published: 'Published',
    closed: 'Closed',
    filled: 'Filled',
    archived: 'Archived',
    new: 'New',
    reviewing: 'Reviewing',
    shortlisted: 'Shortlisted',
    interview_scheduled: 'Interview Scheduled',
    interviewed: 'Interviewed',
    offered: 'Offered',
    hired: 'Hired',
    rejected: 'Rejected',
    withdrawn: 'Withdrawn',
    active: 'Active',
    inactive: 'Inactive',
    pending: 'Pending',
    approved: 'Approved',
    cancelled: 'Cancelled',
  };
  return map[status] || status;
};

export const groupBy = (array, key) => {
  return array.reduce((result, item) => {
    const groupKey = typeof key === 'function' ? key(item) : item[key];
    if (!result[groupKey]) result[groupKey] = [];
    result[groupKey].push(item);
    return result;
  }, {});
};

export const sortBy = (array, key, order = 'asc') => {
  return [...array].sort((a, b) => {
    const aVal = typeof key === 'function' ? key(a) : a[key];
    const bVal = typeof key === 'function' ? key(b) : b[key];
    if (aVal < bVal) return order === 'asc' ? -1 : 1;
    if (aVal > bVal) return order === 'asc' ? 1 : -1;
    return 0;
  });
};

export const filterBySearch = (items, searchTerm, fields) => {
  if (!searchTerm) return items;
  const term = searchTerm.toLowerCase();
  return items.filter((item) =>
    fields.some((field) => {
      const value = typeof field === 'function' ? field(item) : item[field];
      return value && value.toString().toLowerCase().includes(term);
    })
  );
};

export const downloadFile = (url, filename) => {
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    return true;
  }
};

export const formatFileSize = (bytes) => {
  if (!bytes) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  return `${size.toFixed(1)} ${units[unitIndex]}`;
};
