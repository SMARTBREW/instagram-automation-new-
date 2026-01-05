/**
 * Health check utility to keep Render service awake
 * Pings the health endpoint periodically to prevent cold starts
 */

const HEALTH_CHECK_INTERVAL = 5 * 60 * 1000 // 5 minutes
const HEALTH_CHECK_URL = `${import.meta.env.VITE_API_URL || 'https://instagram-automation-new.onrender.com'}/health-check`

let healthCheckInterval = null
let isChecking = false

export const startHealthCheck = () => {
  // Only start if not already running
  if (healthCheckInterval) {
    return
  }

  // Initial check to wake up the service
  pingHealthCheck()

  // Then ping every 5 minutes to keep it awake
  healthCheckInterval = setInterval(() => {
    pingHealthCheck()
  }, HEALTH_CHECK_INTERVAL)
}

export const stopHealthCheck = () => {
  if (healthCheckInterval) {
    clearInterval(healthCheckInterval)
    healthCheckInterval = null
  }
}

const pingHealthCheck = async () => {
  // Don't ping if already checking
  if (isChecking) {
    return
  }

  try {
    isChecking = true
    // Use fetch with short timeout - we just want to wake up the service
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5000) // 5 second timeout for health check
    
    await fetch(HEALTH_CHECK_URL, {
      method: 'GET',
      signal: controller.signal,
      cache: 'no-cache',
    })
    
    clearTimeout(timeoutId)
  } catch (error) {
    // Silently fail - health check is just to keep service awake
    // Don't show errors to user
    console.debug('Health check ping failed (this is normal):', error.message)
  } finally {
    isChecking = false
  }
}

