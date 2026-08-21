import React, { useState } from 'react';
import { Play } from 'lucide-react';
import { startCrawl } from '../services/api';

interface CrawlFormProps {
  onSuccess: () => void;
}

export default function CrawlForm({ onSuccess }: CrawlFormProps) {
  const [url, setUrl] = useState('');
  const [maxPages, setMaxPages] = useState(50);
  const [maxDepth, setMaxDepth] = useState(3);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await startCrawl(url, maxPages, maxDepth);
      setUrl('');
      onSuccess();
    } catch (e) {
      console.error(e);
      setError('Failed to start new crawl task.');
    }
    setLoading(false);
  };

  return (
    <section className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">Start New Crawl</h2>
      
      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
          <strong>Error! </strong> {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex flex-col md:flex-row gap-4 items-end">
        <div className="flex-1 w-full">
          <label className="block text-sm font-medium text-gray-700 mb-1">Starting URL</label>
          <input 
            type="url" 
            required 
            placeholder="https://example.com"
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            value={url}
            onChange={e => setUrl(e.target.value)}
          />
        </div>
        <div className="w-32">
          <label className="block text-sm font-medium text-gray-700 mb-1">Max Pages</label>
          <input 
            type="number" 
            min="1"
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            value={maxPages}
            onChange={e => setMaxPages(Number(e.target.value))}
          />
        </div>
        <div className="w-32">
          <label className="block text-sm font-medium text-gray-700 mb-1">Max Depth</label>
          <input 
            type="number"
            min="1" 
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            value={maxDepth}
            onChange={e => setMaxDepth(Number(e.target.value))}
          />
        </div>
        <button 
          type="submit" 
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition flex items-center h-[42px] disabled:opacity-50"
        >
          <Play className="w-4 h-4 mr-2" />
          {loading ? 'Starting...' : 'Start'}
        </button>
      </form>
    </section>
  );
}
