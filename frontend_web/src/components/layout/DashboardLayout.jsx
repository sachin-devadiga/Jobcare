'use client';
import { useState, useEffect } from 'react';
import { Box } from '@mui/material';
import { useRouter, usePathname } from 'next/navigation';
import Sidebar from './Sidebar';
import Header from './Header';
import Footer from './Footer';
import { useAuth } from '@/hooks/useAuth';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import { HEADER_HEIGHT } from '@/utils/constants';

export default function DashboardLayout({ children }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { user, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth/login');
    }
  }, [user, loading, router]);

  useEffect(() => {
    const stored = localStorage.getItem('sidebarCollapsed');
    if (stored === 'true') setSidebarCollapsed(true);
  }, []);

  const toggleSidebar = () => {
    const next = !sidebarCollapsed;
    setSidebarCollapsed(next);
    localStorage.setItem('sidebarCollapsed', next);
  };

  if (loading) return <LoadingSpinner message="Authenticating..." />;
  if (!user) return null;

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <Sidebar collapsed={sidebarCollapsed} onToggle={toggleSidebar} />
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          minWidth: 0,
          ml: { xs: 0, md: sidebarCollapsed ? '72px' : '260px' },
          transition: 'margin-left 0.3s ease',
        }}
      >
        <Header onMenuToggle={() => setSidebarCollapsed((prev) => !prev)} />
        <Box
          component="main"
          sx={{
            flex: 1,
            p: { xs: 2, sm: 3 },
            overflow: 'auto',
            animation: 'fadeIn 0.3s ease-in-out',
          }}
        >
          {children}
        </Box>
        <Footer />
      </Box>
    </Box>
  );
}
