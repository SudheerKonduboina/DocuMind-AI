import api from '../../../lib/api'

export interface Summary {
  id: string
  document_id: string
  user_id: string
  content: string
  summary_type: string
  created_at: string
  updated_at: string
}

export const summaryService = {
  async getSummary(documentId: string): Promise<Summary> {
    const response = await api.get<Summary>(`/summaries/${documentId}`)
    return response.data
  },

  async generateSummary(documentId: string): Promise<Summary> {
    const response = await api.post<Summary>(`/summaries/${documentId}`)
    return response.data
  },

  async regenerateSummary(documentId: string): Promise<Summary> {
    const response = await api.post<Summary>(`/summaries/${documentId}/regenerate`)
    return response.data
  },

  async deleteSummary(documentId: string): Promise<void> {
    await api.delete(`/summaries/${documentId}`)
  },
}
