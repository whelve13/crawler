import { useState, useEffect, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, AlertCircle, Clock, Globe, FileWarning, Search, Link as LinkIcon, BarChart3, AlertTriangle, CheckCircle, XCircle, Activity } from 'lucide-react';
import { fetchCrawlReport } from '../services/api';
import { CrawlReport, PageReport, SEOIssue } from '../types/api';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';

export default function CrawlReportPage() {
  const { taskId } = useParams();
  const [report, setReport] = useState<CrawlReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPageUrl, setSelectedPageUrl] = useState<string | null>(null);
  const [pageFilter, setPageFilter] = useState<string>('All');

  useEffect(() => {
    if (!taskId) return;
    fetchCrawlReport(taskId)
      .then(data => {
        setReport(data);
        setLoading(false);
      })
      .catch(e => {
        setError('Failed to load report. Ensure the task is completed.');
        setLoading(false);
      });
  }, [taskId]);

  if (loading) {
    return <div className="flex justify-center items-center h-64 text-gray-500">Loading report data...</div>;
  }

  if (error || !report) {
    return (
      <div className="max-w-5xl mx-auto">
        <Link to="/" className="inline-flex items-center text-blue-600 hover:underline mb-6 font-medium">
          <ArrowLeft className="w-4 h-4 mr-1" /> Back to Dashboard
        </Link>
        <div className="bg-red-50 text-red-700 p-4 rounded-lg border border-red-200">{error}</div>
      </div>
    );
  }

  // Derived metrics
  const totalPages = report.pages.length;
  const status2xx = report.pages.filter(p => p.status_code && p.status_code >= 200 && p.status_code < 300).length;
  const status3xx = report.pages.filter(p => p.status_code && p.status_code >= 300 && p.status_code < 400).length;
  const status4xx = report.pages.filter(p => p.status_code && p.status_code >= 400 && p.status_code < 500).length;
  const status5xx = report.pages.filter(p => p.status_code && p.status_code >= 500).length;
  const failedPages = report.stats.pages_failed;
  
  const allSeoIssues = report.pages.flatMap(p => p.seo_issues.map(i => ({ ...i, url: p.url })));
  const totalSeoIssues = allSeoIssues.length;
  
  const redirects = report.health_issues.filter(i => i.issue_type === 'redirect_chain' || i.issue_type === 'redirect_loop');
  const brokenLinks = report.health_issues.filter(i => i.issue_type === 'broken_link');

  // Chart Data
  const chartData = [
    { name: '2xx', count: status2xx, color: '#10b981' }, // green-500
    { name: '3xx', count: status3xx, color: '#3b82f6' }, // blue-500
    { name: '4xx', count: status4xx, color: '#f59e0b' }, // amber-500
    { name: '5xx', count: status5xx, color: '#ef4444' }, // red-500
    { name: 'Failed', count: failedPages, color: '#6b7280' }, // gray-500
  ].filter(d => d.count > 0);

  // Filtered pages
  const filteredPages = report.pages.filter(p => {
    if (pageFilter === 'All') return true;
    if (pageFilter === '2xx') return p.status_code && p.status_code >= 200 && p.status_code < 300;
    if (pageFilter === '3xx') return p.status_code && p.status_code >= 300 && p.status_code < 400;
    if (pageFilter === '4xx') return p.status_code && p.status_code >= 400 && p.status_code < 500;
    if (pageFilter === '5xx') return p.status_code && p.status_code >= 500;
    if (pageFilter === 'Has SEO issues') return p.seo_issues.length > 0;
    return true;
  });

  const selectedPage = report.pages.find(p => p.url === selectedPageUrl);

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-300 pb-16">
      <nav>
        <Link to="/" className="inline-flex items-center text-blue-600 hover:text-blue-800 transition font-medium text-sm">
          <ArrowLeft className="w-4 h-4 mr-1" /> Back to Dashboard
        </Link>
      </nav>

      {/* 1. Crawl Overview */}
      <section>
        <div className="mb-4">
          <h1 className="text-2xl font-bold text-gray-900 truncate" title={report.start_url}>
            {report.start_url}
          </h1>
          <div className="flex items-center text-sm text-gray-500 mt-1">
            <CheckCircle className="w-4 h-4 text-green-500 mr-1" />
            <span className="font-medium mr-3">Completed</span>
            <Clock className="w-4 h-4 mr-1" />
            <span>{report.stats.duration_seconds.toFixed(1)}s</span>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <StatCard label="Pages Discovered" value={report.stats.pages_crawled + report.stats.pages_failed} icon={<Globe />} />
          <StatCard label="2xx Success" value={status2xx} icon={<CheckCircle />} color="text-green-600" />
          <StatCard label="3xx Redirects" value={status3xx} icon={<ArrowLeft className="rotate-180" />} color="text-blue-600" />
          <StatCard label="4xx Errors" value={status4xx} icon={<FileWarning />} color="text-amber-600" />
          <StatCard label="SEO Issues" value={totalSeoIssues} icon={<AlertTriangle />} color="text-red-600" />
        </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* 2. HTTP Status Distribution */}
        <section className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 col-span-1 lg:col-span-1">
          <h2 className="text-lg font-semibold mb-6 flex items-center"><BarChart3 className="w-5 h-5 mr-2 text-gray-400" /> Status Distribution</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" axisLine={false} tickLine={false} />
                <YAxis axisLine={false} tickLine={false} />
                <Tooltip cursor={{fill: '#f3f4f6'}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* 8. Crawl Performance */}
        <section className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 col-span-1 lg:col-span-2">
          <h2 className="text-lg font-semibold mb-4 flex items-center"><Activity className="w-5 h-5 mr-2 text-gray-400" /> Crawl Performance</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <div className="text-sm text-gray-500 mb-1">Total Duration</div>
              <div className="text-2xl font-bold">{report.stats.duration_seconds.toFixed(2)}s</div>
            </div>
            <div>
              <div className="text-sm text-gray-500 mb-1">Pages Crawled</div>
              <div className="text-2xl font-bold">{report.stats.pages_crawled}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500 mb-1">Pages / Second</div>
              <div className="text-2xl font-bold">
                {report.stats.duration_seconds > 0 ? (report.stats.pages_crawled / report.stats.duration_seconds).toFixed(1) : 0}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500 mb-1">Failed Requests</div>
              <div className="text-2xl font-bold text-red-600">{report.stats.pages_failed}</div>
            </div>
          </div>
        </section>
      </div>

      {/* 3. SEO Issues */}
      {totalSeoIssues > 0 && (
        <section className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
            <h2 className="text-lg font-semibold flex items-center"><AlertTriangle className="w-5 h-5 mr-2 text-amber-500" /> SEO Issues ({totalSeoIssues})</h2>
          </div>
          <div className="max-h-96 overflow-y-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-white sticky top-0 border-b shadow-sm">
                <tr>
                  <th className="px-6 py-3 font-semibold text-gray-600">Issue Type</th>
                  <th className="px-6 py-3 font-semibold text-gray-600">URL</th>
                  <th className="px-6 py-3 font-semibold text-gray-600">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {allSeoIssues.map((issue, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-6 py-3 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 rounded text-xs font-medium ${
                        issue.severity === 'error' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'
                      }`}>
                        {issue.rule_id}
                      </span>
                    </td>
                    <td className="px-6 py-3 truncate max-w-xs text-gray-600" title={issue.url}>
                      <button onClick={() => setSelectedPageUrl(issue.url)} className="text-blue-600 hover:underline text-left truncate w-full">
                        {new URL(issue.url).pathname || issue.url}
                      </button>
                    </td>
                    <td className="px-6 py-3 text-gray-700">{issue.message} {issue.element ? <span className="font-mono text-xs bg-gray-100 px-1 rounded ml-1">{issue.element}</span> : ''}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* 4 & 5. Network Health (Broken Links & Redirects) */}
      {(brokenLinks.length > 0 || redirects.length > 0) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {brokenLinks.length > 0 && (
            <section className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                <h2 className="text-lg font-semibold flex items-center"><XCircle className="w-5 h-5 mr-2 text-red-500" /> Broken Links ({brokenLinks.length})</h2>
              </div>
              <div className="max-h-80 overflow-y-auto p-4 space-y-3">
                {brokenLinks.map((bl, idx) => (
                  <div key={idx} className="bg-red-50 p-3 rounded-lg border border-red-100 text-sm">
                    <div className="font-semibold text-red-800 mb-1">{bl.issue_type}</div>
                    <div className="text-gray-700 break-all">{bl.description}</div>
                    <div className="mt-2 pt-2 border-t border-red-200/50 text-xs text-gray-500 break-all font-mono">
                      Target: {bl.url}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {redirects.length > 0 && (
            <section className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                <h2 className="text-lg font-semibold flex items-center"><LinkIcon className="w-5 h-5 mr-2 text-blue-500" /> Redirect Anomalies ({redirects.length})</h2>
              </div>
              <div className="max-h-80 overflow-y-auto p-4 space-y-3">
                {redirects.map((rd, idx) => (
                  <div key={idx} className="bg-blue-50 p-3 rounded-lg border border-blue-100 text-sm">
                    <div className="font-semibold text-blue-800 mb-1">{rd.issue_type}</div>
                    <div className="text-gray-700 break-all">{rd.description}</div>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      )}

      {/* 6. Pages Table */}
      <section className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <h2 className="text-lg font-semibold">Crawled Pages</h2>
          <div className="flex items-center space-x-2">
            <Search className="w-4 h-4 text-gray-400" />
            <select 
              value={pageFilter}
              onChange={e => setPageFilter(e.target.value)}
              className="border-gray-300 rounded-md text-sm pl-2 pr-8 py-1.5 focus:ring-blue-500 focus:border-blue-500"
            >
              <option>All</option>
              <option>2xx</option>
              <option>3xx</option>
              <option>4xx</option>
              <option>5xx</option>
              <option>Has SEO issues</option>
            </select>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-white border-b">
              <tr>
                <th className="px-6 py-3 font-semibold text-gray-600">URL</th>
                <th className="px-6 py-3 font-semibold text-gray-600">Status</th>
                <th className="px-6 py-3 font-semibold text-gray-600">Title</th>
                <th className="px-6 py-3 font-semibold text-gray-600 text-right">Issues</th>
                <th className="px-6 py-3 font-semibold text-gray-600 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredPages.map(p => (
                <tr key={p.url} className={`hover:bg-gray-50 ${selectedPageUrl === p.url ? 'bg-blue-50' : ''}`}>
                  <td className="px-6 py-3 text-gray-700 truncate max-w-[200px]" title={p.url}>
                    {new URL(p.url).pathname || '/'}
                  </td>
                  <td className="px-6 py-3">
                    <span className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${
                      !p.status_code ? 'bg-gray-100 text-gray-700' :
                      p.status_code < 300 ? 'bg-green-100 text-green-700' : 
                      p.status_code < 400 ? 'bg-blue-100 text-blue-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      {p.status_code || 'Err'}
                    </span>
                  </td>
                  <td className="px-6 py-3 text-gray-600 truncate max-w-[200px]" title={p.title || ''}>
                    {p.title || <span className="text-gray-400 italic">None</span>}
                  </td>
                  <td className="px-6 py-3 text-right">
                    {p.seo_issues.length > 0 ? (
                      <span className="text-amber-600 font-semibold">{p.seo_issues.length}</span>
                    ) : (
                      <span className="text-gray-400">0</span>
                    )}
                  </td>
                  <td className="px-6 py-3 text-right">
                    <button 
                      onClick={() => setSelectedPageUrl(p.url === selectedPageUrl ? null : p.url)}
                      className="text-blue-600 hover:text-blue-800 font-medium text-xs"
                    >
                      {selectedPageUrl === p.url ? 'Close Details' : 'View Details'}
                    </button>
                  </td>
                </tr>
              ))}
              {filteredPages.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                    No pages match the filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      {/* 7. Page Details Modal/Panel */}
      {selectedPage && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-3xl max-h-[90vh] flex flex-col animate-in zoom-in-95 duration-200">
            <div className="px-6 py-4 border-b flex justify-between items-center bg-gray-50 rounded-t-xl">
              <h3 className="font-semibold text-lg truncate pr-4">{selectedPage.url}</h3>
              <button onClick={() => setSelectedPageUrl(null)} className="text-gray-400 hover:text-gray-600">
                <XCircle className="w-6 h-6" />
              </button>
            </div>
            <div className="p-6 overflow-y-auto space-y-6">
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="block text-gray-500 mb-1">Status Code</span>
                  <span className="font-semibold">{selectedPage.status_code || 'Network Error'}</span>
                </div>
                <div>
                  <span className="block text-gray-500 mb-1">Language</span>
                  <span className="font-semibold">{selectedPage.language || 'Not specified'}</span>
                </div>
              </div>

              <div>
                <span className="block text-gray-500 mb-1 text-sm">Title</span>
                <div className="p-3 bg-gray-50 rounded border text-gray-800 font-medium">{selectedPage.title || <i className="text-gray-400">Missing</i>}</div>
              </div>

              <div>
                <span className="block text-gray-500 mb-1 text-sm">Meta Description</span>
                <div className="p-3 bg-gray-50 rounded border text-gray-800 text-sm">{selectedPage.meta_description || <i className="text-gray-400">Missing</i>}</div>
              </div>
              
              <div>
                <span className="block text-gray-500 mb-1 text-sm">Canonical URL</span>
                <div className="p-3 bg-gray-50 rounded border text-gray-800 text-sm truncate">{selectedPage.canonical_url || <i className="text-gray-400">Missing</i>}</div>
              </div>

              <div className="grid grid-cols-3 gap-4 text-sm">
                <div className="p-3 bg-gray-50 rounded border text-center">
                  <div className="text-2xl font-bold text-gray-700">{selectedPage.h1_tags.length}</div>
                  <div className="text-gray-500 mt-1">H1 Tags</div>
                </div>
                <div className="p-3 bg-gray-50 rounded border text-center">
                  <div className="text-2xl font-bold text-gray-700">{selectedPage.h2_tags.length}</div>
                  <div className="text-gray-500 mt-1">H2 Tags</div>
                </div>
                <div className="p-3 bg-gray-50 rounded border text-center">
                  <div className="text-2xl font-bold text-gray-700">{selectedPage.internal_links.length}</div>
                  <div className="text-gray-500 mt-1">Internal Links</div>
                </div>
              </div>

              {selectedPage.seo_issues.length > 0 && (
                <div>
                  <span className="block text-gray-500 mb-2 text-sm font-medium">Page SEO Issues</span>
                  <ul className="space-y-2">
                    {selectedPage.seo_issues.map((issue, idx) => (
                      <li key={idx} className="bg-amber-50 border border-amber-100 p-3 rounded text-sm text-amber-800 flex items-start">
                        <AlertCircle className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                        <div>
                          <strong>{issue.rule_id}:</strong> {issue.message}
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

            </div>
          </div>
        </div>
      )}

    </div>
  );
}

function StatCard({ label, value, icon, color = "text-gray-700" }: { label: string, value: string | number, icon: React.ReactNode, color?: string }) {
  return (
    <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center mb-3 bg-gray-50 ${color}`}>
        {icon}
      </div>
      <div className="text-2xl font-bold text-gray-900">{value}</div>
      <div className="text-sm font-medium text-gray-500 mt-1">{label}</div>
    </div>
  );
}
