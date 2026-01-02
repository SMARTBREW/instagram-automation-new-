import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, Send, User, Bot, MessageSquare, Image as ImageIcon, X } from 'lucide-react'
import { messageService } from '../services/messageService'
import { uploadService } from '../services/uploadService'
import { formatTime, formatRelativeTime } from '../utils/timeUtils'
import toast from 'react-hot-toast'

export default function Messages() {
  const { conversationId } = useParams()
  const navigate = useNavigate()
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [selectedImage, setSelectedImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const fileInputRef = useRef(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    loadMessages()
    const interval = setInterval(loadMessages, 5000) // Poll every 5 seconds
    return () => clearInterval(interval)
  }, [conversationId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadMessages = async () => {
    try {
      const data = await messageService.getMessages(conversationId)
      setMessages(data.messages || [])
    } catch (error) {
      // Don't show toast for timeout errors during polling to avoid spam
      if (error.code === 'ECONNABORTED' || error.message === 'Network Error') {
        console.warn('Request timed out during polling')
      } else if (error.response?.status === 401) {
        // Token expired - will be handled by interceptor
        console.warn('Session expired')
      } else {
        console.error('Failed to load messages:', error)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleImageSelect = (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast.error('Please select an image file')
      return
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('Image size should be less than 10MB')
      return
    }

    setSelectedImage(file)
    
    // Create preview
    const reader = new FileReader()
    reader.onloadend = () => {
      setImagePreview(reader.result)
    }
    reader.readAsDataURL(file)
  }

  const removeImage = () => {
    setSelectedImage(null)
    setImagePreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const uploadImageToUrl = async (file) => {
    try {
      // Upload to Cloudinary via backend
      const result = await uploadService.uploadImage(file)
      return result.url
    } catch (error) {
      toast.error(error.response?.data?.error?.message || 'Failed to upload image')
      throw error
    }
  }

  const handleSend = async (e) => {
    e.preventDefault()
    if ((!newMessage.trim() && !selectedImage) || sending) return

    setSending(true)
    try {
      let attachment = null
      
      // Handle image upload
      if (selectedImage) {
        const imageUrl = await uploadImageToUrl(selectedImage)
        attachment = {
          type: 'image',
          url: imageUrl
        }
      }

      const sentMessage = await messageService.sendMessage(
        conversationId, 
        newMessage.trim() || null,
        attachment
      )
      setMessages((prev) => [sentMessage, ...prev])
      setNewMessage('')
      removeImage()
      toast.success('Message sent!')
    } catch (error) {
      toast.error(error.response?.data?.error?.message || 'Failed to send message')
    } finally {
      setSending(false)
    }
  }


  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-light via-primary-DEFAULT to-primary-light flex flex-col">
      <div className="bg-white/80 backdrop-blur-md shadow-lg sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-primary-dark hover:text-primary-DEFAULT transition mb-2"
          >
            <ArrowLeft className="w-5 h-5" />
            Back
          </button>
        </div>
      </div>

      <div className="flex-1 max-w-4xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6 flex flex-col">
        {loading ? (
          <div className="flex justify-center items-center h-full">
            <div className="w-12 h-12 border-4 border-primary-DEFAULT border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <>
            <div className="flex-1 overflow-y-auto mb-4 space-y-4 pb-4">
              <AnimatePresence>
                {messages.length === 0 ? (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-center py-12"
                  >
                    <MessageSquare className="w-16 h-16 text-primary-DEFAULT mx-auto mb-4 opacity-50" />
                    <p className="text-gray-600">No messages yet. Start the conversation!</p>
                  </motion.div>
                ) : (
                  [...messages].reverse().map((message, index) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className={`flex ${message.sender === 'page' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${
                          message.sender === 'page'
                            ? 'bg-primary-DEFAULT text-primary-dark'
                            : 'bg-white text-gray-800'
                        } shadow-md`}
                      >
                        <div className="flex items-start gap-2">
                          {message.sender === 'user' ? (
                            <User className="w-5 h-5 mt-0.5 flex-shrink-0" />
                          ) : (
                            <Bot className="w-5 h-5 mt-0.5 flex-shrink-0" />
                          )}
                          <div className="flex-1">
                            {/* Display text if available */}
                            {message.text && (
                              <p className="text-sm break-words mb-2">{message.text}</p>
                            )}
                            
                            {/* Display attachments (images) */}
                            {message.attachments && message.attachments.length > 0 && (
                              <div className="space-y-2 mb-2">
                                {message.attachments.map((attachment, idx) => (
                                  <div key={idx} className="rounded-lg overflow-hidden">
                                    {attachment.type === 'image' && (
                                      <>
                                        <img
                                          src={attachment.url}
                                          alt="Attachment"
                                          className="max-w-full h-auto max-h-64 rounded-lg cursor-pointer hover:opacity-90 transition object-contain"
                                          onClick={() => window.open(attachment.url, '_blank')}
                                          onError={(e) => {
                                            e.target.style.display = 'none'
                                            const fallback = e.target.nextElementSibling
                                            if (fallback) fallback.style.display = 'block'
                                          }}
                                        />
                                        <div className="hidden p-2 bg-gray-100 rounded text-sm text-center">
                                          Failed to load image
                                        </div>
                                      </>
                                    )}
                                    {attachment.type !== 'image' && (
                                      <div className="p-2 bg-gray-100 rounded text-sm">
                                        {attachment.type} attachment
                                      </div>
                                    )}
                                  </div>
                                ))}
                              </div>
                            )}
                            
                            <p
                              className={`text-xs mt-1 ${
                                message.sender === 'page'
                                  ? 'text-primary-dark/70'
                                  : 'text-gray-500'
                              }`}
                            >
                              {formatRelativeTime(message.timestamp || message.createdAt)}
                            </p>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))
                )}
              </AnimatePresence>
              <div ref={messagesEndRef} />
            </div>

            {/* Image Preview */}
            {imagePreview && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white rounded-xl shadow-lg p-4 mb-4 relative"
              >
                <button
                  onClick={removeImage}
                  className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition"
                >
                  <X className="w-4 h-4" />
                </button>
                <img
                  src={imagePreview}
                  alt="Preview"
                  className="max-w-xs max-h-48 rounded-lg"
                />
              </motion.div>
            )}

            <motion.form
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              onSubmit={handleSend}
              className="bg-white rounded-xl shadow-lg p-4 flex gap-3"
            >
              <input
                type="file"
                ref={fileInputRef}
                accept="image/*"
                onChange={handleImageSelect}
                className="hidden"
              />
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="bg-gray-100 text-gray-700 px-4 py-3 rounded-lg hover:bg-gray-200 transition flex items-center gap-2"
                disabled={sending}
              >
                <ImageIcon className="w-5 h-5" />
              </motion.button>

              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type a message..."
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-DEFAULT focus:border-transparent outline-none"
                disabled={sending}
              />
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                type="submit"
                disabled={(!newMessage.trim() && !selectedImage) || sending}
                className="bg-primary-DEFAULT text-primary-dark px-6 py-3 rounded-lg font-semibold hover:bg-primary-DEFAULT/90 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {sending ? (
                  <div className="w-5 h-5 border-2 border-primary-dark border-t-transparent rounded-full animate-spin" />
                ) : (
                  <>
                    <Send className="w-5 h-5" />
                    Send
                  </>
                )}
              </motion.button>
            </motion.form>
          </>
        )}
      </div>
    </div>
  )
}

