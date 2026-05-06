import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, FileText, Music, Video, X, AlertCircle, CheckCircle2, Sparkles } from 'lucide-react'
import api from '../../../lib/api'

export default function UploadPage() {
  const navigate = useNavigate()
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setError('')
      setSuccess(false)
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setError('')
    const formData = new FormData()
    formData.append('file', file)

    try {
      await api.post('/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 100))
          setProgress(percentCompleted)
        },
      })
      setSuccess(true)
      setTimeout(() => navigate('/media'), 2000)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const getFileIcon = () => {
    if (!file) return <Upload size={48} className="text-luxury-sage opacity-20" />
    const type = file.type
    if (type.includes('pdf')) return <FileText size={48} className="text-red-500" />
    if (type.includes('audio')) return <Music size={48} className="text-purple-500" />
    if (type.includes('video')) return <Video size={48} className="text-blue-500" />
    return <FileText size={48} className="text-luxury-sage" />
  }

  return (
    <div className="max-w-4xl mx-auto space-y-12">
      <div className="text-center animate-fade-in">
        <div className="flex items-center justify-center gap-3 text-luxury-sage mb-6">
          <Sparkles size={24} className="animate-float" />
          <span className="text-xs uppercase tracking-[0.4em] font-bold">New Knowledge Intake</span>
        </div>
        <h1 className="text-7xl font-serif mb-6">Import Asset</h1>
        <p className="text-xl text-luxury-dark/50 dark:text-white/50 max-w-2xl mx-auto font-light leading-relaxed">
          Select a file to begin the processing sequence. Our AI will analyze and categorize your content instantly.
        </p>
      </div>

      <div className="luxury-card !p-12 animate-slide-up">
        <div 
          onClick={() => !uploading && fileInputRef.current?.click()}
          className={`relative border-2 border-dashed rounded-[3rem] p-16 text-center cursor-pointer transition-all duration-500 group ${
            file ? 'border-luxury-sage bg-luxury-sage/5' : 'border-luxury-dark/10 dark:border-white/10 hover:border-luxury-sage/40 hover:bg-luxury-sage/5'
          } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            className="hidden"
            accept=".pdf,.mp3,.mp4,.wav,.m4a,.mov,.avi"
            disabled={uploading}
          />

          <div className="flex flex-col items-center gap-6">
            <div className={`p-8 bg-white dark:bg-luxury-dark rounded-[2.5rem] shadow-xl transition-all duration-500 ${file ? 'scale-110 rotate-3' : 'group-hover:scale-105'}`}>
              {getFileIcon()}
            </div>
            
            {file ? (
              <div className="animate-scale-in">
                <h3 className="text-2xl font-serif mb-2">{file.name}</h3>
                <p className="text-xs uppercase tracking-widest opacity-40 font-bold">
                  {(file.size / (1024 * 1024)).toFixed(2)} MB • Ready for ingestion
                </p>
                {!uploading && (
                  <button 
                    onClick={(e) => { e.stopPropagation(); setFile(null); }}
                    className="mt-6 p-3 bg-red-50 text-red-500 rounded-full hover:bg-red-100 transition-colors"
                  >
                    <X size={20} />
                  </button>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                <h3 className="text-2xl font-serif">Drop your file here</h3>
                <p className="text-sm opacity-40 leading-relaxed font-medium">
                  Support for PDF, MP3, MP4 and more <br />
                  Max file size: 500MB
                </p>
                <div className="btn-luxury-outline inline-block mt-4">
                  Select from Computer
                </div>
              </div>
            )}
          </div>
        </div>

        {uploading && (
          <div className="mt-12 space-y-4 animate-fade-in">
            <div className="flex justify-between items-end mb-2">
              <span className="text-xs uppercase tracking-widest font-bold text-luxury-sage animate-pulse">Processing...</span>
              <span className="font-serif text-2xl">{progress}%</span>
            </div>
            <div className="h-3 w-full bg-luxury-sage/10 rounded-full overflow-hidden">
              <div 
                className="h-full bg-luxury-sage transition-all duration-500 ease-out rounded-full shadow-[0_0_20px_rgba(67,104,80,0.4)]"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {error && (
          <div className="mt-8 p-6 bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-900/30 rounded-3xl flex items-center gap-4 text-red-600 dark:text-red-400 animate-shake">
            <AlertCircle size={24} />
            <span className="text-sm font-medium">{error}</span>
          </div>
        )}

        {success && (
          <div className="mt-8 p-6 bg-green-50 dark:bg-green-900/20 border border-green-100 dark:border-green-900/30 rounded-3xl flex items-center gap-4 text-green-600 dark:text-green-400 animate-scale-in">
            <CheckCircle2 size={24} />
            <div className="flex flex-col">
              <span className="text-sm font-bold uppercase tracking-widest">Ingestion Complete</span>
              <span className="text-xs opacity-60">Redirecting to archive...</span>
            </div>
          </div>
        )}

        {file && !uploading && !success && (
          <button
            onClick={handleUpload}
            className="btn-luxury w-full mt-12 flex items-center justify-center gap-3 py-6 text-xl"
          >
            Start Launch Sequence
            <Sparkles size={24} />
          </button>
        )}
      </div>
    </div>
  )
}
