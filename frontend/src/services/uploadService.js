import api from './api'

export const uploadService = {
  async uploadImage(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/v1/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    
    return response.data
  },
}

