import api from './api'

export const messageService = {
  async getConversations(accountId, limit = 20, skip = 0) {
    const response = await api.get(`/v1/conversations/${accountId}`, {
      params: { limit, skip },
    })
    return response.data
  },

  async getConversationDetail(conversationId) {
    const response = await api.get(`/v1/conversations/detail/${conversationId}`)
    return response.data
  },

  async getMessages(conversationId, limit = 50, skip = 0) {
    const response = await api.get(`/v1/messages/${conversationId}`, {
      params: { limit, skip },
    })
    return response.data
  },

  async sendMessage(conversationId, text, attachment = null) {
    const response = await api.post(`/v1/messages/${conversationId}`, {
      text,
      attachment,
    })
    return response.data
  },

  async markAsRead(conversationId) {
    await api.post(`/v1/messages/${conversationId}/read`)
  },
}

