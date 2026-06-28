import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
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
  const { theme, toggleTheme } = useTheme();

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
            setError('邮箱或密码错误');
            break;
          case 400:
            setError(axiosError.response.data?.error || '请求无效');
            break;
          default:
            setError('登录失败，请重试');
        }
      } else if (axiosError.request) {
        setError('网络错误，请检查网络连接');
      } else {
        setError('发生未知错误');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-logo-section">
        <div className="logo-wrapper">
          <h1 className="logo-title">BLackAnt</h1>
        </div>
      </div>
      <div className="auth-card">
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>邮箱</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="请输入邮箱"
            />
          </div>
          <div className="form-group">
            <label>密码</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="请输入密码"
            />
          </div>
          <button type="submit" disabled={isLoading}>
            {isLoading ? '登录中...' : '登录'}
          </button>
        </form>
        <p className="link-text">
          还没有账号？<button onClick={() => onNavigate('/register')}>注册</button>
        </p>
      </div>
      <button onClick={toggleTheme} className="theme-toggle-btn">
        {theme === 'light' ? '🌙' : '☀️'}
      </button>
    </div>
  );
};