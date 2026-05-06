import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { FileText, Music, Video, Trash2, Search, Sparkles, Clock, HardDrive } from 'lucide-react'
import { mediaService, Document } from '../services/mediaService'
import { formatFileSize } from '../../../lib/utils'

export default function MediaLibraryPage() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string>('all')
  const [search, setSearch] = useState('')

  useEffect(() => {
    loadDocuments()
  }, [filter])

  const loadDocuments = async () => {
    setLoading(true)
    try {
      const fileType = filter === 'all' ? undefined : filter
      const data = await mediaService.getDocuments(1, 50, fileType)
      setDocuments(data.items || [])
    } catch (error) {
      console.error('Failed to load documents:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return
    
    try {
      await mediaService.deleteDocument(id)
      loadDocuments()
    } catch (error) {
      console.error('Failed to delete document:', error)
    }
  }

  const getFileIcon = (fileType: string) => {
    switch (fileType) {
      case 'pdf':
        return <FileText size={24} className="text-red-500" />
      case 'audio':
        return <Music size={24} className="text-purple-500" />
      case 'video':
        return <Video size={24} className="text-blue-500" />
      default:
        return <FileText size={24} className="text-luxury-sage" />
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

  const filteredDocuments = documents.filter(doc =>
    doc.title.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-12">
      <div className="flex flex-col md:flex-row justify-between items-end gap-6 animate-fade-in">
        <div className="max-w-2xl">
          <div className="flex items-center gap-3 text-luxury-sage mb-4">
            <Sparkles size={20} className="animate-float" />
            <span className="text-xs uppercase tracking-[0.3em] font-bold">Your Digital Archive</span>
          </div>
          <h1 className="text-6xl font-serif leading-tight">Media Library</h1>
          <p className="text-xl text-luxury-dark/50 dark:text-white/50 mt-4 font-light">
            An organized collection of your knowledge assets. Seamlessly manage and interact with your files.
          </p>
        </div>
        
        <Link to="/upload" className="btn-luxury group">
          Upload New File
          <Sparkles className="inline ml-2 group-hover:rotate-12 transition-transform" size={18} />
        </Link>
      </div>

      {/* Luxury Search & Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-4 p-4 bg-white/40 dark:bg-white/5 backdrop-blur-md rounded-[2.5rem] border border-white/20 dark:border-white/5 animate-slide-up">
        <div className="flex-1 relative">
          <Search className="absolute left-6 top-1/2 -translate-y-1/2 text-luxury-sage/40" size={20} />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by filename..."
            className="w-full pl-14 pr-6 py-4 bg-transparent outline-none text-lg placeholder:text-luxury-dark/20 dark:placeholder:text-white/20"
          />
        </div>
        <div className="flex gap-2 p-1">
          {['all', 'pdf', 'audio', 'video'].map((type) => (
            <button
              key={type}
              onClick={() => setFilter(type)}
              className={`px-6 py-3 rounded-full text-sm font-medium transition-all duration-500 uppercase tracking-widest ${
                filter === type 
                ? 'bg-luxury-sage text-white shadow-lg' 
                : 'hover:bg-luxury-sage/10 text-luxury-dark/60 dark:text-white/60'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Documents Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="relative w-16 h-16">
            <div className="absolute inset-0 border-4 border-luxury-sage/20 rounded-full" />
            <div className="absolute inset-0 border-4 border-luxury-sage border-t-transparent rounded-full animate-spin" />
          </div>
        </div>
      ) : filteredDocuments.length === 0 ? (
        <div className="luxury-card text-center py-24 animate-scale-in">
          <div className="w-24 h-24 bg-luxury-sage/10 rounded-full flex items-center justify-center mx-auto mb-6">
            <FileText size={40} className="text-luxury-sage opacity-40" />
          </div>
          <h2 className="text-2xl font-serif mb-2">No documents found</h2>
          <p className="text-luxury-dark/40 dark:text-white/40 mb-8">Start by uploading your first file to begin the experience.</p>
          <Link to="/upload" className="btn-luxury-outline">
            Upload Document
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredDocuments.map((doc, index) => (
            <div 
              key={doc.id} 
              className="luxury-card group animate-slide-up"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="flex items-start justify-between mb-8">
                <div className="p-4 bg-luxury-cream dark:bg-luxury-dark rounded-3xl group-hover:bg-luxury-sage group-hover:text-white transition-colors duration-500">
                  {getFileIcon(doc.file_type)}
                </div>
                <button
                  onClick={() => handleDelete(doc.id)}
                  className="p-2 text-luxury-dark/20 dark:text-white/20 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl transition-all"
                >
                  <Trash2 size={20} />
                </button>
              </div>
              
              <h3 className="text-xl font-serif mb-4 truncate group-hover:text-luxury-sage transition-colors">
                {doc.title}
              </h3>
              
              <div className="grid grid-cols-2 gap-4 mb-8">
                <div className="flex items-center gap-2 text-xs text-luxury-dark/40 dark:text-white/40 uppercase tracking-widest font-bold">
                  <HardDrive size={14} />
                  {formatFileSize(doc.file_size)}
                </div>
                <div className="flex items-center gap-2 text-xs text-luxury-dark/40 dark:text-white/40 uppercase tracking-widest font-bold">
                  <Clock size={14} />
                  {new Date(doc.created_at).toLocaleDateString()}
                </div>
              </div>

              <div className="flex items-center justify-between pt-6 border-t border-luxury-dark/5 dark:border-white/5">
                <span className={`px-4 py-1.5 rounded-full text-[10px] uppercase tracking-[0.2em] font-bold ${getStatusColor(doc.status)}`}>
                  {doc.status}
                </span>
                {doc.status === 'completed' && (
                  <Link
                    to={`/chat`}
                    state={{ documentId: doc.id }}
                    className="flex items-center gap-2 text-luxury-sage font-bold text-xs uppercase tracking-widest hover:translate-x-2 transition-transform"
                  >
                    Enter Chat
                    <Sparkles size={16} />
                  </Link>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
