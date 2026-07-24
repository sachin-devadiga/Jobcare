'use client';
import { useState } from 'react';
import {
  Box, TextField, Button, Grid, Typography, Paper, MenuItem, Chip,
  Autocomplete, FormControlLabel, Switch, Divider, CircularProgress,
} from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { jobSchema } from '@/utils/validators';
import { JOB_TYPES, EXPERIENCE_LEVELS, CURRENCIES } from '@/utils/constants';

const commonSkills = [
  'JavaScript', 'Python', 'Java', 'React', 'Node.js', 'TypeScript',
  'SQL', 'AWS', 'Docker', 'Kubernetes', 'Machine Learning', 'Data Analysis',
  'Project Management', 'UI/UX Design', 'Digital Marketing', 'Sales',
  'Customer Support', 'Finance', 'HR', 'Communication',
];

export default function JobForm({ job, onSubmit, loading = false, onSaveDraft }) {
  const [skills, setSkills] = useState(job?.skills || []);
  const isEditing = !!job;

  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
    setValue,
    watch,
  } = useForm({
    resolver: yupResolver(jobSchema),
    defaultValues: {
      title: job?.title || '',
      department: job?.department || '',
      location: job?.location || '',
      locationType: job?.locationType || 'on_site',
      type: job?.type || 'full_time',
      experienceLevel: job?.experienceLevel || 'mid',
      minSalary: job?.minSalary || '',
      maxSalary: job?.maxSalary || '',
      currency: job?.currency || 'USD',
      salaryVisible: job?.salaryVisible ?? true,
      description: job?.description || '',
      responsibilities: job?.responsibilities || '',
      requirements: job?.requirements || '',
      benefits: job?.benefits || '',
      skills: job?.skills || [],
      questions: job?.questions || [],
      status: job?.status || 'draft',
    },
  });

  const handleFormSubmit = (data) => {
    if (onSubmit) onSubmit({ ...data, skills });
  };

  const handleSaveAsDraft = () => {
    if (onSaveDraft) {
      const data = {
        title: watch('title'),
        department: watch('department'),
        location: watch('location'),
        locationType: watch('locationType'),
        type: watch('type'),
        experienceLevel: watch('experienceLevel'),
        minSalary: watch('minSalary'),
        maxSalary: watch('maxSalary'),
        description: watch('description'),
        requirements: watch('requirements'),
        skills,
        status: 'draft',
      };
      onSaveDraft(data);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit(handleFormSubmit)}>
      <Paper sx={{ p: 3, mb: 3, borderRadius: 3 }}>
        <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>Basic Information</Typography>
        <Grid container spacing={2.5}>
          <Grid item xs={12}>
            <TextField
              fullWidth label="Job Title *" {...register('title')}
              error={!!errors.title} helperText={errors.title?.message}
              placeholder="e.g. Senior Frontend Developer"
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField fullWidth label="Department" {...register('department')} placeholder="e.g. Engineering" />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField fullWidth label="Location *" {...register('location')} placeholder="e.g. San Francisco, CA" error={!!errors.location} helperText={errors.location?.message} />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField fullWidth select label="Location Type" {...register('locationType')}>
              <MenuItem value="on_site">On-site</MenuItem>
              <MenuItem value="hybrid">Hybrid</MenuItem>
              <MenuItem value="remote">Remote</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField fullWidth select label="Job Type *" {...register('type')} error={!!errors.type}>
              {Object.entries(JOB_TYPES).map(([key, val]) => (
                <MenuItem key={key} value={val}>{val.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField fullWidth select label="Experience Level *" {...register('experienceLevel')} error={!!errors.experienceLevel}>
              {Object.entries(EXPERIENCE_LEVELS).map(([key, val]) => (
                <MenuItem key={key} value={val}>{val.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</MenuItem>
              ))}
            </TextField>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 3, mb: 3, borderRadius: 3 }}>
        <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>Compensation</Typography>
        <Grid container spacing={2.5} alignItems="center">
          <Grid item xs={12} sm={4}>
            <TextField fullWidth label="Min Salary" type="number" {...register('minSalary')} />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField fullWidth label="Max Salary" type="number" {...register('maxSalary')} />
          </Grid>
          <Grid item xs={12} sm={2}>
            <TextField fullWidth select label="Currency" {...register('currency')}>
              {Object.entries(CURRENCIES).map(([key, val]) => (
                <MenuItem key={key} value={val}>{val}</MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={2}>
            <FormControlLabel
              control={<Switch defaultChecked={watch('salaryVisible')} {...register('salaryVisible')} />}
              label="Show salary"
              sx={{ '& .MuiTypography-root': { fontSize: '0.875rem' } }}
            />
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 3, mb: 3, borderRadius: 3 }}>
        <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>Job Details</Typography>
        <Grid container spacing={2.5}>
          <Grid item xs={12}>
            <TextField fullWidth multiline rows={6} label="Job Description *" {...register('description')} error={!!errors.description} helperText={errors.description?.message} placeholder="Describe the role, responsibilities, and what makes this opportunity great..." />
          </Grid>
          <Grid item xs={12}>
            <TextField fullWidth multiline rows={4} label="Responsibilities" {...register('responsibilities')} placeholder="List key responsibilities..." />
          </Grid>
          <Grid item xs={12}>
            <TextField fullWidth multiline rows={4} label="Requirements *" {...register('requirements')} error={!!errors.requirements} helperText={errors.requirements?.message} placeholder="List required qualifications and skills..." />
          </Grid>
          <Grid item xs={12}>
            <TextField fullWidth multiline rows={4} label="Benefits" {...register('benefits')} placeholder="List benefits and perks..." />
          </Grid>
          <Grid item xs={12}>
            <Controller
              name="skills"
              control={control}
              render={({ field }) => (
                <Autocomplete
                  multiple
                  freeSolo
                  options={commonSkills}
                  value={skills}
                  onChange={(_, newVal) => { setSkills(newVal); field.onChange(newVal); }}
                  renderTags={(value, getTagProps) =>
                    value.map((option, index) => (
                      <Chip label={option} {...getTagProps({ index })} key={option} sx={{ borderRadius: 2 }} />
                    ))
                  }
                  renderInput={(params) => (
                    <TextField {...params} label="Skills *" placeholder="Type to add skills" error={!!errors.skills} helperText={skills.length === 0 ? 'Add at least one skill' : ''} />
                  )}
                />
              )}
            />
          </Grid>
        </Grid>
      </Paper>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="outlined" type="button" sx={{ minWidth: 140 }}>Cancel</Button>
          {!isEditing && (
            <Button variant="outlined" type="button" onClick={handleSaveAsDraft} disabled={loading} sx={{ minWidth: 140 }}>
              Save as Draft
            </Button>
          )}
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="contained" type="submit" disabled={loading} sx={{ minWidth: 180, borderRadius: 3 }}>
            {loading ? <CircularProgress size={20} sx={{ color: '#fff' }} /> : isEditing ? 'Update Job' : 'Publish Job'}
          </Button>
        </Box>
      </Box>
    </Box>
  );
}
