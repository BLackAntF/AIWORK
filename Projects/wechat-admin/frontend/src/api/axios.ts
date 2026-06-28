import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:3000/api',
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

    // 401 - Token 过期，清除本地存储并跳转登录页
    if (response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
      console.error('登录已过期，请重新登录');
    }
    // 403 - 权限不足
    else if (response?.status === 403) {
      console.error('权限不足，请联系管理员');
    }
    // 404 - 资源不存在
    else if (response?.status === 404) {
      console.error('请求的资源不存在');
    }
    // 500 - 服务器错误
    else if (response?.status === 500) {
      console.error('服务器错误，请稍后再试');
    }
    // 网络错误（无 response）
    else if (!response && message) {
      console.error('网络连接失败，请检查网络');
    }
    // 其他未知错误
    else {
      console.error('请求失败：', error.message || '未知错误');
    }

    return Promise.reject(error);
  }
);

export default api;