import { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Play, Pause, SkipBack, SkipForward, ArrowLeft } from 'lucide-react'
import { playerService } from '../services/playerService'
import { mediaService, Document } from '../../media/services/mediaService'
import { formatTimestamp } from '../../../lib/utils'

export default function PlayerPage() {
  const { documentId } = useParams()
  const [document, setDocument] = useState<Document | null>(null)
  const [mediaUrl, setMediaUrl] = useState<string | null>(null)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [loading, setLoading] = useState(true)
  const videoRef = useRef<HTMLVideoElement>(null)
  const audioRef = useRef<HTMLAudioElement>(null)

  useEffect(() => {
    if (documentId) {
      loadMedia()
    }
  }, [documentId])

  const loadMedia = async () => {
    setLoading(true)
    try {
      const [docData, urlData] = await Promise.all([
        mediaService.getDocument(documentId!),
        playerService.getMediaUrl(documentId!)
      ])
      setDocument(docData)
      setMediaUrl(urlData.url)
    } catch (error) {
      console.error('Failed to load media:', error)
    } finally {
      setLoading(false)
    }
  }

  const togglePlay = () => {
    const media = document?.file_type === 'video' ? videoRef.current : audioRef.current
    if (media) {
      if (isPlaying) {
        media.pause()
      } else {
        media.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  const handleTimeUpdate = () => {
    const media = document?.file_type === 'video' ? videoRef.current : audioRef.current
    if (media) {
      setCurrentTime(media.currentTime)
      setDuration(media.duration || 0)
    }
  }

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value)
    const media = document?.file_type === 'video' ? videoRef.current : audioRef.current
    if (media) {
      media.currentTime = time
      setCurrentTime(time)
    }
  }

  const skip = (seconds: number) => {
    const media = document?.file_type === 'video' ? videoRef.current : audioRef.current
    if (media) {
      media.currentTime = Math.max(0, Math.min(duration, media.currentTime + seconds))
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!document || !mediaUrl) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Failed to load media</p>
        <Link to="/media" className="btn-primary inline-block mt-4">
          Back to Media Library
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <Link to="/media" className="text-blue-600 hover:text-blue-700 flex items-center gap-2">
          <ArrowLeft size={20} />
          Back to Media Library
        </Link>
      </div>

      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">{document.title}</h1>
      </div>

      <div className="card">
        {document.file_type === 'video' ? (
          <video
            ref={videoRef}
            src={mediaUrl}
            className="w-full rounded-lg mb-4"
            onTimeUpdate={handleTimeUpdate}
            onLoadedMetadata={handleTimeUpdate}
            controls
          />
        ) : (
          <audio
            ref={audioRef}
            src={mediaUrl}
            className="w-full mb-4"
            onTimeUpdate={handleTimeUpdate}
            onLoadedMetadata={handleTimeUpdate}
            controls
          />
        )}

        {/* Custom Controls */}
        <div className="space-y-4">
          <div>
            <input
              type="range"
              min="0"
              max={duration || 0}
              value={currentTime}
              onChange={handleSeek}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-gray-600 mt-1">
              <span>{formatTimestamp(currentTime)}</span>
              <span>{formatTimestamp(duration)}</span>
            </div>
          </div>

          <div className="flex items-center justify-center gap-4">
            <button onClick={() => skip(-10)} className="p-2 hover:bg-gray-100 rounded-lg">
              <SkipBack size={24} />
            </button>
            <button
              onClick={togglePlay}
              className="p-4 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors"
            >
              {isPlaying ? <Pause size={24} /> : <Play size={24} />}
            </button>
            <button onClick={() => skip(10)} className="p-2 hover:bg-gray-100 rounded-lg">
              <SkipForward size={24} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
