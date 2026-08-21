import { useState, useMemo, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { PageReport } from '../types/api';
import { Search, ZoomIn, ZoomOut, AlertTriangle, Link as LinkIcon, FileQuestion, Globe } from 'lucide-react';

interface SiteGraphProps {
  pages: PageReport[];
  startUrl: string;
  onNodeClick: (url: string) => void;
}

export default function SiteGraph({ pages, startUrl, onNodeClick }: SiteGraphProps) {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<'all' | '2xx' | 'errors' | 'orphans'>('all');

  // Compute graph data
  const { nodes, links, stats } = useMemo(() => {
    const graphNodes: any[] = [];
    const graphLinks: any[] = [];
    
    // Quick lookup for crawled pages
    const crawledUrls = new Set(pages.map(p => p.url));
    const incomingCounts: Record<string, number> = {};
    
    // Compute edges and incoming counts
    pages.forEach(p => {
      p.internal_links.forEach(target => {
        // Only include edges to pages that were actually crawled or we consider them "external/uncrawled"
        if (crawledUrls.has(target)) {
          graphLinks.push({ source: p.url, target });
          incomingCounts[target] = (incomingCounts[target] || 0) + 1;
        }
      });
    });

    let orphanCount = 0;
    
    // Generate nodes
    pages.forEach(p => {
      const isStart = p.url === startUrl;
      const incoming = incomingCounts[p.url] || 0;
      const outgoing = p.internal_links.filter(t => crawledUrls.has(t)).length;
      
      const isOrphan = !isStart && incoming === 0;
      if (isOrphan) orphanCount++;
      
      const is2xx = p.status_code && p.status_code >= 200 && p.status_code < 300;
      const isError = !p.status_code || p.status_code >= 400;
      const hasSeo = p.seo_issues.length > 0;
      
      let color = '#9ca3af'; // default gray
      if (isStart) color = '#3b82f6'; // blue
      else if (isError) color = '#ef4444'; // red
      else if (is2xx) {
        if (hasSeo) color = '#f59e0b'; // amber/warning
        else color = '#10b981'; // green
      }
      
      // Node size scales with incoming links, capped
      const val = Math.min(Math.max(incoming * 0.5, 2), 10);
      
      graphNodes.push({
        id: p.url,
        name: p.title || p.url,
        url: p.url,
        status: p.status_code,
        val: isStart ? 12 : val,
        color,
        isOrphan,
        isError,
        is2xx,
        hasSeo,
        incoming,
        outgoing
      });
    });

    return { 
      nodes: graphNodes, 
      links: graphLinks,
      stats: { orphans: orphanCount, total: graphNodes.length, edges: graphLinks.length }
    };
  }, [pages, startUrl]);

  // Apply filters and search
  const filteredData = useMemo(() => {
    const searchLower = search.toLowerCase();
    
    const visibleNodes = nodes.filter(n => {
      if (searchLower && !n.url.toLowerCase().includes(searchLower) && !n.name.toLowerCase().includes(searchLower)) return false;
      
      if (filter === '2xx' && !n.is2xx) return false;
      if (filter === 'errors' && !n.isError) return false;
      if (filter === 'orphans' && !n.isOrphan) return false;
      
      return true;
    });

    const visibleNodeIds = new Set(visibleNodes.map(n => n.id));
    
    // Only show links where BOTH source and target are visible
    const visibleLinks = links.filter(l => 
      visibleNodeIds.has(typeof l.source === 'object' ? l.source.id : l.source) && 
      visibleNodeIds.has(typeof l.target === 'object' ? l.target.id : l.target)
    );

    return { nodes: visibleNodes, links: visibleLinks };
  }, [nodes, links, search, filter]);

  const paintNode = useCallback((node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
    const label = new URL(node.url).pathname || '/';
    const fontSize = 12 / globalScale;
    ctx.font = `${fontSize}px Sans-Serif`;
    const textWidth = ctx.measureText(label).width;
    const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2);

    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    if (globalScale > 2) {
      ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2 - node.val - 4, bckgDimensions[0], bckgDimensions[1]);
    }

    ctx.beginPath();
    ctx.arc(node.x, node.y, node.val, 0, 2 * Math.PI, false);
    ctx.fillStyle = node.color;
    ctx.fill();

    // Outline for SEO issues or Orphans
    if (node.hasSeo) {
      ctx.lineWidth = 1.5 / globalScale;
      ctx.strokeStyle = '#f59e0b';
      ctx.stroke();
    }
    if (node.isOrphan) {
       ctx.setLineDash([2 / globalScale, 2 / globalScale]);
       ctx.lineWidth = 2 / globalScale;
       ctx.strokeStyle = '#ef4444';
       ctx.stroke();
       ctx.setLineDash([]);
    }

    if (globalScale > 2) {
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#374151';
      ctx.fillText(label, node.x, node.y - node.val - 4);
    }
  }, []);

  return (
    <div className="flex flex-col h-[700px] bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden relative">
      {/* Toolbar */}
      <div className="absolute top-4 left-4 right-4 z-10 flex justify-between pointer-events-none">
        
        {/* Left Controls */}
        <div className="flex space-x-2 pointer-events-auto bg-white/90 backdrop-blur p-2 rounded-lg shadow-sm border border-gray-200">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-2.5 top-2 text-gray-400" />
            <input 
              type="text" 
              placeholder="Search URLs..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="pl-8 pr-3 py-1.5 text-sm border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500 w-48"
            />
          </div>
          <select 
            value={filter}
            onChange={e => setFilter(e.target.value as any)}
            className="text-sm border-gray-300 rounded py-1.5 pl-3 pr-8 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Pages</option>
            <option value="2xx">Healthy (2xx)</option>
            <option value="errors">Errors (4xx/5xx)</option>
            <option value="orphans">Orphan Pages</option>
          </select>
        </div>

        {/* Right Stats */}
        <div className="flex space-x-4 pointer-events-auto bg-white/90 backdrop-blur p-2 px-4 rounded-lg shadow-sm border border-gray-200 text-sm">
          <div className="flex items-center text-gray-700">
            <Globe className="w-4 h-4 mr-1.5 text-blue-500" /> 
            <span className="font-semibold mr-1">{stats.total}</span> Nodes
          </div>
          <div className="flex items-center text-gray-700">
            <LinkIcon className="w-4 h-4 mr-1.5 text-gray-400" /> 
            <span className="font-semibold mr-1">{stats.edges}</span> Edges
          </div>
          <div className="flex items-center text-red-700">
            <FileQuestion className="w-4 h-4 mr-1.5" /> 
            <span className="font-semibold mr-1">{stats.orphans}</span> Orphans
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-10 pointer-events-auto bg-white/90 backdrop-blur p-3 rounded-lg shadow-sm border border-gray-200 text-xs">
        <h4 className="font-semibold text-gray-700 mb-2">Legend</h4>
        <div className="space-y-1.5">
          <div className="flex items-center"><div className="w-3 h-3 rounded-full bg-[#3b82f6] mr-2"></div> Start URL</div>
          <div className="flex items-center"><div className="w-3 h-3 rounded-full bg-[#10b981] mr-2"></div> Healthy</div>
          <div className="flex items-center"><div className="w-3 h-3 rounded-full bg-[#f59e0b] mr-2"></div> SEO Issues</div>
          <div className="flex items-center"><div className="w-3 h-3 rounded-full bg-[#ef4444] mr-2"></div> Error (4xx/5xx)</div>
          <div className="flex items-center mt-2 pt-1 border-t border-gray-200"><div className="w-3 h-0 border-b-2 border-dashed border-red-500 mr-2"></div> Orphan</div>
        </div>
      </div>

      <div className="flex-1 w-full h-full cursor-grab active:cursor-grabbing">
        {filteredData.nodes.length > 0 ? (
          <ForceGraph2D
            graphData={filteredData}
            nodeLabel={(node: any) => `${node.url} (Status: ${node.status || 'Error'})`}
            nodeColor="color"
            nodeCanvasObject={paintNode}
            onNodeClick={(node) => onNodeClick(node.id as string)}
            linkDirectionalArrowLength={3.5}
            linkDirectionalArrowRelPos={1}
            linkColor={() => 'rgba(156, 163, 175, 0.3)'}
            cooldownTicks={100}
            minZoom={0.5}
            maxZoom={8}
            width={undefined} // Auto scale to parent
            height={undefined}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-500">
            No pages match the current filter.
          </div>
        )}
      </div>
    </div>
  );
}
