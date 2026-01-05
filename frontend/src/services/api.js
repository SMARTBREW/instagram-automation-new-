import axios from 'axios'
import { shouldRedirectToLogin, clearFailureCounter } from '../utils/errorHandler'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://instagram-automation-new.onrender.com'

// Helper to check if user is authenticated (avoid circular dependency)
const isAuthenticated = () => {
  return !!localStorage.getItem('accessToken')
}

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

// Handle token refresh on 401 and redirect on critical errors
api.interceptors.response.use(
  (response) => {
    // Reset failure counter on successful response
    clearFailureCounter()
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    // Prevent infinite retry loops
    if (originalRequest._retry) {
      // Clear auth data and redirect to login
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
      localStorage.removeItem('lastActivityTime')
      // Store current route to redirect back after login
      const currentPath = window.location.pathname
      if (currentPath !== '/login' && currentPath !== '/register') {
        sessionStorage.setItem('redirectAfterLogin', currentPath)
      }
      window.location.href = '/login'
      return Promise.reject(error)
    }

    // Handle 401 - try to refresh token
    if (error.response?.status === 401) {
      // Don't try to refresh on login/register endpoints
      const isAuthEndpoint = originalRequest.url?.includes('/auth/login') || 
                             originalRequest.url?.includes('/auth/register')
      
      if (isAuthEndpoint) {
        // For login/register, just reject (let component handle it)
        return Promise.reject(error)
      }

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
          clearFailureCounter() // Reset on successful refresh
          return api.request(originalRequest)
        } catch (refreshError) {
          // Token refresh failed - clear everything and redirect
          localStorage.removeItem('accessToken')
          localStorage.removeItem('refreshToken')
          localStorage.removeItem('user')
          localStorage.removeItem('lastActivityTime')
          const currentPath = window.location.pathname
          if (currentPath !== '/login' && currentPath !== '/register') {
            sessionStorage.setItem('redirectAfterLogin', currentPath)
          }
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      } else {
        // No refresh token - redirect to login
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
        localStorage.removeItem('user')
        localStorage.removeItem('lastActivityTime')
        const currentPath = window.location.pathname
        if (currentPath !== '/login' && currentPath !== '/register') {
          sessionStorage.setItem('redirectAfterLogin', currentPath)
        }
        window.location.href = '/login'
        return Promise.reject(error)
      }
    }
    
    // Use smart error handler to decide if we should redirect
    if (shouldRedirectToLogin(error, originalRequest.url)) {
      // Multiple consecutive failures - backend is likely down
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
      localStorage.removeItem('lastActivityTime')
      const currentPath = window.location.pathname
      if (currentPath !== '/login' && currentPath !== '/register') {
        sessionStorage.setItem('redirectAfterLogin', currentPath)
      }
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

export default api

