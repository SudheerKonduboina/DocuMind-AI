import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { FileText, Upload, MessageSquare, Clock, Sparkles, ArrowRight, Zap } from 'lucide-react'
import api from '../../../lib/api'
import { formatFileSize } from '../../../lib/utils'

interface Document {
  id: string
  title: string
  file_type: string
  file_size: number
  status: string
  created_at: string
}

interface Chat {
  id: string
  title: string
  updated_at: string
}

export default function DashboardPage() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [chats, setChats] = useState<Chat[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const [docsRes, chatsRes] = await Promise.all([
        api.get('/documents?page=1&limit=5'),
        api.get('/chats')
      ])
      setDocuments(docsRes.data.items || [])
      setChats(chatsRes.data.items || [])
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
      case 'processing':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="relative w-16 h-16">
          <div className="absolute inset-0 border-4 border-luxury-sage/20 rounded-full" />
          <div className="absolute inset-0 border-4 border-luxury-sage border-t-transparent rounded-full animate-spin" />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <div className="relative py-12 animate-fade-in">
        <div className="absolute top-0 right-0 -z-10 opacity-10">
          <Sparkles size={300} className="text-luxury-sage animate-float" />
        </div>
        <div className="flex items-center gap-3 text-luxury-sage mb-6">
          <Zap size={20} className="fill-current" />
          <span className="text-xs uppercase tracking-[0.4em] font-bold">Intelligent Workspace</span>
        </div>
        <h1 className="text-7xl font-serif leading-[1.1] max-w-4xl">
          Everything <span className="italic text-luxury-sage">Analyzed</span>. <br />
          Perfectly <span className="font-light opacity-50">Organized</span>.
        </h1>
        <p className="text-xl text-luxury-dark/50 dark:text-white/50 mt-8 max-w-xl font-light leading-relaxed">
          Your personal AI-powered knowledge base. Upload documents and start a conversation with your data today.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 animate-slide-up">
        <Link to="/upload" className="luxury-card group !p-10">
          <div className="flex flex-col gap-6">
            <div className="w-16 h-16 bg-luxury-sage/10 rounded-[1.5rem] flex items-center justify-center group-hover:scale-110 transition-transform duration-500">
              <Upload size={28} className="text-luxury-sage" />
            </div>
            <div>
              <h3 className="text-2xl font-serif mb-2">Upload</h3>
              <p className="text-sm opacity-40 leading-relaxed font-medium tracking-wide">
                Import PDF, Audio, or Video files to start the analysis process.
              </p>
            </div>
            <div className="flex items-center gap-2 text-luxury-sage font-bold text-xs uppercase tracking-[0.2em] mt-4 opacity-0 group-hover:opacity-100 transition-all">
              Get Started <ArrowRight size={16} />
            </div>
          </div>
        </Link>

        <Link to="/chat" className="luxury-card group !p-10">
          <div className="flex flex-col gap-6">
            <div className="w-16 h-16 bg-luxury-gold/10 rounded-[1.5rem] flex items-center justify-center group-hover:scale-110 transition-transform duration-500">
              <MessageSquare size={28} className="text-luxury-gold" />
            </div>
            <div>
              <h3 className="text-2xl font-serif mb-2">Interact</h3>
              <p className="text-sm opacity-40 leading-relaxed font-medium tracking-wide">
                Start a knowledge stream and ask questions about your documents.
              </p>
            </div>
            <div className="flex items-center gap-2 text-luxury-gold font-bold text-xs uppercase tracking-[0.2em] mt-4 opacity-0 group-hover:opacity-100 transition-all">
              Open Stream <ArrowRight size={16} />
            </div>
          </div>
        </Link>

        <Link to="/library" className="luxury-card group !p-10">
          <div className="flex flex-col gap-6">
            <div className="w-16 h-16 bg-luxury-dark/10 dark:bg-white/10 rounded-[1.5rem] flex items-center justify-center group-hover:scale-110 transition-transform duration-500">
              <FileText size={28} className="text-luxury-dark dark:text-white" />
            </div>
            <div>
              <h3 className="text-2xl font-serif mb-2">Library</h3>
              <p className="text-sm opacity-40 leading-relaxed font-medium tracking-wide">
                Browse and manage your entire collection of knowledge assets.
              </p>
            </div>
            <div className="flex items-center gap-2 text-luxury-dark dark:text-white font-bold text-xs uppercase tracking-[0.2em] mt-4 opacity-0 group-hover:opacity-100 transition-all">
              Browse All <ArrowRight size={16} />
            </div>
          </div>
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 animate-slide-up animate-delay-200">
        {/* Recent Documents */}
        <div className="luxury-card !p-10">
          <div className="flex items-center justify-between mb-10">
            <h2 className="text-3xl font-serif">Latest Files</h2>
            <Link to="/library" className="text-luxury-sage hover:underline text-sm font-bold uppercase tracking-widest">
              View Library
            </Link>
          </div>

          {documents.length === 0 ? (
            <div className="text-center py-20 opacity-20">
              <FileText size={64} className="mx-auto mb-4" />
              <p className="font-serif text-xl">Your archive is empty</p>
            </div>
          ) : (
            <div className="space-y-6">
              {documents.map((doc) => (
                <Link
                  key={doc.id}
                  to={`/chat`}
                  state={{ documentId: doc.id }}
                  className="flex items-center gap-6 p-6 rounded-3xl hover:bg-luxury-sage/5 transition-colors group"
                >
                  <div className="p-4 bg-luxury-cream dark:bg-luxury-dark rounded-2xl group-hover:bg-luxury-sage group-hover:text-white transition-all">
                    <FileText size={24} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-serif truncate">{doc.title}</h3>
                    <p className="text-xs uppercase tracking-widest opacity-40 mt-1 font-bold">
                      {formatFileSize(doc.file_size)} • {new Date(doc.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <span className={`px-4 py-1.5 rounded-full text-[10px] uppercase tracking-widest font-bold ${getStatusColor(doc.status)}`}>
                    {doc.status}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Recent Chats */}
        <div className="luxury-card !p-10">
          <div className="flex items-center justify-between mb-10">
            <h2 className="text-3xl font-serif">Recent Streams</h2>
            <Link to="/chat" className="text-luxury-sage hover:underline text-sm font-bold uppercase tracking-widest">
              All Conversations
            </Link>
          </div>

          {chats.length === 0 ? (
            <div className="text-center py-20 opacity-20">
              <MessageSquare size={64} className="mx-auto mb-4" />
              <p className="font-serif text-xl">No active streams</p>
            </div>
          ) : (
            <div className="space-y-6">
              {chats.map((chat) => (
                <Link
                  key={chat.id}
                  to={`/chat/${chat.id}`}
                  className="flex items-center gap-6 p-6 rounded-3xl hover:bg-luxury-sage/5 transition-colors group"
                >
                  <div className="p-4 bg-luxury-cream dark:bg-luxury-dark rounded-2xl group-hover:bg-luxury-gold group-hover:text-white transition-all">
                    <MessageSquare size={24} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-serif truncate">{chat.title}</h3>
                    <div className="flex items-center gap-2 text-xs uppercase tracking-widest opacity-40 mt-1 font-bold">
                      <Clock size={14} />
                      {new Date(chat.updated_at).toLocaleDateString()}
                    </div>
                  </div>
                  <ArrowRight size={20} className="text-luxury-sage opacity-0 group-hover:opacity-100 transition-all group-hover:translate-x-2" />
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
