/**
 * Get current time in IST
 */
const getCurrentIST = () => {
  const now = new Date()
  return new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }))
}

/**
 * Convert UTC timestamp to IST Date object
 */
const convertToIST = (utcTimestamp) => {
  if (!utcTimestamp) return null
  const date = new Date(utcTimestamp)
  // Get IST time by formatting and parsing
  const istString = date.toLocaleString('en-US', { timeZone: 'Asia/Kolkata' })
  return new Date(istString)
}

/**
 * Format timestamp as relative time (e.g., "1 min ago", "5h ago")
 * Handles UTC timestamps from backend and calculates relative time correctly
 */
export const formatRelativeTime = (timestamp) => {
  if (!timestamp) return ''
  
  try {
    // Ensure timestamp has 'Z' suffix if it's UTC (backend should send this, but handle both cases)
    let timestampStr = timestamp
    if (timestampStr && !timestampStr.endsWith('Z') && !timestampStr.includes('+') && !timestampStr.includes('-', 10)) {
      // If it's an ISO string without timezone, assume UTC and add Z
      timestampStr = timestampStr + 'Z'
    }
    
    // Parse the timestamp - backend sends ISO format strings
    const date = new Date(timestampStr)
    
    // Check if date is valid
    if (isNaN(date.getTime())) {
      console.error('Invalid timestamp:', timestamp, timestampStr)
      return ''
    }
    
    const now = new Date()
    
    // Calculate difference in milliseconds
    const diff = now.getTime() - date.getTime()
    
    // Handle negative differences (future dates)
    if (diff < 0) {
      return 'Just now'
    }
    
    const seconds = Math.floor(diff / 1000)
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)
    const weeks = Math.floor(days / 7)
    const months = Math.floor(days / 30)
    const years = Math.floor(days / 365)

    if (seconds < 10) return 'Just now'
    if (seconds < 60) return `${seconds}s ago`
    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    if (days < 7) return `${days}d ago`
    if (weeks < 4) return `${weeks}w ago`
    if (months < 12) return `${months}mo ago`
    if (years < 1) return `${months}mo ago`
    return `${years}y ago`
  } catch (error) {
    console.error('Error formatting relative time:', error, timestamp)
    return ''
  }
}

/**
 * Format timestamp as time in IST (e.g., "2:30 PM")
 */
export const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  
  return date.toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
    timeZone: 'Asia/Kolkata'
  })
}

/**
 * Format timestamp as date and time in IST
 */
export const formatDateTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  
  return date.toLocaleString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
    timeZone: 'Asia/Kolkata'
  })
}

