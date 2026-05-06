import api from '../../../lib/api'

export interface Document {
  id: string
  title: string
  file_type: string
  file_size: number
  status: string
  created_at: string
  updated_at: string
}

export const mediaService = {
  async getDocuments(page = 1, limit = 20, fileType?: string) {
    const params: any = { page, limit }
    if (fileType) params.file_type = fileType
    const response = await api.get('/documents', { params })
    return response.data
  },

  async getDocument(id: string): Promise<Document> {
    const response = await api.get<Document>(`/documents/${id}`)
    return response.data
  },

  async deleteDocument(id: string): Promise<void> {
    await api.delete(`/documents/${id}`)
  },
}
