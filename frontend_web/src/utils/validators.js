import * as yup from 'yup';

export const loginSchema = yup.object().shape({
  email: yup.string().email('Invalid email').required('Email is required'),
  password: yup.string().min(6, 'Min 6 characters').required('Password is required'),
});

export const signupSchema = yup.object().shape({
  companyName: yup.string().required('Company name is required').min(2, 'Min 2 characters'),
  email: yup.string().email('Invalid email').required('Email is required'),
  password: yup.string().min(6, 'Min 6 characters').required('Password is required'),
  confirmPassword: yup.string().oneOf([yup.ref('password')], 'Passwords must match'),
  phone: yup.string().matches(/^\+?[\d\s-]{7,15}$/, 'Invalid phone number'),
});

export const forgotPasswordSchema = yup.object().shape({
  email: yup.string().email('Invalid email').required('Email is required'),
});

export const resetPasswordSchema = yup.object().shape({
  password: yup.string().min(6, 'Min 6 characters').required('Password is required'),
  confirmPassword: yup.string().oneOf([yup.ref('password')], 'Passwords must match'),
});

export const jobSchema = yup.object().shape({
  title: yup.string().required('Job title is required').min(3, 'Min 3 characters'),
  department: yup.string(),
  location: yup.string().required('Location is required'),
  locationType: yup.string().oneOf(['remote', 'hybrid', 'on_site'], 'Invalid location type'),
  type: yup.string().oneOf(['full_time', 'part_time', 'contract', 'internship', 'freelance', 'remote']).required('Job type is required'),
  experienceLevel: yup.string().oneOf(['entry', 'mid', 'senior', 'lead', 'executive']).required('Experience level is required'),
  minSalary: yup.number().positive('Must be positive').nullable(),
  maxSalary: yup.number().positive('Must be positive').nullable(),
  currency: yup.string().oneOf(['USD', 'INR', 'EUR', 'GBP']),
  salaryVisible: yup.boolean(),
  description: yup.string().required('Description is required').min(50, 'Min 50 characters'),
  responsibilities: yup.string(),
  requirements: yup.string().required('Requirements are required'),
  benefits: yup.string(),
  skills: yup.array().of(yup.string()).min(1, 'At least one skill required'),
  questions: yup.array().of(
    yup.object().shape({
      question: yup.string(),
      required: yup.boolean(),
    })
  ),
  status: yup.string().oneOf(['draft', 'published']),
});

export const companyProfileSchema = yup.object().shape({
  companyName: yup.string().required('Company name is required'),
  companyEmail: yup.string().email('Invalid email'),
  phone: yup.string(),
  website: yup.string().url('Invalid URL'),
  industry: yup.string(),
  companySize: yup.string(),
  foundedYear: yup.number().min(1800).max(new Date().getFullYear()),
  description: yup.string().min(50, 'Min 50 characters'),
  mission: yup.string(),
  vision: yup.string(),
  address: yup.string(),
  city: yup.string(),
  state: yup.string(),
  country: yup.string(),
  postalCode: yup.string(),
  socialLinks: yup.object().shape({
    linkedin: yup.string().url('Invalid URL'),
    twitter: yup.string().url('Invalid URL'),
    facebook: yup.string().url('Invalid URL'),
    instagram: yup.string().url('Invalid URL'),
  }),
});

export const applicationFilterSchema = yup.object().shape({
  status: yup.string(),
  search: yup.string(),
  jobId: yup.string(),
  dateFrom: yup.date(),
  dateTo: yup.date(),
  matchScoreMin: yup.number().min(0).max(100),
  sortBy: yup.string(),
  sortOrder: yup.string(),
});
