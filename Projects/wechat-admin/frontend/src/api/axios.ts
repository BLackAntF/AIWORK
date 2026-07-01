import axios from 'axios';
import { logger } from '../utils/logger';

const DEFAULT_API_BASE_URL = 'http://localhost:3000/api';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const { response, message } = error;

    if (response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
      logger.error('登录已过期，请重新登录');
    } else if (response?.status === 403) {
      logger.error('权限不足，请联系管理员');
    } else if (response?.status === 404) {
      logger.error('请求的资源不存在');
    } else if (response?.status === 500) {
      logger.error('服务器错误，请稍后再试');
    } else if (!response && message) {
      logger.error('网络连接失败，请检查网络');
    } else {
      logger.error('请求失败：', error.message || '未知错误');
    }

    return Promise.reject(error);
  }
);

export default api;