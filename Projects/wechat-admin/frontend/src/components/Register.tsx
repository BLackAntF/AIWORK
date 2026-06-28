import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
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
  const { theme, toggleTheme } = useTheme();

  const validatePassword = (pwd: string): string | null => {
    if (pwd.length < 8) {
      return '密码长度至少8个字符';
    }
    if (!/[a-z]/.test(pwd)) {
      return '密码必须包含小写字母';
    }
    if (!/[A-Z]/.test(pwd)) {
      return '密码必须包含大写字母';
    }
    if (!/[0-9]/.test(pwd)) {
      return '密码必须包含数字';
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('两次输入的密码不一致');
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
            setError('该邮箱已被注册');
            break;
          case 400:
            setError(axiosError.response.data?.error || '注册数据无效');
            break;
          default:
            setError('注册失败，请重试');
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
          <div className="form-group">
            <label>确认密码</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              placeholder="请再次输入密码"
            />
          </div>
          <button type="submit" disabled={isLoading}>
            {isLoading ? '注册中...' : '注册'}
          </button>
        </form>
        <p className="link-text">
          已有账号？<button onClick={() => onNavigate('/login')}>登录</button>
        </p>
      </div>
      <button onClick={toggleTheme} className="theme-toggle-btn">
        {theme === 'light' ? '🌙' : '☀️'}
      </button>
    </div>
  );
};