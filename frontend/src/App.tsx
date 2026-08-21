import { useState, useEffect } from 'react';
import { Activity, Play, CheckCircle, XCircle, Search } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1';

interface Task {
  task_id: string;
  status: string;
  pages_crawled: number;
  pages_failed: number;
  duration_seconds: number;
}

function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [url, setUrl] = useState('');
  const [maxPages, setMaxPages] = useState(50);
  const [maxDepth, setMaxDepth] = useState(3);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = async () => {
    try {
      const res = await fetch(`${API_BASE}/crawl/`);
      if (!res.ok) throw new Error('API Response was not OK');
      const data = await res.json();
      setTasks(data);
      setError(null);
      return data.some((t: Task) => t.status === 'pending' || t.status === 'running');
    } catch (e) {
      console.error('Failed to fetch tasks', e);
      setError('Failed to reach backend API.');
      return false; 
    }
  };

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    
    const poll = async () => {
      const shouldContinue = await fetchTasks();
      if (!shouldContinue && interval) {
        clearInterval(interval);
      }
    };
    
    poll(); // initial fetch
    interval = setInterval(poll, 3000);
    
    return () => clearInterval(interval);
  }, [loading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/crawl/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ start_url: url, max_pages: maxPages, max_depth: maxDepth })
      });
      if (!res.ok) throw new Error('Failed to start crawl');
      setUrl('');
      // fetchTasks will be triggered by [loading] dependency change when we set it to false
    } catch (e) {
      console.error(e);
      setError('Failed to start new crawl task.');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        
        <header className="flex items-center space-x-3 pb-4 border-b">
          <Activity className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold">Website Auditor</h1>
        </header>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
            <strong className="font-bold">Error! </strong>
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        <section className="bg-white p-6 rounded-xl shadow-sm border">
          <h2 className="text-xl font-semibold mb-4">Start New Crawl</h2>
          <form onSubmit={handleSubmit} className="flex flex-col md:flex-row gap-4 items-end">
            <div className="flex-1 w-full">
              <label className="block text-sm font-medium text-gray-700 mb-1">Starting URL</label>
              <input 
                type="url" 
                required 
                placeholder="https://example.com"
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                value={url}
                onChange={e => setUrl(e.target.value)}
              />
            </div>
            <div className="w-32">
              <label className="block text-sm font-medium text-gray-700 mb-1">Max Pages</label>
              <input 
                type="number" 
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                value={maxPages}
                onChange={e => setMaxPages(Number(e.target.value))}
              />
            </div>
            <div className="w-32">
              <label className="block text-sm font-medium text-gray-700 mb-1">Max Depth</label>
              <input 
                type="number" 
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                value={maxDepth}
                onChange={e => setMaxDepth(Number(e.target.value))}
              />
            </div>
            <button 
              type="submit" 
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition flex items-center h-[42px]"
            >
              <Play className="w-4 h-4 mr-2" />
              Start
            </button>
          </form>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-4">Recent Tasks</h2>
          <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
            <table className="w-full text-left">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-sm font-semibold text-gray-600">Task ID</th>
                  <th className="px-6 py-3 text-sm font-semibold text-gray-600">Status</th>
                  <th className="px-6 py-3 text-sm font-semibold text-gray-600">Pages</th>
                  <th className="px-6 py-3 text-sm font-semibold text-gray-600">Duration</th>
                  <th className="px-6 py-3 text-sm font-semibold text-gray-600">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {tasks.map(task => (
                  <tr key={task.task_id} className="hover:bg-gray-50 transition">
                    <td className="px-6 py-4 font-mono text-sm text-gray-500">
                      {task.task_id.split('-')[0]}...
                    </td>
                    <td className="px-6 py-4">
                      {task.status === 'completed' && <span className="inline-flex items-center text-green-700 bg-green-100 px-2 py-1 rounded-full text-xs font-semibold"><CheckCircle className="w-3 h-3 mr-1"/> Completed</span>}
                      {task.status === 'failed' && <span className="inline-flex items-center text-red-700 bg-red-100 px-2 py-1 rounded-full text-xs font-semibold"><XCircle className="w-3 h-3 mr-1"/> Failed</span>}
                      {task.status === 'running' && <span className="inline-flex items-center text-blue-700 bg-blue-100 px-2 py-1 rounded-full text-xs font-semibold"><Activity className="w-3 h-3 mr-1 animate-pulse"/> Running</span>}
                      {task.status === 'pending' && <span className="inline-flex items-center text-gray-700 bg-gray-100 px-2 py-1 rounded-full text-xs font-semibold">Pending</span>}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span className="text-green-600 font-medium">{task.pages_crawled}</span> / <span className="text-red-500">{task.pages_failed}</span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {task.duration_seconds.toFixed(1)}s
                    </td>
                    <td className="px-6 py-4">
                      <button 
                        disabled={task.status !== 'completed'}
                        className="text-blue-600 hover:text-blue-800 disabled:opacity-50 flex items-center text-sm font-medium"
                      >
                        <Search className="w-4 h-4 mr-1" /> View Report
                      </button>
                    </td>
                  </tr>
                ))}
                {tasks.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                      No tasks found. Start a crawl above!
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

      </div>
    </div>
  );
}

export default App;
