'use client';
import { useState } from 'react';
import {
  Box, Container, TextField, Button, Typography, Paper, InputAdornment,
  Link, CircularProgress, Alert,
} from '@mui/material';
import EmailIcon from '@mui/icons-material/Email';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import MailOutlineIcon from '@mui/icons-material/MailOutline';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { forgotPasswordSchema } from '@/utils/validators';
import { useAuth } from '@/hooks/useAuth';

export default function ForgotPasswordPage() {
  const { forgotPassword, loading } = useAuth();
  const [sent, setSent] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({ resolver: yupResolver(forgotPasswordSchema) });

  const onSubmit = async (data) => {
    try {
      await forgotPassword(data.email);
      setSent(true);
    } catch {
      /* error handled by auth */
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Container maxWidth="xs">
        <Paper sx={{ p: 4, borderRadius: 4, backdropFilter: 'blur(20px)', background: 'rgba(255,255,255,0.95)', boxShadow: '0 25px 50px rgba(0,0,0,0.15)' }}>
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Box
              sx={{
                width: 64,
                height: 64,
                borderRadius: 3,
                background: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mx: 'auto',
                mb: 2,
              }}
            >
              <MailOutlineIcon sx={{ color: '#fff', fontSize: 28 }} />
            </Box>
            <Typography variant="h5" sx={{ fontWeight: 700, color: '#1E293B' }}>
              Forgot Password?
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              {sent ? 'Check your email for reset link' : 'Enter your email and we\'ll send you a reset link'}
            </Typography>
          </Box>

          {sent ? (
            <Alert severity="success" sx={{ borderRadius: 2, mb: 2 }}>
              Password reset email sent! Check your inbox.
            </Alert>
          ) : (
            <Box component="form" onSubmit={handleSubmit(onSubmit)}>
              <TextField
                fullWidth
                label="Email Address"
                {...register('email')}
                error={!!errors.email}
                helperText={errors.email?.message}
                sx={{ mb: 3 }}
                InputProps={{
                  startAdornment: <InputAdornment position="start"><EmailIcon sx={{ color: 'text.secondary', fontSize: 20 }} /></InputAdornment>,
                }}
              />
              <Button
                fullWidth
                variant="contained"
                type="submit"
                disabled={loading}
                sx={{ py: 1.5, borderRadius: 3, fontSize: '1rem', mb: 2 }}
              >
                {loading ? <CircularProgress size={22} sx={{ color: '#fff' }} /> : 'Send Reset Link'}
              </Button>
            </Box>
          )}

          <Box sx={{ textAlign: 'center', mt: 2 }}>
            <Link href="/auth/login" variant="body2" sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, fontWeight: 500 }}>
              <ArrowBackIcon sx={{ fontSize: 16 }} />
              Back to Sign In
            </Link>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
}
