import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import LoginPage from '@/pages/auth/login';
import { useAuth } from '@/hooks/useAuth';

jest.mock('@/hooks/useAuth');

jest.mock('react-hook-form', () => ({
  useForm: jest.fn(() => ({
    register: jest.fn(() => ({})),
    handleSubmit: jest.fn((fn) => (e) => { e?.preventDefault?.(); fn({ email: 'test@test.com', password: 'password' }); }),
    formState: { errors: {} },
  })),
}));

jest.mock('@hookform/resolvers/yup', () => ({
  yupResolver: jest.fn(() => () => ({})),
}));

jest.mock('@/utils/validators', () => ({
  loginSchema: {},
}));

describe('LoginPage', () => {
  const mockLogin = jest.fn();

  beforeEach(() => {
    mockLogin.mockClear();
    useAuth.mockReturnValue({
      login: mockLogin,
      loading: false,
    });
  });

  test('renders login page elements', () => {
    render(<LoginPage />);
    expect(screen.getByText('Welcome Back')).toBeInTheDocument();
    expect(screen.getByText('Sign in to your employer account')).toBeInTheDocument();
    expect(screen.getByText('Sign In')).toBeInTheDocument();
  });

  test('renders email field', () => {
    render(<LoginPage />);
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
  });

  test('renders password field', () => {
    render(<LoginPage />);
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
  });

  test('renders forgot password link', () => {
    render(<LoginPage />);
    expect(screen.getByText('Forgot password?')).toBeInTheDocument();
  });

  test('renders social login buttons', () => {
    render(<LoginPage />);
    expect(screen.getByText('Google')).toBeInTheDocument();
    expect(screen.getByText('LinkedIn')).toBeInTheDocument();
  });

  test('renders sign up link', () => {
    render(<LoginPage />);
    expect(screen.getByText('Create Account')).toBeInTheDocument();
  });

  test('submits form on button click', async () => {
    render(<LoginPage />);
    fireEvent.click(screen.getByText('Sign In'));
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({ email: 'test@test.com', password: 'password' });
    });
  });

  test('disables button when loading', () => {
    useAuth.mockReturnValue({
      login: mockLogin,
      loading: true,
    });
    render(<LoginPage />);
    expect(screen.getByText('Sign In')).toBeDisabled();
  });

  test('toggles password visibility', () => {
    render(<LoginPage />);
    const toggleBtn = screen.getByRole('button', { name: '' });
    fireEvent.click(toggleBtn);
  });
});
