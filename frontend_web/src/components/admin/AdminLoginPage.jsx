import { useState } from 'react';
import { Box, Card, CardContent, Typography, TextField, Button, InputAdornment, IconButton, Alert, Divider } from '@mui/material';
import { useRouter } from 'next/navigation';
import { AdminAuthProvider, useAdminAuth } from '@/contexts/AdminAuthContext';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import LockIcon from '@mui/icons-material/Lock';
import EmailIcon from '@mui/icons-material/Email';
import SecurityIcon from '@mui/icons-material/Security';

function AdminLoginForm() {
  const { login, verifyOtp, loading, error, otpSent, clearError } = useAdminAuth();
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [otp, setOtp] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [tempToken, setTempToken] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!email || !password) return;
    try {
      const result = await login({ email, password });
      if (result?.otpRequired) {
        setTempToken(result.tempToken);
      }
    } catch {}
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    if (!otp) return;
    try {
      await verifyOtp({ email, otp, tempToken });
    } catch {}
  };

  if (otpSent) {
    return (
      <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: '#0F172A', p: 2 }}>
        <Card sx={{ maxWidth: 420, width: '100%', bgcolor: '#1E293B', borderRadius: 4 }}>
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ textAlign: 'center', mb: 4 }}>
              <Box sx={{ width: 64, height: 64, borderRadius: 3, background: 'linear-gradient(135deg, #818CF8 0%, #A78BFA 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', mx: 'auto', mb: 2 }}>
                <SecurityIcon sx={{ color: '#fff', fontSize: 32 }} />
              </Box>
              <Typography variant="h5" sx={{ fontWeight: 700, color: '#F1F5F9', mb: 1 }}>Two-Factor Authentication</Typography>
              <Typography variant="body2" sx={{ color: '#64748B' }}>Enter the OTP sent to your registered email</Typography>
            </Box>
            {error && <Alert severity="error" sx={{ mb: 2, borderRadius: 2, bgcolor: 'rgba(248,113,113,0.15)', color: '#F87171' }}>{error}</Alert>}
            <Box component="form" onSubmit={handleVerifyOtp}>
              <TextField fullWidth label="OTP Code" value={otp} onChange={(e) => setOtp(e.target.value)} placeholder="Enter 6-digit OTP"
                sx={{ mb: 3, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' }, '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.2)' }, '&.Mui-focused fieldset': { borderColor: '#818CF8' } }, '& .MuiInputLabel-root': { color: '#64748B' } }}
                InputProps={{ startAdornment: <InputAdornment position="start"><SecurityIcon sx={{ color: '#64748B' }} /></InputAdornment> }} />
              <Button fullWidth type="submit" variant="contained" disabled={loading || otp.length < 4}
                sx={{ py: 1.5, borderRadius: 2, background: 'linear-gradient(135deg, #818CF8 0%, #A78BFA 100%)', '&:hover': { background: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)' } }}>
                {loading ? 'Verifying...' : 'Verify OTP'}
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: '#0F172A', p: 2 }}>
      <Card sx={{ maxWidth: 420, width: '100%', bgcolor: '#1E293B', borderRadius: 4 }}>
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Box sx={{ width: 64, height: 64, borderRadius: 3, background: 'linear-gradient(135deg, #818CF8 0%, #A78BFA 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', mx: 'auto', mb: 2 }}>
              <LockIcon sx={{ color: '#fff', fontSize: 32 }} />
            </Box>
            <Typography variant="h5" sx={{ fontWeight: 700, color: '#F1F5F9', mb: 1 }}>Admin Login</Typography>
            <Typography variant="body2" sx={{ color: '#64748B' }}>Sign in to manage JobCare Voice</Typography>
          </Box>
          {error && <Alert severity="error" sx={{ mb: 2, borderRadius: 2, bgcolor: 'rgba(248,113,113,0.15)', color: '#F87171' }}>{error}</Alert>}
          <Box component="form" onSubmit={handleLogin}>
            <TextField fullWidth label="Email Address" type="email" value={email} onChange={(e) => { setEmail(e.target.value); clearError(); }}
              sx={{ mb: 2.5, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' }, '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.2)' }, '&.Mui-focused fieldset': { borderColor: '#818CF8' } }, '& .MuiInputLabel-root': { color: '#64748B' } }}
              InputProps={{ startAdornment: <InputAdornment position="start"><EmailIcon sx={{ color: '#64748B' }} /></InputAdornment> }} />
            <TextField fullWidth label="Password" type={showPassword ? 'text' : 'password'} value={password} onChange={(e) => { setPassword(e.target.value); clearError(); }}
              sx={{ mb: 3, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' }, '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.2)' }, '&.Mui-focused fieldset': { borderColor: '#818CF8' } }, '& .MuiInputLabel-root': { color: '#64748B' } }}
              InputProps={{ startAdornment: <InputAdornment position="start"><LockIcon sx={{ color: '#64748B' }} /></InputAdornment>, endAdornment: <InputAdornment position="end"><IconButton onClick={() => setShowPassword(!showPassword)} sx={{ color: '#64748B' }}>{showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}</IconButton></InputAdornment> }} />
            <Button fullWidth type="submit" variant="contained" disabled={loading || !email || !password}
              sx={{ py: 1.5, borderRadius: 2, background: 'linear-gradient(135deg, #818CF8 0%, #A78BFA 100%)', '&:hover': { background: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)' } }}>
              {loading ? 'Signing in...' : 'Sign In'}
            </Button>
          </Box>
          <Divider sx={{ my: 3, borderColor: 'rgba(255,255,255,0.06)' }} />
          <Typography variant="caption" sx={{ color: '#64748B', textAlign: 'center', display: 'block' }}>
            Admin access only. Unauthorized access is prohibited.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}

export default function AdminLoginPage() {
  return (
    <AdminAuthProvider>
      <AdminLoginForm />
    </AdminAuthProvider>
  );
}
