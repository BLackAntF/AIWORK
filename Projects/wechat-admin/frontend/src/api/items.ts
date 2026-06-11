import api from './axios';
import type { ItemsResponse, ItemResponse, MessageResponse } from './types';

export const getItems = async (): Promise<ItemsResponse> => {
  const response = await api.get('/items');
  return response.data;
};

export const getItem = async (id: string): Promise<ItemResponse> => {
  const response = await api.get(`/items/${id}`);
  return response.data;
};

export const createItem = async (name: string, description?: string): Promise<ItemResponse> => {
  const response = await api.post('/items', { name, description });
  return response.data;
};

export const updateItem = async (id: string, name: string, description?: string): Promise<ItemResponse> => {
  const response = await api.put('/items', { id, name, description });
  return response.data;
};

export const deleteItem = async (id: string): Promise<MessageResponse> => {
  const response = await api.delete('/items', { params: { id } });
  return response.data;
};