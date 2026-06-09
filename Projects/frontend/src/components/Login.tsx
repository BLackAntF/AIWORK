import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { login } from '../api/auth';
import type { AxiosError } from 'axios';
import type { ErrorResponse } from '../api/types';

interface LoginProps {
  onNavigate: (path: string) => void;
}

export const Login = ({ onNavigate }: LoginProps) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login: handleLogin } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await login(email, password);
      if (response.success) {
        handleLogin(response.data.token, {
          userId: response.data.userId,
          email: response.data.email,
          role: response.data.role,
        });
        onNavigate('/dashboard');
      }
    } catch (err) {
      const axiosError = err as AxiosError<ErrorResponse>;
      if (axiosError.response) {
        switch (axiosError.response.status) {
          case 401:
            setError('Invalid email or password');
            break;
          case 400:
            setError(axiosError.response.data?.error || 'Invalid request');
            break;
          default:
            setError('Login failed, please try again');
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
        <h2>Login</h2>
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
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        <p className="link-text">
          Don't have an account? <button onClick={() => onNavigate('/register')}>Register</button>
        </p>
      </div>
    </div>
  );
};