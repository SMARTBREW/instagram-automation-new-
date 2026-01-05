import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useEffect } from 'react'
import { authService } from './services/authService'
import { useInactivity } from './hooks/useInactivity'
import { startHealthCheck, stopHealthCheck } from './utils/healthCheck'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Conversations from './pages/Conversations'
import Messages from './pages/Messages'
import './styles/index.css'

function PrivateRoute({ children }) {
  return authService.isAuthenticated() ? children : <Navigate to="/login" />
}

function AppContent() {
  // Track inactivity (hook always called, but only tracks if authenticated)
  useInactivity()

  // Start health check pings to keep Render service awake
  useEffect(() => {
    startHealthCheck()
    return () => {
      stopHealthCheck()
    }
  }, [])

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/conversations/:accountId"
        element={
          <PrivateRoute>
            <Conversations />
          </PrivateRoute>
        }
      />
      <Route
        path="/messages/:conversationId"
        element={
          <PrivateRoute>
            <Messages />
          </PrivateRoute>
        }
      />
    </Routes>
  )
}

function App() {
  return (
    <Router>
      <Toaster position="top-right" />
      <AppContent />
    </Router>
  )
}

export default App

