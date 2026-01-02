import api from './api'

export const instagramService = {
  async getAccounts() {
    const response = await api.get('/v1/instagram')
    return response.data
  },

  async createAccount(data) {
    const response = await api.post('/v1/instagram', data)
    return response.data
  },

  async getAccount(accountId) {
    const response = await api.get(`/v1/instagram/${accountId}`)
    return response.data
  },

  async updateAccount(accountId, data) {
    const response = await api.patch(`/v1/instagram/${accountId}`, data)
    return response.data
  },

  async deleteAccount(accountId) {
    await api.delete(`/v1/instagram/${accountId}`)
  },

  async getProfile(accountId) {
    const response = await api.get(`/v1/instagram/${accountId}/profile`)
    return response.data
  },
}

