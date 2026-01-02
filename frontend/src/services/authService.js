import api from './api'

export const authService = {
  async register(name, email, password) {
    const response = await api.post('/v1/auth/register', {
      name,
      email,
      password,
    })
    if (response.data.tokens) {
      localStorage.setItem('accessToken', response.data.tokens.access.token)
      localStorage.setItem('refreshToken', response.data.tokens.refresh.token)
      localStorage.setItem('user', JSON.stringify(response.data.user))
    }
    return response.data
  },

  async login(email, password) {
    const response = await api.post('/v1/auth/login', {
      email,
      password,
    })
    if (response.data.tokens) {
      localStorage.setItem('accessToken', response.data.tokens.access.token)
      localStorage.setItem('refreshToken', response.data.tokens.refresh.token)
      localStorage.setItem('user', JSON.stringify(response.data.user))
    }
    return response.data
  },

  async logout() {
    const refreshToken = localStorage.getItem('refreshToken')
    if (refreshToken) {
      try {
        await api.post('/v1/auth/logout', { refreshToken })
      } catch (error) {
        console.error('Logout error:', error)
      }
    }
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
  },

  getCurrentUser() {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  },

  isAuthenticated() {
    return !!localStorage.getItem('accessToken')
  },
}

