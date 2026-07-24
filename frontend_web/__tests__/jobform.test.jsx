import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import JobForm from '@/components/jobs/JobForm';

jest.mock('react-hook-form', () => ({
  useForm: jest.fn(() => ({
    register: jest.fn(() => ({})),
    handleSubmit: jest.fn((fn) => (e) => { e?.preventDefault?.(); fn({}); }),
    control: {},
    formState: { errors: {} },
    setValue: jest.fn(),
    watch: jest.fn(() => ''),
  })),
  Controller: ({ render }) => render({ field: { value: [], onChange: jest.fn() } }),
}));

jest.mock('@hookform/resolvers/yup', () => ({
  yupResolver: jest.fn(() => () => ({})),
}));

jest.mock('@/utils/validators', () => ({
  jobSchema: {},
}));

describe('JobForm', () => {
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  test('renders all form sections', () => {
    render(<JobForm onSubmit={mockOnSubmit} />);
    expect(screen.getByText('Basic Information')).toBeInTheDocument();
    expect(screen.getByText('Compensation')).toBeInTheDocument();
    expect(screen.getByText('Job Details')).toBeInTheDocument();
  });

  test('renders form fields', () => {
    render(<JobForm onSubmit={mockOnSubmit} />);
    expect(screen.getByLabelText('Job Title *')).toBeInTheDocument();
    expect(screen.getByLabelText('Department')).toBeInTheDocument();
    expect(screen.getByLabelText('Location *')).toBeInTheDocument();
  });

  test('shows publish button for new job', () => {
    render(<JobForm onSubmit={mockOnSubmit} />);
    expect(screen.getByText('Publish Job')).toBeInTheDocument();
  });

  test('shows update button for existing job', () => {
    render(<JobForm job={{ id: '1', title: 'Test' }} onSubmit={mockOnSubmit} />);
    expect(screen.getByText('Update Job')).toBeInTheDocument();
  });

  test('shows save as draft for new job', () => {
    render(<JobForm onSubmit={mockOnSubmit} />);
    expect(screen.getByText('Save as Draft')).toBeInTheDocument();
  });

  test('hides draft button for editing', () => {
    render(<JobForm job={{ id: '1', title: 'Test' }} onSubmit={mockOnSubmit} />);
    expect(screen.queryByText('Save as Draft')).not.toBeInTheDocument();
  });

  test('renders all job type options', () => {
    render(<JobForm onSubmit={mockOnSubmit} />);
    expect(screen.getByText('Location Type')).toBeInTheDocument();
    expect(screen.getByText('Job Type *')).toBeInTheDocument();
    expect(screen.getByText('Experience Level *')).toBeInTheDocument();
  });

  test('renders salary fields', () => {
    render(<JobForm onSubmit={mockOnSubmit} />);
    expect(screen.getByLabelText('Min Salary')).toBeInTheDocument();
    expect(screen.getByLabelText('Max Salary')).toBeInTheDocument();
  });

  test('renders description textarea', () => {
    render(<JobForm onSubmit={mockOnSubmit} />);
    expect(screen.getByLabelText('Job Description *')).toBeInTheDocument();
  });

  test('renders skills autocomplete', () => {
    render(<JobForm onSubmit={mockOnSubmit} />);
    expect(screen.getByText('Skills *')).toBeInTheDocument();
  });

  test('renders cancel button', () => {
    render(<JobForm onSubmit={mockOnSubmit} />);
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });
});
