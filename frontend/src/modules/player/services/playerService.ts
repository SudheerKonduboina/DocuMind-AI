import api from '../../../lib/api'

export interface PlaybackSegment {
  start_time: number
  end_time: number
  transcript: string
  s3_url: string | null
}

export const playerService = {
  async getPlaybackSegment(documentId: string, timestamp: number, duration = 30): Promise<PlaybackSegment> {
    const response = await api.get<PlaybackSegment>(`/playback/${documentId}/segment`, {
      params: { timestamp, duration }
    })
    return response.data
  },

  async getMediaUrl(documentId: string): Promise<{ url: string }> {
    const response = await api.get<{ url: string }>(`/playback/${documentId}/url`)
    return response.data
  },
}
