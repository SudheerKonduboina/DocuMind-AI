import React, { useState, useEffect } from 'react';

interface SummaryPanelProps {
  documentId: string;
  summary?: string;
  isLoading?: boolean;
}

export const SummaryPanel: React.FC<SummaryPanelProps> = ({
  documentId,
  summary: initialSummary,
  isLoading: initialLoading = false
}) => {
  const [summary, setSummary] = useState(initialSummary);
  const [isLoading, setIsLoading] = useState(initialLoading);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!initialSummary && documentId) {
      fetchSummary();
    }
  }, [documentId, initialSummary]);

  const fetchSummary = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/documents/${documentId}/summary`);
      if (!response.ok) {
        throw new Error('Failed to fetch summary');
      }
      const data = await response.json();
      setSummary(data.summary);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="summary-panel p-4 bg-gray-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-2">Summary</h3>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded mb-2"></div>
          <div className="h-4 bg-gray-200 rounded mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="summary-panel p-4 bg-red-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-2 text-red-800">Summary</h3>
        <p className="text-red-600">{error}</p>
        <button
          onClick={fetchSummary}
          className="mt-2 px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="summary-panel p-4 bg-gray-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-2">Summary</h3>
        <p className="text-gray-600">No summary available yet.</p>
        <button
          onClick={fetchSummary}
          className="mt-2 px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Generate Summary
        </button>
      </div>
    );
  }

  return (
    <div className="summary-panel p-4 bg-gray-50 rounded-lg">
      <h3 className="text-lg font-semibold mb-2">Summary</h3>
      <div className="prose prose-sm max-w-none">
        <p className="text-gray-700 whitespace-pre-wrap">{summary}</p>
      </div>
    </div>
  );
};
