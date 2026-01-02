import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, Send, User, Bot, MessageSquare } from 'lucide-react'
import { messageService } from '../services/messageService'
import { formatTime, formatRelativeTime } from '../utils/timeUtils'
import toast from 'react-hot-toast'

export default function Messages() {
  const { conversationId } = useParams()
  const navigate = useNavigate()
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
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
      console.error('Failed to load messages:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSend = async (e) => {
    e.preventDefault()
    if (!newMessage.trim() || sending) return

    setSending(true)
    try {
      const sentMessage = await messageService.sendMessage(conversationId, newMessage.trim())
      setMessages((prev) => [sentMessage, ...prev])
      setNewMessage('')
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
                            <p className="text-sm break-words">{message.text}</p>
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

            <motion.form
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              onSubmit={handleSend}
              className="bg-white rounded-xl shadow-lg p-4 flex gap-3"
            >
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
                disabled={!newMessage.trim() || sending}
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

