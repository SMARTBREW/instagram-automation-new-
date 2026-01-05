/**
 * Centralized error handling utility
 * Provides retry logic, error categorization, and user-friendly error messages
 */

// Track consecutive failures to avoid immediate redirects
let consecutiveFailures = 0
const MAX_CONSECUTIVE_FAILURES = 3
const FAILURE_RESET_TIME = 60000 // Reset counter after 1 minute

let failureResetTimer = null

const resetFailureCounter = () => {
  consecutiveFailures = 0
  if (failureResetTimer) {
    clearTimeout(failureResetTimer)
    failureResetTimer = null
  }
}

const incrementFailureCounter = () => {
  consecutiveFailures++
  
  // Reset counter after a period of successful requests
  if (failureResetTimer) {
    clearTimeout(failureResetTimer)
  }
  failureResetTimer = setTimeout(resetFailureCounter, FAILURE_RESET_TIME)
}

export const shouldRedirectToLogin = (error, requestUrl) => {
  // Don't redirect on login/register endpoints
  const isAuthEndpoint = requestUrl?.includes('/auth/login') || 
                         requestUrl?.includes('/auth/register')
  
  if (isAuthEndpoint) {
    return false
  }

  // Check if user is authenticated
  const isAuthenticated = !!localStorage.getItem('accessToken')
  if (!isAuthenticated) {
    return false
  }

  // Categorize error
  const isNetworkError = 
    error.code === 'ECONNABORTED' || 
    error.message === 'Network Error' ||
    error.code === 'ERR_NETWORK' ||
    !error.response // No response means network issue

  const isServerError = error.response?.status >= 500 && error.response?.status < 600
  const isAuthError = error.response?.status === 401

  // Only redirect on critical errors after multiple failures
  if ((isNetworkError || isServerError || isAuthError) && consecutiveFailures >= MAX_CONSECUTIVE_FAILURES) {
    return true
  }

  // Increment failure counter for network/server errors
  if (isNetworkError || isServerError) {
    incrementFailureCounter()
  } else {
    // Reset on successful error handling (like 400, 404, etc.)
    resetFailureCounter()
  }

  return false
}

export const getErrorMessage = (error) => {
  if (error.response) {
    // Server responded with error
    const status = error.response.status
    const message = error.response?.data?.error?.message || 
                   error.response?.data?.message

    switch (status) {
      case 401:
        return 'Session expired. Please login again.'
      case 403:
        return 'You do not have permission to perform this action.'
      case 404:
        return 'The requested resource was not found.'
      case 429:
        return 'Too many requests. Please try again later.'
      case 500:
      case 502:
      case 503:
      case 504:
        return 'Server error. Please try again in a moment.'
      default:
        return message || `Server error (${status}). Please try again.`
    }
  } else if (error.code === 'ECONNABORTED') {
    return 'Request timed out. Please check your connection and try again.'
  } else if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
    return 'Network error. Please check your internet connection.'
  } else {
    return error.message || 'An unexpected error occurred. Please try again.'
  }
}

export const isRetryableError = (error) => {
  // Retry on network errors, timeouts, and server errors
  if (!error.response) {
    return true // Network error
  }
  
  const status = error.response.status
  // Retry on 5xx errors and 429 (rate limit)
  return (status >= 500 && status < 600) || status === 429
}

export const clearFailureCounter = () => {
  resetFailureCounter()
}

