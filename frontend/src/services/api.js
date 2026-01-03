import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://instagram-automation-new.onrender.com'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout to prevent hanging requests
})

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    // Prevent infinite retry loops
    if (originalRequest._retry) {
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
      window.location.href = '/login'
      return Promise.reject(error)
    }

    // Only handle 401 for token refresh, not timeouts
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refreshToken')
      if (refreshToken) {
        originalRequest._retry = true
        try {
          const response = await axios.post(
            `${API_BASE_URL}/v1/auth/refresh-tokens`,
            { refreshToken },
            { timeout: 10000 } // 10 second timeout for refresh
          )
          const { access, refresh } = response.data.tokens
          localStorage.setItem('accessToken', access.token)
          localStorage.setItem('refreshToken', refresh.token)
          originalRequest.headers.Authorization = `Bearer ${access.token}`
          return api.request(originalRequest)
        } catch (refreshError) {
          // Token refresh failed - clear everything and redirect
          localStorage.removeItem('accessToken')
          localStorage.removeItem('refreshToken')
          localStorage.removeItem('user')
          localStorage.removeItem('lastActivityTime')
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      } else {
        // No refresh token - redirect to login
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
        localStorage.removeItem('user')
        localStorage.removeItem('lastActivityTime')
        window.location.href = '/login'
      }
    }
    
    // Handle network errors and timeouts
    if (error.code === 'ECONNABORTED' || error.message === 'Network Error') {
      // Don't redirect on timeout, just reject the promise
      // The component should handle the error
      return Promise.reject(error)
    }
    
    return Promise.reject(error)
  }
)

export default api

