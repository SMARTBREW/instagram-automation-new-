import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Instagram } from 'lucide-react'
import { instagramService } from '../services/instagramService'
import toast from 'react-hot-toast'

export default function AddAccountModal({ isOpen, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    pageId: '',
    instagramBusinessId: '',
    pageAccessToken: '',
    username: '',
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      await instagramService.createAccount(formData)
      toast.success('Instagram account connected!')
      onSuccess()
      onClose()
      setFormData({
        pageId: '',
        instagramBusinessId: '',
        pageAccessToken: '',
        username: '',
      })
    } catch (error) {
      toast.error(error.response?.data?.error?.message || 'Failed to connect account')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <Instagram className="w-6 h-6 text-primary-DEFAULT" />
              <h2 className="text-2xl font-bold text-primary-dark">Connect Instagram</h2>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Page ID *
              </label>
              <input
                type="text"
                value={formData.pageId}
                onChange={(e) => setFormData({ ...formData, pageId: e.target.value })}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-DEFAULT focus:border-transparent outline-none"
                placeholder="123456789"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Instagram Business ID *
              </label>
              <input
                type="text"
                value={formData.instagramBusinessId}
                onChange={(e) => setFormData({ ...formData, instagramBusinessId: e.target.value })}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-DEFAULT focus:border-transparent outline-none"
                placeholder="987654321"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Page Access Token *
              </label>
              <input
                type="text"
                value={formData.pageAccessToken}
                onChange={(e) => setFormData({ ...formData, pageAccessToken: e.target.value })}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-DEFAULT focus:border-transparent outline-none"
                placeholder="EAABwzLix..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Username (Optional)
              </label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-DEFAULT focus:border-transparent outline-none"
                placeholder="instagram_handle"
              />
            </div>

            <div className="flex gap-3 pt-4">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                Cancel
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                type="submit"
                disabled={loading}
                className="flex-1 px-4 py-2 bg-primary-DEFAULT text-primary-dark rounded-lg font-semibold hover:bg-primary-DEFAULT/90 transition disabled:opacity-50"
              >
                {loading ? 'Connecting...' : 'Connect'}
              </motion.button>
            </div>
          </form>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}

