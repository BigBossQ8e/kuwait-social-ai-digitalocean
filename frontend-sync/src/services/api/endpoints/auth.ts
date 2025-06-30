// Authentication API endpoints using centralized API client
import api from '../apiClient';
import type { LoginCredentials, RegisterData, AuthResponse, User } from '../types/auth';

export const authApi = {
  // Login user
  login: (credentials: LoginCredentials) =>
    api.post<AuthResponse>('/auth/login', credentials),

  // Register new user
  register: (data: RegisterData) =>
    api.post<AuthResponse>('/auth/register', data),

  // Refresh access token
  refreshToken: (refreshToken: string) =>
    api.post<AuthResponse>('/auth/refresh', { refresh_token: refreshToken }),

  // Logout user
  logout: () =>
    api.post('/auth/logout'),

  // Get current user profile
  getCurrentUser: () =>
    api.get<User>('/auth/me'),

  // Update user profile
  updateProfile: (data: Partial<User>) =>
    api.put<User>('/auth/profile', data),

  // Change password
  changePassword: (currentPassword: string, newPassword: string) =>
    api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    }),

  // Request password reset
  requestPasswordReset: (email: string) =>
    api.post('/auth/forgot-password', { email }),

  // Reset password with token
  resetPassword: (token: string, newPassword: string) =>
    api.post('/auth/reset-password', {
      token,
      new_password: newPassword,
    }),

  // Verify email with token
  verifyEmail: (token: string) =>
    api.post('/auth/verify-email', { token }),

  // Resend verification email
  resendVerificationEmail: () =>
    api.post('/auth/resend-verification'),
};