import { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'

const INACTIVITY_TIMEOUT = 12 * 60 * 60 * 1000 // 12 hours in milliseconds
const LAST_ACTIVITY_KEY = 'lastActivityTime'

import { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { authService } from '../services/authService'

const INACTIVITY_TIMEOUT = 12 * 60 * 60 * 1000 // 12 hours in milliseconds
const LAST_ACTIVITY_KEY = 'lastActivityTime'

export const useInactivity = () => {
  const navigate = useNavigate()
  const timeoutRef = useRef(null)

  const updateLastActivity = () => {
    localStorage.setItem(LAST_ACTIVITY_KEY, Date.now().toString())
  }

  const checkInactivity = () => {
    // Only check if user is authenticated
    if (!authService.isAuthenticated()) {
      return
    }

    const lastActivity = localStorage.getItem(LAST_ACTIVITY_KEY)
    if (!lastActivity) {
      updateLastActivity()
      return
    }

    const timeSinceLastActivity = Date.now() - parseInt(lastActivity, 10)
    
    if (timeSinceLastActivity >= INACTIVITY_TIMEOUT) {
      // 12 hours of inactivity - redirect to home but keep session
      const currentPath = window.location.pathname
      if (currentPath !== '/') {
        navigate('/', { replace: true })
        // Update activity time so it doesn't keep redirecting
        updateLastActivity()
      }
    }
  }

  useEffect(() => {
    // Only track inactivity if user is authenticated
    if (!authService.isAuthenticated()) {
      return
    }

    // Initialize last activity time if not set
    if (!localStorage.getItem(LAST_ACTIVITY_KEY)) {
      updateLastActivity()
    }

    // Check inactivity every minute
    const interval = setInterval(checkInactivity, 60 * 1000)
    
    // Check immediately on mount
    checkInactivity()

    // Track user activity events
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click']
    
    const handleActivity = () => {
      // Only update if authenticated
      if (authService.isAuthenticated()) {
        updateLastActivity()
        // Clear existing timeout
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current)
        }
      }
    }

    // Add event listeners
    events.forEach(event => {
      window.addEventListener(event, handleActivity, { passive: true })
    })

    return () => {
      clearInterval(interval)
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
      events.forEach(event => {
        window.removeEventListener(event, handleActivity)
      })
    }
  }, [navigate])
}

