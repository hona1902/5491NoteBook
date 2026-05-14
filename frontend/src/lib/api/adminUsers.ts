import { apiClient } from './client'
import type { AppUser } from '@/lib/stores/auth-store'

export interface CreateUserRequest {
  username: string
  email: string
  password: string
  role?: string
}

export interface UpdateUserRequest {
  username?: string
  email?: string
  role?: string
  is_active?: boolean
}

export const adminUsersApi = {
  list: async (): Promise<AppUser[]> => {
    const response = await apiClient.get('/admin/users')
    return response.data
  },

  create: async (data: CreateUserRequest): Promise<AppUser> => {
    const response = await apiClient.post('/admin/users', data)
    return response.data
  },

  update: async (userId: string, data: UpdateUserRequest): Promise<AppUser> => {
    const response = await apiClient.patch(`/admin/users/${userId}`, data)
    return response.data
  },

  delete: async (userId: string): Promise<void> => {
    await apiClient.delete(`/admin/users/${userId}`)
  },

  resetPassword: async (userId: string, newPassword: string): Promise<void> => {
    await apiClient.patch(`/admin/users/${userId}/password`, null, {
      params: { new_password: newPassword },
    })
  },
}
