'use client';
import { useState, useCallback } from 'react';
import {
  Box,
  TextField,
  Button,
  Grid,
  Typography,
  Paper,
  MenuItem,
  IconButton,
  Avatar,
  InputAdornment,
  CircularProgress,
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import PhotoCameraIcon from '@mui/icons-material/PhotoCamera';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { companyProfileSchema } from '@/utils/validators';

const industries = [
  'Technology', 'Healthcare', 'Finance', 'Education', 'Manufacturing',
  'Retail', 'Real Estate', 'Consulting', 'Media', 'Transportation',
  'Energy', 'Hospitality', 'Other',
];

const companySizes = [
  '1-10', '11-50', '51-200', '201-500', '501-1000', '1001-5000', '5000+',
];

export default function CompanyProfileForm({ profile, onSubmit, loading = false }) {
  const [logoPreview, setLogoPreview] = useState(profile?.logo || '');
  const [bannerPreview, setBannerPreview] = useState(profile?.banner || '');

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm({
    resolver: yupResolver(companyProfileSchema),
    defaultValues: {
      companyName: profile?.companyName || '',
      companyEmail: profile?.companyEmail || '',
      phone: profile?.phone || '',
      website: profile?.website || '',
      industry: profile?.industry || '',
      companySize: profile?.companySize || '',
      foundedYear: profile?.foundedYear || '',
      description: profile?.description || '',
      mission: profile?.mission || '',
      vision: profile?.vision || '',
      address: profile?.address || '',
      city: profile?.city || '',
      state: profile?.state || '',
      country: profile?.country || '',
      postalCode: profile?.postalCode || '',
      socialLinks: {
        linkedin: profile?.socialLinks?.linkedin || '',
        twitter: profile?.socialLinks?.twitter || '',
        facebook: profile?.socialLinks?.facebook || '',
        instagram: profile?.socialLinks?.instagram || '',
      },
    },
  });

  const onLogoDrop = useCallback((files) => {
    if (files[0]) {
      const reader = new FileReader();
      reader.onload = (e) => setLogoPreview(e.target.result);
      reader.readAsDataURL(files[0]);
      setValue('logo', files[0]);
    }
  }, [setValue]);

  const onBannerDrop = useCallback((files) => {
    if (files[0]) {
      const reader = new FileReader();
      reader.onload = (e) => setBannerPreview(e.target.result);
      reader.readAsDataURL(files[0]);
      setValue('banner', files[0]);
    }
  }, [setValue]);

  const { getRootProps: getLogoRoot, getInputProps: getLogoInput } = useDropzone({
    onDrop: onLogoDrop,
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.svg'] },
    maxFiles: 1,
  });

  const { getRootProps: getBannerRoot, getInputProps: getBannerInput } = useDropzone({
    onDrop: onBannerDrop,
    accept: { 'image/*': ['.png', '.jpg', '.jpeg'] },
    maxFiles: 1,
  });

  const handleFormSubmit = (data) => {
    onSubmit(data);
  };

  return (
    <Box component="form" onSubmit={handleSubmit(handleFormSubmit)}>
      <Paper sx={{ p: 3, mb: 3, borderRadius: 3 }}>
        <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>Company Logo & Banner</Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>Company Logo</Typography>
            <Box
              {...getLogoRoot()}
              sx={{
                width: 120,
                height: 120,
                borderRadius: 3,
                border: '2px dashed',
                borderColor: 'divider',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                overflow: 'hidden',
                bgcolor: 'action.hover',
                transition: 'all 0.2s',
                '&:hover': { borderColor: 'primary.main', bgcolor: 'primary.main' + '08' },
              }}
            >
              <input {...getLogoInput()} />
              {logoPreview ? (
                <Avatar src={logoPreview} sx={{ width: '100%', height: '100%', borderRadius: 2 }} />
              ) : (
                <PhotoCameraIcon sx={{ color: 'text.disabled', fontSize: 32 }} />
              )}
            </Box>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>Banner Image</Typography>
            <Box
              {...getBannerRoot()}
              sx={{
                width: '100%',
                height: 120,
                borderRadius: 3,
                border: '2px dashed',
                borderColor: 'divider',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                overflow: 'hidden',
                bgcolor: 'action.hover',
                transition: 'all 0.2s',
                '&:hover': { borderColor: 'primary.main' },
              }}
            >
              <input {...getBannerInput()} />
              {bannerPreview ? (
                <Box
                  component="img"
                  src={bannerPreview}
                  sx={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              ) : (
                <PhotoCameraIcon sx={{ color: 'text.disabled', fontSize: 32 }} />
              )}
            </Box>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 3, mb: 3, borderRadius: 3 }}>
        <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>Basic Information</Typography>
        <Grid container spacing={2.5}>
          <Grid item xs={12} sm={6}>
            <TextField fullWidth label="Company Name" {...register('companyName')} error={!!errors.companyName} helperText={errors.companyName?.message} />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField fullWidth label="Company Email" {...register('companyEmail')} error={!!errors.companyEmail} helperText={errors.companyEmail?.message} />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField fullWidth label="Phone" {...register('phone')} error={!!errors.phone} helperText={errors.phone?.message} />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField fullWidth label="Website" {...register('website')} error={!!errors.website} helperText={errors.website?.message} />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField fullWidth select label="Industry" {...register('industry')} error={!!errors.industry}>
              {industries.map((ind) => (<MenuItem key={ind} value={ind}>{ind}</MenuItem>))}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField fullWidth select label="Company Size" {...register('companySize')} error={!!errors.companySize}>
              {companySizes.map((size) => (<MenuItem key={size} value={size}>{size} employees</MenuItem>))}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField fullWidth label="Founded Year" type="number" {...register('foundedYear')} error={!!errors.foundedYear} helperText={errors.foundedYear?.message} />
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 3, mb: 3, borderRadius: 3 }}>
        <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>About</Typography>
        <Grid container spacing={2.5}>
          <Grid item xs={12}>
            <TextField fullWidth multiline rows={4} label="Company Description" {...register('description')} error={!!errors.description} helperText={errors.description?.message} />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField fullWidth multiline rows={3} label="Mission" {...register('mission')} />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField fullWidth multiline rows={3} label="Vision" {...register('vision')} />
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 3, mb: 3, borderRadius: 3 }}>
        <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>Address</Typography>
        <Grid container spacing={2.5}>
          <Grid item xs={12}>
            <TextField fullWidth label="Address" {...register('address')} />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField fullWidth label="City" {...register('city')} />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField fullWidth label="State" {...register('state')} />
          </Grid>
          <Grid item xs={12} sm={2}>
            <TextField fullWidth label="Postal Code" {...register('postalCode')} />
          </Grid>
          <Grid item xs={12} sm={2}>
            <TextField fullWidth label="Country" {...register('country')} />
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 3, mb: 3, borderRadius: 3 }}>
        <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>Social Links</Typography>
        <Grid container spacing={2.5}>
          <Grid item xs={12} sm={6}>
            <TextField fullWidth label="LinkedIn" {...register('socialLinks.linkedin')} error={!!errors.socialLinks?.linkedin} />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField fullWidth label="Twitter" {...register('socialLinks.twitter')} error={!!errors.socialLinks?.twitter} />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField fullWidth label="Facebook" {...register('socialLinks.facebook')} error={!!errors.socialLinks?.facebook} />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField fullWidth label="Instagram" {...register('socialLinks.instagram')} error={!!errors.socialLinks?.instagram} />
          </Grid>
        </Grid>
      </Paper>

      <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
        <Button variant="outlined" type="button" sx={{ minWidth: 140 }}>Cancel</Button>
        <Button variant="contained" type="submit" disabled={loading} sx={{ minWidth: 180 }}>
          {loading ? <CircularProgress size={20} sx={{ color: '#fff' }} /> : 'Save Changes'}
        </Button>
      </Box>
    </Box>
  );
}
