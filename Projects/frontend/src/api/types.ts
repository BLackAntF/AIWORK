export interface User {
  userId: string;
  email: string;
  role?: string;
}

export interface AuthResponse {
  success: boolean;
  data: {
    userId: string;
    email: string;
    role?: string;
    token: string;
  };
}

export interface UserResponse {
  success: boolean;
  data: User;
}

export interface Item {
  id: string;
  name: string;
  description?: string;
  created_at?: string;
}

export interface ItemsResponse {
  success: boolean;
  data: Item[];
}

export interface ItemResponse {
  success: boolean;
  data: Item;
}

export interface MessageResponse {
  success: boolean;
  message: string;
}

export interface ErrorResponse {
  success: boolean;
  error: string;
}