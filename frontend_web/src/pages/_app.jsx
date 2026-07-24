import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { AuthProvider } from '@/contexts/AuthContext';
import { AdminAuthProvider } from '@/contexts/AdminAuthContext';
import { ThemeContextProvider } from '@/contexts/ThemeContext';
import { NotificationProvider } from '@/contexts/NotificationContext';
import AdminLayout from '@/components/admin/AdminLayout';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import '@/styles/globals.css';

function App({ Component, pageProps }) {
  const router = useRouter();

  useEffect(() => {
    const handleStart = () => {
      const nprogress = require('nprogress');
      nprogress.start();
    };
    const handleStop = () => {
      const nprogress = require('nprogress');
      nprogress.done();
    };

    router.events.on('routeChangeStart', handleStart);
    router.events.on('routeChangeComplete', handleStop);
    router.events.on('routeChangeError', handleStop);

    return () => {
      router.events.off('routeChangeStart', handleStart);
      router.events.off('routeChangeComplete', handleStop);
      router.events.off('routeChangeError', handleStop);
    };
  }, [router]);

  const isAdminRoute = router.pathname.startsWith('/admin') && router.pathname !== '/admin/login';
  const getLayout = Component.getLayout || ((page) => page);

  const content = (
    <AdminAuthProvider>
      {isAdminRoute ? <AdminLayout>{getLayout(<Component {...pageProps} />)}</AdminLayout> : getLayout(<Component {...pageProps} />)}
    </AdminAuthProvider>
  );

  return (
    <ThemeContextProvider>
      <AuthProvider>
        <NotificationProvider>
          {content}
          <ToastContainer
            position="top-right"
            autoClose={4000}
            hideProgressBar={false}
            newestOnTop
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
            theme="light"
          />
        </NotificationProvider>
      </AuthProvider>
    </ThemeContextProvider>
  );
}

export default App;
