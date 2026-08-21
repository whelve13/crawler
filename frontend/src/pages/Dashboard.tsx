import { useState, useEffect } from 'react';
import { Activity } from 'lucide-react';
import CrawlForm from '../components/CrawlForm';
import CrawlList from '../components/CrawlList';
import { fetchRecentTasks } from '../services/api';
import { CrawlTaskStatus } from '../types/api';

export default function Dashboard() {
  const [tasks, setTasks] = useState<CrawlTaskStatus[]>([]);
  const [error, setError] = useState<string | null>(null);

  const loadTasks = async () => {
    try {
      const data = await fetchRecentTasks();
      setTasks(data);
      setError(null);
      return data.some((t) => t.status === 'pending' || t.status === 'running');
    } catch (e) {
      console.error(e);
      setError('Failed to reach backend API.');
      return false;
    }
  };

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    
    const poll = async () => {
      const shouldContinue = await loadTasks();
      if (!shouldContinue && interval) {
        clearInterval(interval);
      }
    };
    
    poll();
    interval = setInterval(poll, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-300">
      <header className="flex items-center space-x-3 pb-4 border-b border-terminal-border">
        <Activity className="w-8 h-8 text-terminal-accent" />
        <h1 className="text-3xl font-bold text-terminal-accent tracking-tight">Crawler</h1>
      </header>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          <strong className="font-semibold">Connection Error: </strong>
          <span>{error}</span>
        </div>
      )}

      <CrawlForm onSuccess={() => loadTasks()} />
      <CrawlList tasks={tasks} />
    </div>
  );
}
