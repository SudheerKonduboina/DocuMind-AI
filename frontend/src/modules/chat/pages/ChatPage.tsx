import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { Send, Plus, Trash2, Sparkles, User, Bot, Paperclip, ChevronLeft, Search, MessageSquarePlus } from 'lucide-react'
import { chatService, Chat, Message } from '../services/chatService'
import { useAuthStore } from '../../auth/store/authStore'

export default function ChatPage() {
  const { chatId } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const user = useAuthStore((state) => state.user)
  
  const [chats, setChats] = useState<Chat[]>([])
  const [currentChat, setCurrentChat] = useState<Chat | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [streaming, setStreaming] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadChats()
    if (chatId) {
      loadChat(chatId)
    } else if (location.state?.documentId) {
      createNewChat(location.state.documentId)
    }
  }, [chatId, location.state])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadChats = async () => {
    try {
      const data = await chatService.getChats()
      setChats(data)
    } catch (error) {
      console.error('Failed to load chats:', error)
    }
  }

  const loadChat = async (id: string) => {
    setLoading(true)
    try {
      const [chat, msgs] = await Promise.all([
        chatService.getChat(id),
        chatService.getMessages(id),
      ])
      setCurrentChat(chat)
      setMessages(msgs)
    } catch (error) {
      console.error('Failed to load chat:', error)
      navigate('/chat')
    } finally {
      setLoading(false)
    }
  }

  const createNewChat = async (documentId?: string) => {
    try {
      const title = documentId ? 'Knowledge Extraction' : 'Untitled Stream'
      const newChat = await chatService.createChat(title, documentId)
      navigate(`/chat/${newChat.id}`, { replace: true })
      loadChats()
    } catch (error) {
      console.error('Failed to create chat:', error)
    }
  }

  const deleteChat = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!confirm('Discard this session?')) return
    try {
      await chatService.deleteChat(id)
      if (currentChat?.id === id) {
        navigate('/chat')
      }
      loadChats()
    } catch (error) {
      console.error('Failed to delete chat:', error)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || !currentChat || streaming) return

    const userMessage = input.trim()
    setInput('')
    setStreaming(true)

    const tempUserMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: userMessage,
      metadata: null,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, tempUserMessage])

    const tempAssistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '',
      metadata: null,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, tempAssistantMessage])

    try {
      let fullResponse = ''
      for await (const chunk of chatService.sendMessage(currentChat.id, userMessage)) {
        if (chunk.token) {
          fullResponse += chunk.token
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === tempAssistantMessage.id
                ? { ...msg, content: fullResponse }
                : msg
            )
          )
        }
        if (chunk.done) {
          setStreaming(false)
        }
      }
    } catch (error) {
      console.error('Failed to send message:', error)
      setStreaming(false)
    }
  }

  return (
    <div className="flex h-[calc(100vh-5rem)] relative overflow-hidden bg-luxury-cream/50 dark:bg-luxury-dark/50 border-t border-luxury-dark/5 dark:border-white/5 backdrop-blur-3xl">
      {/* Immersive Sidebar */}
      <aside className="w-80 border-r border-luxury-dark/5 dark:border-white/5 flex flex-col bg-white/20 dark:bg-black/10 backdrop-blur-md">
        <div className="p-8">
          <button
            onClick={() => createNewChat()}
            className="w-full py-4 px-6 bg-luxury-sage text-white rounded-2xl flex items-center justify-between group hover:shadow-xl hover:shadow-luxury-sage/20 transition-all duration-500"
          >
            <span className="font-serif font-bold text-lg tracking-tight text-left leading-none">
              New <br />Knowledge <br />Stream
            </span>
            <div className="p-2 bg-white/20 rounded-xl group-hover:rotate-90 transition-transform duration-500">
              <Plus size={20} />
            </div>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-4 space-y-2 custom-scrollbar">
          {chats.map((chat) => (
            <div
              key={chat.id}
              onClick={() => navigate(`/chat/${chat.id}`)}
              className={`p-5 rounded-3xl cursor-pointer group transition-all duration-500 ${
                currentChat?.id === chat.id
                  ? 'bg-white dark:bg-luxury-card-dark shadow-xl shadow-luxury-dark/5'
                  : 'hover:bg-white/40 dark:hover:bg-white/5'
              }`}
            >
              <div className="flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <span className={`text-sm font-serif font-bold truncate ${currentChat?.id === chat.id ? 'text-luxury-sage' : 'opacity-60'}`}>
                    {chat.title}
                  </span>
                  <button
                    onClick={(e) => deleteChat(chat.id, e)}
                    className="p-1.5 opacity-0 group-hover:opacity-100 hover:text-red-500 transition-all"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
                <div className="flex items-center gap-2 opacity-30 text-[10px] font-bold tracking-widest uppercase">
                  <Sparkles size={10} className={currentChat?.id === chat.id ? 'text-luxury-sage animate-pulse' : ''} />
                  {new Date(chat.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                </div>
              </div>
            </div>
          ))}
        </div>
      </aside>

      {/* Main Stream Interface */}
      <section className="flex-1 flex flex-col relative overflow-hidden">
        {currentChat ? (
          <>
            {/* Minimal Header */}
            <header className="px-12 py-8 flex items-center justify-between bg-gradient-to-b from-luxury-cream/80 dark:from-luxury-dark/80 to-transparent absolute top-0 left-0 right-0 z-10">
              <div className="flex items-center gap-6">
                <div className="w-12 h-12 bg-luxury-sage rounded-2xl flex items-center justify-center shadow-lg shadow-luxury-sage/20">
                  <Bot size={24} className="text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-serif tracking-tighter">{currentChat.title}</h1>
                  <p className="text-[10px] uppercase tracking-[0.3em] font-bold text-luxury-sage">
                    Neural Processing Active
                  </p>
                </div>
              </div>
            </header>

            {/* Knowledge Stream (Messages) */}
            <div className="flex-1 overflow-y-auto pt-32 pb-40 px-12 custom-scrollbar">
              <div className="max-w-5xl mx-auto space-y-12">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-6 ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-message-in`}
                  >
                    {message.role === 'assistant' && (
                      <div className="w-10 h-10 bg-luxury-sage/10 rounded-xl flex items-center justify-center mt-2">
                        <Sparkles size={16} className="text-luxury-sage" />
                      </div>
                    )}
                    <div className={`max-w-[80%] ${message.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-bot'}`}>
                      {message.role === 'assistant' && (
                        <div className="text-[10px] uppercase tracking-[0.2em] font-bold text-luxury-sage/60 mb-3 block">
                          Intelligence Output
                        </div>
                      )}
                      <p className="text-sm sm:text-base leading-relaxed whitespace-pre-wrap font-medium">
                        {message.content}
                      </p>
                    </div>
                  </div>
                ))}
                {streaming && (
                  <div className="flex items-center gap-2 text-luxury-sage/40 ml-16 animate-pulse font-bold tracking-widest text-[10px] uppercase">
                    Analyzing context...
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>

            {/* Floating Interaction Bar */}
            <div className="absolute bottom-10 left-1/2 -translate-x-1/2 w-full max-w-3xl px-6">
              <div className="relative group p-2 bg-white dark:bg-luxury-card-dark rounded-[2.5rem] shadow-2xl border border-luxury-dark/5 dark:border-white/5 transition-all duration-500 focus-within:ring-4 ring-luxury-sage/10">
                <div className="flex items-center gap-2 pl-4">
                  <div className="p-3 text-luxury-dark/20 dark:text-white/20 hover:text-luxury-sage transition-colors cursor-pointer">
                    <Paperclip size={20} />
                  </div>
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                    placeholder="Ask your digital oracle..."
                    className="flex-1 py-4 bg-transparent outline-none text-lg font-medium placeholder:text-luxury-dark/20 dark:placeholder:text-white/20"
                    disabled={streaming}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!input.trim() || streaming}
                    className="p-4 bg-luxury-sage text-white rounded-[2rem] shadow-lg shadow-luxury-sage/30 hover:scale-105 active:scale-95 disabled:opacity-30 disabled:grayscale transition-all duration-500"
                  >
                    <Send size={24} />
                  </button>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center p-12 text-center animate-fade-in">
            <div className="w-40 h-40 bg-luxury-sage/5 rounded-full flex items-center justify-center mb-10 relative">
              <div className="absolute inset-0 bg-luxury-sage/10 rounded-full animate-ping opacity-20" />
              <Bot size={64} className="text-luxury-sage opacity-20" />
            </div>
            <h2 className="text-5xl font-serif mb-6 tracking-tighter">Initialize Intelligence</h2>
            <p className="max-w-md text-xl text-luxury-dark/40 dark:text-white/40 mb-12 font-light leading-relaxed">
              Open a previous knowledge stream or start a new sequence to begin the extraction of data.
            </p>
            <button
              onClick={() => createNewChat()}
              className="btn-luxury px-12 py-5 text-xl flex items-center gap-4 group"
            >
              Start Launch Sequence
              <ArrowRight size={24} className="group-hover:translate-x-2 transition-transform" />
            </button>
          </div>
        )}
      </section>
    </div>
  )
}

const ArrowRight = ({ size, className }: { size: number, className?: string }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2.5" 
    strokeLinecap="round" 
    strokeLinejoin="round" 
    className={className}
  >
    <path d="M5 12h14m-7-7 7 7-7 7" />
  </svg>
)
