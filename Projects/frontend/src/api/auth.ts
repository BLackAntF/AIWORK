import api from './axios';
import type { AuthResponse, UserResponse } from './types';

export const register = async (email: string, password: string): Promise<AuthResponse> => {
  const response = await api.post('/auth/register', { email, password });
  return response.data;
};

export const login = async (email: string, password: string): Promise<AuthResponse> => {
  const response = await api.post('/auth/login', { email, password });
  return response.data;
};

export const getCurrentUser = async (): Promise<UserResponse> => {
  const response = await api.get('/auth/me');
  return response.data;
};