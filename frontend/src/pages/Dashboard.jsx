import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { LogOut, Plus, Instagram, Users, MessageSquare, Shield, AlertCircle, RefreshCw } from 'lucide-react'
import { authService } from '../services/authService'
import { instagramService } from '../services/instagramService'
import AddAccountModal from '../components/AddAccountModal'
import { getErrorMessage, isRetryableError } from '../utils/errorHandler'
import toast from 'react-hot-toast'

export default function Dashboard() {
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [error, setError] = useState(null)
  const [retrying, setRetrying] = useState(false)
  const navigate = useNavigate()
  const user = authService.getCurrentUser()

  useEffect(() => {
    loadAccounts()
  }, [])

  const loadAccounts = async (showRetry = false) => {
    try {
      setError(null)
      setRetrying(showRetry)
      const data = await instagramService.getAccounts()
      setAccounts(data)
      setError(null) // Clear any previous errors
    } catch (error) {
      const errorMessage = getErrorMessage(error)
      setError({
        message: errorMessage,
        retryable: isRetryableError(error),
        originalError: error
      })
      
      // Only show toast for non-retryable errors or if not showing retry option
      if (!isRetryableError(error) || !showRetry) {
        toast.error(errorMessage)
      }
    } finally {
      setLoading(false)
      setRetrying(false)
    }
  }

  const handleRetry = () => {
    loadAccounts(true)
  }

  const handleLogout = async () => {
    await authService.logout()
    navigate('/login')
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-light via-primary-DEFAULT to-primary-light">
      <nav className="bg-white/80 backdrop-blur-md shadow-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <motion.div
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              className="flex items-center gap-2"
            >
              <Instagram className="w-8 h-8 text-primary-DEFAULT" />
              <span className="text-xl font-bold text-primary-dark">DM Automation</span>
            </motion.div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                {user?.role === 'admin' && (
                  <span className="flex items-center gap-1 px-2 py-1 bg-primary-DEFAULT text-primary-dark text-xs font-semibold rounded-full">
                    <Shield className="w-3 h-3" />
                    Admin
                  </span>
                )}
                <span className="text-sm text-gray-600">{user?.name}</span>
              </div>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 bg-primary-DEFAULT text-primary-dark rounded-lg hover:bg-primary-DEFAULT/90 transition"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </motion.button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-primary-dark mb-2">
            Instagram Accounts
          </h1>
          <p className="text-gray-700">
            {user?.role === 'admin' 
              ? 'View and manage all Instagram accounts from all users' 
              : 'Manage your connected Instagram business accounts'}
          </p>
        </motion.div>

        {error && error.retryable && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6 rounded-lg"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-yellow-400 mr-3" />
                <div>
                  <p className="text-sm font-medium text-yellow-800">
                    Connection issue detected
                  </p>
                  <p className="text-sm text-yellow-700 mt-1">
                    {error.message}
                  </p>
                </div>
              </div>
              <button
                onClick={handleRetry}
                disabled={retrying}
                className="ml-4 flex items-center gap-2 px-4 py-2 bg-yellow-400 text-yellow-900 rounded-lg hover:bg-yellow-500 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {retrying ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Retrying...
                  </>
                ) : (
                  <>
                    <RefreshCw className="w-4 h-4" />
                    Retry
                  </>
                )}
              </button>
            </div>
          </motion.div>
        )}

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="w-12 h-12 border-4 border-primary-DEFAULT border-t-transparent rounded-full animate-spin" />
          </div>
        ) : error && !error.retryable ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12 bg-white rounded-xl shadow-lg"
          >
            <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-primary-dark mb-2">
              Failed to load accounts
            </h3>
            <p className="text-gray-600 mb-6">{error.message}</p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleRetry}
              className="bg-primary-DEFAULT text-primary-dark px-6 py-3 rounded-lg font-semibold hover:bg-primary-DEFAULT/90 transition"
            >
              Try Again
            </motion.button>
          </motion.div>
        ) : (
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {accounts.map((account, index) => (
              <motion.div
                key={account.id}
                variants={itemVariants}
                whileHover={{ scale: 1.02, y: -5 }}
                className="bg-white rounded-xl shadow-lg p-6 cursor-pointer hover:shadow-xl transition relative"
                onClick={() => navigate(`/conversations/${account.id}`)}
              >
                {user?.role === 'admin' && account.userInfo && (
                  <div className="absolute top-3 right-3">
                    <span className="text-xs bg-primary-light text-primary-dark px-2 py-1 rounded-full font-medium">
                      {account.userInfo.name}
                    </span>
                  </div>
                )}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-primary-DEFAULT rounded-full flex items-center justify-center">
                      <Instagram className="w-6 h-6 text-primary-dark" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-primary-dark">
                        {account.username || 'Instagram Account'}
                      </h3>
                      <p className="text-sm text-gray-500">@{account.username || 'N/A'}</p>
                      {user?.role === 'admin' && account.userInfo && (
                        <p className="text-xs text-gray-400 mt-1">
                          Owner: {account.userInfo.name}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Users className="w-4 h-4" />
                    <span>{account.followersCount.toLocaleString()} followers</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <MessageSquare className="w-4 h-4" />
                    <span>View conversations</span>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <span
                    className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                      account.isActive
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {account.isActive ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </motion.div>
            ))}

            <motion.div
              variants={itemVariants}
              whileHover={{ scale: 1.02, y: -5 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setShowAddModal(true)}
              className="bg-white/50 border-2 border-dashed border-primary-DEFAULT rounded-xl p-6 cursor-pointer hover:bg-white/70 transition flex flex-col items-center justify-center min-h-[200px]"
            >
              <Plus className="w-12 h-12 text-primary-DEFAULT mb-4" />
              <p className="text-primary-dark font-semibold">Add Instagram Account</p>
              <p className="text-sm text-gray-600 mt-2">Connect a new account</p>
            </motion.div>
          </motion.div>
        )}

        {accounts.length === 0 && !loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <Instagram className="w-24 h-24 text-primary-DEFAULT mx-auto mb-4 opacity-50" />
            <h3 className="text-xl font-semibold text-primary-dark mb-2">
              No accounts connected
            </h3>
            <p className="text-gray-600 mb-6">Get started by connecting your first Instagram account</p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowAddModal(true)}
              className="bg-primary-DEFAULT text-primary-dark px-6 py-3 rounded-lg font-semibold hover:bg-primary-DEFAULT/90 transition"
            >
              <Plus className="w-5 h-5 inline mr-2" />
              Add Account
            </motion.button>
          </motion.div>
        )}
      </div>

      <AddAccountModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSuccess={loadAccounts}
      />
    </div>
  )
}

