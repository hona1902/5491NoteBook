import { apiClient } from './client'

export const authApi = {
  login: async (usernameOrEmail: string, password: string) => {
    const response = await apiClient.post('/auth/login', {
      username_or_email: usernameOrEmail,
      password,
    })
    return response.data
  },

  getMe: async () => {
    const response = await apiClient.get('/auth/me')
    return response.data
  },

  changePassword: async (currentPassword: string, newPassword: string) => {
    const response = await apiClient.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
    return response.data
  },

  logout: async () => {
    const response = await apiClient.post('/auth/logout')
    return response.data
  },
}
