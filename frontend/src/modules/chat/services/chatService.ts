import api from '../../../lib/api'

export interface Chat {
  id: string
  title: string
  document_id: string | null
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  metadata: any
  created_at: string
}

export interface StreamChunk {
  token: string
  timestamp: number | null
  done: boolean
}

export const chatService = {
  async createChat(title?: string, documentId?: string): Promise<Chat> {
    const response = await api.post<Chat>('/chats', {
      title,
      document_id: documentId,
    })
    return response.data
  },

  async getChats(documentId?: string): Promise<Chat[]> {
    const params = documentId ? { document_id: documentId } : {}
    const response = await api.get<{ items: Chat[] }>('/chats', { params })
    return response.data.items
  },

  async getChat(chatId: string): Promise<Chat> {
    const response = await api.get<Chat>(`/chats/${chatId}`)
    return response.data
  },

  async deleteChat(chatId: string): Promise<void> {
    await api.delete(`/chats/${chatId}`)
  },

  async getMessages(chatId: string): Promise<Message[]> {
    const response = await api.get<{ messages: Message[] }>(`/chats/${chatId}/messages`)
    return response.data.messages
  },

  async *sendMessage(chatId: string, content: string): AsyncGenerator<StreamChunk, void, unknown> {
    const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/chats/${chatId}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      },
      body: JSON.stringify({ content }),
    })

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) throw new Error('No response body')

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          try {
            const parsed = JSON.parse(data) as StreamChunk
            yield parsed
            if (parsed.done) return
          } catch (e) {
            // Skip invalid JSON
          }
        }
      }
    }
  },
}
