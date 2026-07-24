export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

export const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME || 'JobCare Voice';

export const APP_URL = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000';

export const ROLES = {
  EMPLOYER: 'employer',
  JOB_SEEKER: 'job_seeker',
  ADMIN: 'admin',
};

export const JOB_STATUS = {
  DRAFT: 'draft',
  PUBLISHED: 'published',
  CLOSED: 'closed',
  FILLED: 'filled',
  ARCHIVED: 'archived',
};

export const APPLICATION_STATUS = {
  NEW: 'new',
  REVIEWING: 'reviewing',
  SHORTLISTED: 'shortlisted',
  INTERVIEW_SCHEDULED: 'interview_scheduled',
  INTERVIEWED: 'interviewed',
  OFFERED: 'offered',
  HIRED: 'hired',
  REJECTED: 'rejected',
  WITHDRAWN: 'withdrawn',
};

export const APPLICATION_PIPELINE_STAGES = [
  { key: 'new', label: 'New', color: '#3B82F6' },
  { key: 'shortlisted', label: 'Shortlisted', color: '#22C55E' },
  { key: 'interview_scheduled', label: 'Interview', color: '#F59E0B' },
  { key: 'interviewed', label: 'Interviewed', color: '#8B5CF6' },
  { key: 'offered', label: 'Offered', color: '#14B8A6' },
  { key: 'hired', label: 'Hired', color: '#059669' },
  { key: 'rejected', label: 'Rejected', color: '#EF4444' },
];

export const INTERVIEW_TYPES = {
  PHONE: 'phone',
  VIDEO: 'video',
  IN_PERSON: 'in_person',
  VOICE: 'voice',
};

export const SUBSCRIPTION_PLANS = {
  FREE: 'free',
  BASIC: 'basic',
  PROFESSIONAL: 'professional',
  ENTERPRISE: 'enterprise',
};

export const JOB_TYPES = {
  FULL_TIME: 'full_time',
  PART_TIME: 'part_time',
  CONTRACT: 'contract',
  INTERNSHIP: 'internship',
  FREELANCE: 'freelance',
  REMOTE: 'remote',
};

export const EXPERIENCE_LEVELS = {
  ENTRY: 'entry',
  MID: 'mid',
  SENIOR: 'senior',
  LEAD: 'lead',
  EXECUTIVE: 'executive',
};

export const CURRENCIES = {
  USD: 'USD',
  INR: 'INR',
  EUR: 'EUR',
  GBP: 'GBP',
};

export const PAYMENT_INTERVALS = {
  MONTHLY: 'monthly',
  YEARLY: 'yearly',
};

export const SKILL_LEVELS = {
  BEGINNER: 'beginner',
  INTERMEDIATE: 'intermediate',
  ADVANCED: 'advanced',
  EXPERT: 'expert',
};

export const SIDEBAR_WIDTH = 260;
export const SIDEBAR_COLLAPSED_WIDTH = 72;
export const HEADER_HEIGHT = 72;

export const TOAST_DURATION = 4000;

export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 10,
  PAGE_SIZES: [10, 25, 50, 100],
};

export const CHART_COLORS = [
  '#6366F1',
  '#8B5CF6',
  '#EC4899',
  '#F43F5E',
  '#F97316',
  '#EAB308',
  '#22C55E',
  '#14B8A6',
  '#06B6D4',
  '#3B82F6',
];

export const CHART_COLOR_MAP = {
  primary: '#6366F1',
  secondary: '#8B5CF6',
  success: '#22C55E',
  warning: '#F59E0B',
  danger: '#EF4444',
  info: '#06B6D4',
  pink: '#EC4899',
  orange: '#F97316',
  teal: '#14B8A6',
  blue: '#3B82F6',
};

export const STATS_COLOR_VARIANTS = {
  success: { bg: '#ECFDF5', text: '#059669', icon: '#22C55E' },
  warning: { bg: '#FFFBEB', text: '#D97706', icon: '#F59E0B' },
  danger: { bg: '#FEF2F2', text: '#DC2626', icon: '#EF4444' },
  info: { bg: '#EFF6FF', text: '#2563EB', icon: '#3B82F6' },
  primary: { bg: '#EEF2FF', text: '#4F46E5', icon: '#6366F1' },
};

export const STATUS_COLORS = {
  draft: { bg: '#F3F4F6', text: '#6B7280', label: 'Draft' },
  published: { bg: '#ECFDF5', text: '#059669', label: 'Published' },
  closed: { bg: '#FEF3C7', text: '#D97706', label: 'Closed' },
  filled: { bg: '#EFF6FF', text: '#2563EB', label: 'Filled' },
  archived: { bg: '#F3F4F6', text: '#9CA3AF', label: 'Archived' },
  new: { bg: '#EFF6FF', text: '#2563EB', label: 'New' },
  reviewing: { bg: '#FEF3C7', text: '#D97706', label: 'Reviewing' },
  shortlisted: { bg: '#ECFDF5', text: '#059669', label: 'Shortlisted' },
  interview_scheduled: { bg: '#F0FDF4', text: '#16A34A', label: 'Interview Scheduled' },
  interviewed: { bg: '#FDF4FF', text: '#C026D3', label: 'Interviewed' },
  offered: { bg: '#ECFDF5', text: '#059669', label: 'Offered' },
  hired: { bg: '#EFF6FF', text: '#2563EB', label: 'Hired' },
  rejected: { bg: '#FEF2F2', text: '#DC2626', label: 'Rejected' },
  withdrawn: { bg: '#F3F4F6', text: '#6B7280', label: 'Withdrawn' },
};

export const EXPORT_FORMATS = [
  { value: 'xlsx', label: 'Excel (.xlsx)', icon: 'table_chart' },
  { value: 'csv', label: 'CSV (.csv)', icon: 'table_rows' },
  { value: 'pdf', label: 'PDF (.pdf)', icon: 'picture_as_pdf' },
];

export const DATE_RANGE_PRESETS = [
  { value: '7d', label: 'Last 7 days' },
  { value: '30d', label: 'Last 30 days' },
  { value: '90d', label: 'Last 90 days' },
  { value: '1y', label: 'Last year' },
  { value: 'custom', label: 'Custom range' },
];
