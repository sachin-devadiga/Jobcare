import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import StatsCard from '@/components/analytics/StatsCard';
import RevenueChart from '@/components/analytics/RevenueChart';

jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }) => <div>{children}</div>,
  AreaChart: ({ children }) => <div data-testid="area-chart">{children}</div>,
  Area: () => <div>Area</div>,
  XAxis: () => <div>XAxis</div>,
  YAxis: () => <div>YAxis</div>,
  CartesianGrid: () => <div>Grid</div>,
  Tooltip: () => <div>Tooltip</div>,
  Legend: () => <div>Legend</div>,
}));

describe('StatsCard', () => {
  const defaultProps = {
    icon: <div data-testid="test-icon">Icon</div>,
    label: 'Active Jobs',
    value: 42,
    trend: 12,
    trendLabel: 'vs last period',
    variant: 'primary',
  };

  test('renders label and value', () => {
    render(<StatsCard {...defaultProps} />);
    expect(screen.getByText('Active Jobs')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
  });

  test('renders trend percentage', () => {
    render(<StatsCard {...defaultProps} />);
    expect(screen.getByText('12%')).toBeInTheDocument();
  });

  test('renders negative trend', () => {
    render(<StatsCard {...defaultProps} trend={-5} />);
    expect(screen.getByText('5%')).toBeInTheDocument();
  });

  test('renders with prefix', () => {
    render(<StatsCard {...defaultProps} prefix="$" value={1000} />);
    expect(screen.getByText('$1K')).toBeInTheDocument();
  });

  test('renders loading skeleton', () => {
    render(<StatsCard {...defaultProps} loading />);
    const skeletons = document.querySelectorAll('.MuiSkeleton-root');
    expect(skeletons.length).toBeGreaterThanOrEqual(3);
  });

  test('renders tooltip', () => {
    render(<StatsCard {...defaultProps} tooltipTitle="Help text" />);
    expect(screen.getByText('Active Jobs')).toBeInTheDocument();
  });
});

describe('RevenueChart', () => {
  test('renders with data', () => {
    const data = [
      { name: 'Jan', revenue: 1000, subscriptions: 500 },
      { name: 'Feb', revenue: 2000, subscriptions: 800 },
    ];
    render(<RevenueChart data={data} />);
    expect(screen.getByText('Revenue Overview')).toBeInTheDocument();
    expect(screen.getByTestId('area-chart')).toBeInTheDocument();
  });

  test('shows empty state when no data', () => {
    render(<RevenueChart data={[]} />);
    expect(screen.getByText('No revenue data available')).toBeInTheDocument();
  });

  test('renders with custom title', () => {
    render(<RevenueChart data={[]} title="Custom Title" />);
    expect(screen.getByText('Custom Title')).toBeInTheDocument();
  });
});
