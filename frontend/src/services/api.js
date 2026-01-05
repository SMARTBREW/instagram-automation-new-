import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://instagram-automation-new.onrender.com'

// Helper to check if user is authenticated (avoid circular dependency)
const isAuthenticated = () => {
  return !!localStorage.getItem('accessToken')
}

// Helper to clear auth and redirect to login
const redirectToLogin = (saveRoute = true) => {
  localStorage.removeItem('accessToken')
  localStorage.removeItem('refreshToken')
  localStorage.removeItem('user')
  localStorage.removeItem('lastActivityTime')
  
  // Save current route to redirect back after login
  if (saveRoute) {
    const currentPath = window.location.pathname
    if (currentPath !== '/login' && currentPath !== '/register') {
      sessionStorage.setItem('redirectAfterLogin', currentPath)
    }
  }
  
  window.location.href = '/login'
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 second timeout to allow for Render cold start (30s) + request processing
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

// Handle token refresh on 401 and redirect on timeouts/network errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    // Prevent infinite retry loops
    if (originalRequest._retry) {
      redirectToLogin()
      return Promise.reject(error)
    }

    // Don't redirect on login/register endpoints
    const isAuthEndpoint = originalRequest.url?.includes('/auth/login') || 
                           originalRequest.url?.includes('/auth/register')
    
    // Handle 401 - try to refresh token
    if (error.response?.status === 401) {
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
          return api.request(originalRequest)
        } catch (refreshError) {
          // Token refresh failed - redirect to login
          redirectToLogin()
          return Promise.reject(refreshError)
        }
      } else {
        // No refresh token - redirect to login
        redirectToLogin()
        return Promise.reject(error)
      }
    }
    
    // Handle timeouts and network errors - redirect immediately on first timeout
    if (
      error.code === 'ECONNABORTED' || 
      error.message === 'Network Error' ||
      error.code === 'ERR_NETWORK' ||
      (error.response?.status >= 500 && error.response?.status < 600)
    ) {
      // Only redirect if user is authenticated and not on auth pages
      if (!isAuthEndpoint && isAuthenticated()) {
        // Show helpful message about Render cold start
        if (error.code === 'ECONNABORTED' || error.code === 'ERR_NETWORK') {
          console.warn('Request timed out - Render service may be waking up from sleep. This is normal on free tier.')
        }
        redirectToLogin()
      }
      return Promise.reject(error)
    }
    
    return Promise.reject(error)
  }
)

export default api

