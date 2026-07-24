import { format, formatDistanceToNow, parseISO } from 'date-fns';

export const formatCurrency = (amount, currency = 'USD') => {
  if (amount == null) return 'Not specified';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

export const formatSalaryRange = (min, max, currency = 'USD') => {
  if (!min && !max) return 'Not specified';
  if (min && !max) return `${formatCurrency(min, currency)}+`;
  if (!min && max) return `Up to ${formatCurrency(max, currency)}`;
  return `${formatCurrency(min, currency)} - ${formatCurrency(max, currency)}`;
};

export const formatDate = (date, fmt = 'MMM dd, yyyy') => {
  if (!date) return '-';
  try {
    return format(parseISO(date), fmt);
  } catch {
    return format(new Date(date), fmt);
  }
};

export const formatDateTime = (date) => {
  if (!date) return '-';
  try {
    return format(parseISO(date), 'MMM dd, yyyy h:mm a');
  } catch {
    return format(new Date(date), 'MMM dd, yyyy h:mm a');
  }
};

export const formatRelativeTime = (date) => {
  if (!date) return '-';
  try {
    return formatDistanceToNow(parseISO(date), { addSuffix: true });
  } catch {
    return formatDistanceToNow(new Date(date), { addSuffix: true });
  }
};

export const formatNumber = (num) => {
  if (num == null) return '0';
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toLocaleString();
};

export const formatPercentage = (value, decimals = 1) => {
  if (value == null) return '-';
  return `${Number(value).toFixed(decimals)}%`;
};

export const formatJobType = (type) => {
  const map = {
    full_time: 'Full Time',
    part_time: 'Part Time',
    contract: 'Contract',
    internship: 'Internship',
    freelance: 'Freelance',
    remote: 'Remote',
    hybrid: 'Hybrid',
    on_site: 'On Site',
  };
  return map[type] || type;
};

export const formatExperienceLevel = (level) => {
  const map = {
    entry: 'Entry Level',
    mid: 'Mid Level',
    senior: 'Senior Level',
    lead: 'Lead',
    executive: 'Executive',
  };
  return map[level] || level;
};

export const formatPhone = (phone) => {
  if (!phone) return '-';
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  }
  return phone;
};

export const truncate = (str, length = 100) => {
  if (!str) return '';
  return str.length > length ? `${str.substring(0, length)}...` : str;
};

export const pluralize = (count, singular, plural) => {
  return count === 1 ? singular : plural || `${singular}s`;
};

export const timeAgo = (date) => formatRelativeTime(date);

export const daysRemaining = (endDate) => {
  if (!endDate) return null;
  const end = new Date(endDate);
  const now = new Date();
  const diff = Math.ceil((end - now) / (1000 * 60 * 60 * 24));
  return diff > 0 ? diff : 0;
};
