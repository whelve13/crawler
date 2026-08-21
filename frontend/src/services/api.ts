import { CrawlTaskStatus, CrawlReport } from '../types/api';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1';

export async function fetchRecentTasks(): Promise<CrawlTaskStatus[]> {
  const res = await fetch(`${API_BASE}/crawl/`);
  if (!res.ok) throw new Error('Failed to fetch recent tasks');
  return res.json();
}

export async function startCrawl(start_url: string, max_pages: number, max_depth: number): Promise<{ task_id: string, status: string }> {
  const res = await fetch(`${API_BASE}/crawl/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ start_url, max_pages, max_depth })
  });
  if (!res.ok) throw new Error('Failed to start crawl');
  return res.json();
}

export async function fetchTaskStatus(taskId: string): Promise<CrawlTaskStatus> {
  const res = await fetch(`${API_BASE}/crawl/${taskId}`);
  if (!res.ok) throw new Error('Failed to fetch task status');
  return res.json();
}

export async function fetchCrawlReport(taskId: string): Promise<CrawlReport> {
  const res = await fetch(`${API_BASE}/crawl/${taskId}/report`);
  if (!res.ok) throw new Error('Failed to fetch crawl report');
  return res.json();
}
