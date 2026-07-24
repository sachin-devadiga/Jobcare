import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ApplicantCard from '@/components/applications/ApplicantCard';

jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: jest.fn() }),
}));

jest.mock('@/components/common/StatusBadge', () => ({ status }) => <span data-testid="status-badge">{status}</span>);

describe('ApplicantCard', () => {
  const mockApplicant = {
    _id: '1',
    name: 'John Doe',
    currentPosition: 'Software Engineer',
    location: 'Bangalore, India',
    status: 'under_review',
    matchScore: 85,
    skills: ['Python', 'Django', 'JavaScript', 'React'],
    createdAt: '2024-01-15T10:00:00Z',
    avatar: null,
  };

  test('renders applicant name', () => {
    render(<ApplicantCard applicant={mockApplicant} />);
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  test('renders applicant position', () => {
    render(<ApplicantCard applicant={mockApplicant} />);
    expect(screen.getByText('Software Engineer')).toBeInTheDocument();
  });

  test('renders applicant location', () => {
    render(<ApplicantCard applicant={mockApplicant} />);
    expect(screen.getByText('Bangalore, India')).toBeInTheDocument();
  });

  test('renders status badge', () => {
    render(<ApplicantCard applicant={mockApplicant} />);
    expect(screen.getByTestId('status-badge')).toHaveTextContent('under_review');
  });

  test('renders AI match score', () => {
    render(<ApplicantCard applicant={mockApplicant} />);
    expect(screen.getByText('AI Match Score')).toBeInTheDocument();
    expect(screen.getByText('85%')).toBeInTheDocument();
  });

  test('renders skills chips', () => {
    render(<ApplicantCard applicant={mockApplicant} />);
    expect(screen.getByText('Python')).toBeInTheDocument();
    expect(screen.getByText('Django')).toBeInTheDocument();
    expect(screen.getByText('JavaScript')).toBeInTheDocument();
  });

  test('shows +N for extra skills', () => {
    render(<ApplicantCard applicant={mockApplicant} />);
    expect(screen.getByText('+1')).toBeInTheDocument();
  });

  test('handles missing match score', () => {
    const applicant = { ...mockApplicant, matchScore: 0 };
    render(<ApplicantCard applicant={applicant} />);
    expect(screen.queryByText('AI Match Score')).not.toBeInTheDocument();
  });

  test('handles missing location', () => {
    const applicant = { ...mockApplicant, location: null };
    render(<ApplicantCard applicant={applicant} />);
    expect(screen.queryByText('Bangalore, India')).not.toBeInTheDocument();
  });

  test('handles missing skills', () => {
    const applicant = { ...mockApplicant, skills: [] };
    render(<ApplicantCard applicant={applicant} />);
    expect(screen.queryByText('Python')).not.toBeInTheDocument();
  });

  test('handles unknown name', () => {
    const applicant = { _id: '1', name: null };
    render(<ApplicantCard applicant={applicant} />);
    expect(screen.getByText('Unknown')).toBeInTheDocument();
  });

  test('renders with aiScore as fallback', () => {
    const applicant = { ...mockApplicant, matchScore: null, aiScore: 92 };
    render(<ApplicantCard applicant={applicant} />);
    expect(screen.getByText('92%')).toBeInTheDocument();
  });
});
