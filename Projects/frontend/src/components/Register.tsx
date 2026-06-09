import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { register } from '../api/auth';
import type { AxiosError } from 'axios';
import type { ErrorResponse } from '../api/types';

interface RegisterProps {
  onNavigate: (path: string) => void;
}

export const Register = ({ onNavigate }: RegisterProps) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login: handleLogin } = useAuth();

  const validatePassword = (pwd: string): string | null => {
    if (pwd.length < 8) {
      return 'Password must be at least 8 characters';
    }
    if (!/[a-z]/.test(pwd)) {
      return 'Password must contain lowercase letters';
    }
    if (!/[A-Z]/.test(pwd)) {
      return 'Password must contain uppercase letters';
    }
    if (!/[0-9]/.test(pwd)) {
      return 'Password must contain numbers';
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    const passwordError = validatePassword(password);
    if (passwordError) {
      setError(passwordError);
      return;
    }

    setIsLoading(true);

    try {
      const response = await register(email, password);
      if (response.success) {
        handleLogin(response.data.token, {
          userId: response.data.userId,
          email: response.data.email,
        });
        onNavigate('/dashboard');
      }
    } catch (err) {
      const axiosError = err as AxiosError<ErrorResponse>;
      if (axiosError.response) {
        switch (axiosError.response.status) {
          case 409:
            setError('User already exists');
            break;
          case 400:
            setError(axiosError.response.data?.error || 'Invalid registration data');
            break;
          default:
            setError('Registration failed, please try again');
        }
      } else if (axiosError.request) {
        setError('Network error, please check your connection');
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Register</h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="Enter email"
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Enter password"
            />
          </div>
          <div className="form-group">
            <label>Confirm Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              placeholder="Confirm password"
            />
          </div>
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Registering...' : 'Register'}
          </button>
        </form>
        <p className="link-text">
          Already have an account? <button onClick={() => onNavigate('/login')}>Login</button>
        </p>
      </div>
    </div>
  );
};