import dynamic from 'next/dynamic';

export function getServerSideProps() {
  return { props: {} };
}

const AdminLoginPage = dynamic(() => import('@/components/admin/AdminLoginPage'), { ssr: false });

export default AdminLoginPage;
