import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { LogIn, Mail, Lock, Instagram } from 'lucide-react'
import { authService } from '../services/authService'
import toast from 'react-hot-toast'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      await authService.login(email, password)
      toast.success('Login successful!')
      navigate('/')
    } catch (error) {
      // Better error handling for different error types
      let errorMessage = 'Login failed'
      
      if (error.response) {
        // Server responded with error
        errorMessage = error.response?.data?.error?.message || 
                      error.response?.data?.message || 
                      `Server error: ${error.response.status}`
      } else if (error.request) {
        // Request was made but no response received
        errorMessage = 'Network error. Please check your connection and try again.'
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = 'Request timed out. Please try again.'
      } else {
        errorMessage = error.message || 'Login failed'
      }
      
      console.error('Login error:', error)
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <motion.div
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: 'spring' }}
          className="bg-white rounded-2xl shadow-2xl p-8"
        >
          <div className="text-center mb-8">
            <motion.div
              initial={{ rotate: -180 }}
              animate={{ rotate: 0 }}
              transition={{ delay: 0.3, type: 'spring' }}
              className="inline-block mb-4"
            >
              <Instagram className="w-16 h-16 text-primary-DEFAULT mx-auto" />
            </motion.div>
            <h1 className="text-3xl font-bold text-primary-dark mb-2">
              Welcome Back
            </h1>
            <p className="text-gray-600">Sign in to manage your Instagram DMs</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
            >
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-DEFAULT focus:border-transparent outline-none transition"
                  placeholder="your@email.com"
                />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
            >
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-DEFAULT focus:border-transparent outline-none transition"
                  placeholder="••••••••"
                />
              </div>
            </motion.div>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={loading}
              className="w-full bg-primary-DEFAULT text-primary-dark font-semibold py-3 rounded-lg hover:bg-primary-DEFAULT/90 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-primary-dark border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <LogIn className="w-5 h-5" />
                  Sign In
                </>
              )}
            </motion.button>
          </form>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="mt-6 text-center text-sm text-gray-600"
          >
            Don't have an account?{' '}
            <Link to="/register" className="text-primary-DEFAULT font-semibold hover:underline">
              Sign up
            </Link>
          </motion.p>
        </motion.div>
      </motion.div>
    </div>
  )
}

