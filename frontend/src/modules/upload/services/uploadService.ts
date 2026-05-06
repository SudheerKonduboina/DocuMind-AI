import api from '../../../lib/api'

export interface UploadResponse {
  id: string
  title: string
  file_type: string
  file_size: number
  status: string
  created_at: string
}

export const uploadService = {
  async uploadFile(file: File, title?: string): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    if (title) {
      formData.append('title', title)
    }

    const response = await api.post<UploadResponse>('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
}
