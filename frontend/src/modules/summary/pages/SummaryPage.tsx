import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { FileText, RefreshCw, Trash2, ArrowLeft } from 'lucide-react'
import { summaryService, Summary } from '../services/summaryService'
import { mediaService, Document } from '../../media/services/mediaService'

export default function SummaryPage() {
  const { documentId } = useParams()
  const [summary, setSummary] = useState<Summary | null>(null)
  const [document, setDocument] = useState<Document | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    if (documentId) {
      loadData()
    }
  }, [documentId])

  const loadData = async () => {
    setLoading(true)
    try {
      const [docData, summaryData] = await Promise.all([
        mediaService.getDocument(documentId!),
        summaryService.getSummary(documentId!).catch(() => null)
      ])
      setDocument(docData)
      setSummary(summaryData)
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateSummary = async () => {
    if (!documentId) return
    setGenerating(true)
    try {
      const newSummary = await summaryService.generateSummary(documentId)
      setSummary(newSummary)
    } catch (error) {
      console.error('Failed to generate summary:', error)
    } finally {
      setGenerating(false)
    }
  }

  const regenerateSummary = async () => {
    if (!documentId) return
    setGenerating(true)
    try {
      const newSummary = await summaryService.regenerateSummary(documentId)
      setSummary(newSummary)
    } catch (error) {
      console.error('Failed to regenerate summary:', error)
    } finally {
      setGenerating(false)
    }
  }

  const deleteSummary = async () => {
    if (!documentId || !confirm('Are you sure you want to delete this summary?')) return
    try {
      await summaryService.deleteSummary(documentId)
      setSummary(null)
    } catch (error) {
      console.error('Failed to delete summary:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
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
        <h1 className="text-3xl font-bold text-gray-900">Document Summary</h1>
        {document && (
          <p className="text-gray-600 mt-2">{document.title}</p>
        )}
      </div>

      <div className="card">
        {!summary ? (
          <div className="text-center py-12">
            <FileText size={48} className="text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">No summary generated yet</p>
            <button
              onClick={generateSummary}
              disabled={generating}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {generating ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white inline-block mr-2"></div>
                  Generating...
                </>
              ) : (
                'Generate Summary'
              )}
            </button>
          </div>
        ) : (
          <div>
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                <span className="badge bg-blue-100 text-blue-800">
                  {summary.summary_type}
                </span>
                <span className="text-sm text-gray-500">
                  {new Date(summary.updated_at).toLocaleDateString()}
                </span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={regenerateSummary}
                  disabled={generating}
                  className="btn-secondary flex items-center gap-2 disabled:opacity-50"
                >
                  <RefreshCw size={16} />
                  Regenerate
                </button>
                <button
                  onClick={deleteSummary}
                  className="text-red-600 hover:text-red-700"
                >
                  <Trash2 size={20} />
                </button>
              </div>
            </div>

            <div className="prose max-w-none">
              <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                {summary.content}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
