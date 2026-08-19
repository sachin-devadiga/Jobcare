import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import DashboardPage from '@/pages/employer/dashboard';
import { useAuth } from '@/hooks/useAuth';
import { useAnalytics } from '@/hooks/useAnalytics';

jest.mock('@/hooks/useAuth');
jest.mock('@/hooks/useAnalytics');
jest.mock('next/router', () => ({
  useRouter: () => ({ push: jest.fn() }),
}));
jest.mock('@/components/layout/DashboardLayout', () => ({ children }) => <div>{children}</div>);
jest.mock('@/components/analytics/StatsCard', () => ({ label, value, loading }) =>
  loading ? <div data-testid="stats-loading">Loading</div> : <div data-testid="stats-card">{label}: {value}</div>
);
jest.mock('@/components/analytics/JobChart', () => () => <div data-testid="job-chart">Chart</div>);
jest.mock('@/components/common/DataTable', () => ({ columns, rows }) =>
  <div data-testid="data-table">{rows.length} rows</div>
);
jest.mock('@/components/common/StatusBadge', () => () => <span>Badge</span>);
jest.mock('@/components/common/LoadingSpinner', () => () => <div>Loading</div>);
jest.mock('@/components/common/ErrorState', () => ({ message }) => <div>Error: {message}</div>);

describe('DashboardPage', () => {
  const mockStats = {
    activeJobs: 12,
    totalApplicants: 145,
    interviewsToday: 3,
    newMessages: 8,
    recentJobs: [
      { id: 1, title: 'Software Engineer', status: 'active', minSalary: 80000, currency: 'USD', createdAt: '2024-01-01' },
    ],
    recentApplications: [
      { id: 1, name: 'John Doe', jobTitle: 'Engineer', status: 'applied', matchScore: 85, createdAt: '2024-01-01' },
    ],
    jobPerformance: [
      { title: 'Engineer', views: 100, applications: 15, interviews: 5, hires: 2, status: 'active' },
    ],
    applicationTrends: [],
    recentActivity: [],
  };

  beforeEach(() => {
    useAuth.mockReturnValue({
      user: { name: 'Test Employer', companyName: 'Test Corp', email: 'test@test.com' },
    });
    useAnalytics.mockReturnValue({
      dashboardStats: mockStats,
      loading: false,
      error: null,
      refresh: jest.fn(),
    });
  });

  test('renders dashboard with stats', async () => {
    render(<DashboardPage />);
    expect(screen.getByText(/Welcome back/)).toBeInTheDocument();
    expect(screen.getByText(/Active Jobs/)).toBeInTheDocument();
    expect(screen.getByText(/Total Applicants/)).toBeInTheDocument();
    expect(screen.getByText(/Interviews Today/)).toBeInTheDocument();
    expect(screen.getByText(/New Messages/)).toBeInTheDocument();
  });

  test('shows stat card values', () => {
    render(<DashboardPage />);
    expect(screen.getAllByText(/12/).length).toBeGreaterThan(0);
  });

  test('shows loading skeletons when loading', () => {
    useAnalytics.mockReturnValue({
      dashboardStats: null,
      loading: true,
      error: null,
      refresh: jest.fn(),
    });
    render(<DashboardPage />);
    const skeletons = screen.getAllByTestId('stats-loading');
    expect(skeletons.length).toBeGreaterThanOrEqual(4);
  });

  test('shows error state when error occurs', () => {
    useAnalytics.mockReturnValue({
      dashboardStats: null,
      loading: false,
      error: 'Failed to load data',
      refresh: jest.fn(),
    });
    render(<DashboardPage />);
    expect(screen.getByText('Error: Failed to load data')).toBeInTheDocument();
  });

  test('renders recent applications section', () => {
    render(<DashboardPage />);
    expect(screen.getByText('Recent Applications')).toBeInTheDocument();
  });

  test('renders quick actions', () => {
    render(<DashboardPage />);
    expect(screen.getByText('Post a Job')).toBeInTheDocument();
    expect(screen.getByText('View Applicants')).toBeInTheDocument();
    expect(screen.getByText('Analytics')).toBeInTheDocument();
    expect(screen.getByText('Manage Jobs')).toBeInTheDocument();
  });

  test('renders job performance section', () => {
    render(<DashboardPage />);
    expect(screen.getByText('Job Performance Overview')).toBeInTheDocument();
  });

  test('renders key metrics', () => {
    render(<DashboardPage />);
    expect(screen.getByText('Total Jobs')).toBeInTheDocument();
    expect(screen.getByText('Total Apps')).toBeInTheDocument();
  });
});
