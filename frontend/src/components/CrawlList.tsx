import { Activity, CheckCircle, XCircle, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { CrawlTaskStatus } from '../types/api';

interface CrawlListProps {
  tasks: CrawlTaskStatus[];
}

export default function CrawlList({ tasks }: CrawlListProps) {
  return (
    <section>
      <h2 className="text-xl font-semibold mb-4 text-gray-800">Recent Tasks</h2>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-xs font-semibold text-gray-600 uppercase tracking-wider">Task ID</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-600 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-600 uppercase tracking-wider">Pages</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-600 uppercase tracking-wider">Duration</th>
              <th className="px-6 py-3 text-xs font-semibold text-gray-600 uppercase tracking-wider text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {tasks.map(task => (
              <tr key={task.task_id} className="hover:bg-gray-50/50 transition">
                <td className="px-6 py-4 font-mono text-sm text-gray-500">
                  {task.task_id.split('-')[0]}...
                </td>
                <td className="px-6 py-4">
                  {task.status === 'completed' && <span className="inline-flex items-center text-green-700 bg-green-50 px-2.5 py-1 rounded-full text-xs font-medium border border-green-200"><CheckCircle className="w-3.5 h-3.5 mr-1.5"/> Completed</span>}
                  {task.status === 'failed' && <span className="inline-flex items-center text-red-700 bg-red-50 px-2.5 py-1 rounded-full text-xs font-medium border border-red-200"><XCircle className="w-3.5 h-3.5 mr-1.5"/> Failed</span>}
                  {task.status === 'running' && <span className="inline-flex items-center text-blue-700 bg-blue-50 px-2.5 py-1 rounded-full text-xs font-medium border border-blue-200"><Activity className="w-3.5 h-3.5 mr-1.5 animate-pulse"/> Running</span>}
                  {task.status === 'pending' && <span className="inline-flex items-center text-gray-700 bg-gray-100 px-2.5 py-1 rounded-full text-xs font-medium border border-gray-200">Pending</span>}
                </td>
                <td className="px-6 py-4 text-sm text-gray-700">
                  <span className="font-medium">{task.pages_crawled}</span> <span className="text-gray-400 mx-1">/</span> <span className="text-red-500">{task.pages_failed} fail</span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {task.duration_seconds.toFixed(1)}s
                </td>
                <td className="px-6 py-4 text-right">
                  <Link 
                    to={`/report/${task.task_id}`}
                    className={`inline-flex items-center text-sm font-medium ${task.status === 'completed' ? 'text-blue-600 hover:text-blue-800' : 'text-gray-400 pointer-events-none'}`}
                  >
                    View Report <ChevronRight className="w-4 h-4 ml-1" />
                  </Link>
                </td>
              </tr>
            ))}
            {tasks.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-gray-500 text-sm">
                  No tasks found. Start a crawl above.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
