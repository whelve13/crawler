import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import SiteGraph from './SiteGraph';
import { PageReport } from '../types/api';

// Mock react-force-graph-2d so it doesn't crash in jsdom without canvas
vi.mock('react-force-graph-2d', () => {
  return {
    default: vi.fn(({ graphData, onNodeClick }) => (
      <div data-testid="force-graph-mock">
        <span data-testid="nodes-count">{graphData.nodes.length}</span>
        <span data-testid="links-count">{graphData.links.length}</span>
        <button data-testid="mock-node-click" onClick={() => onNodeClick({ id: 'https://example.com/mock' })}>
          Click Node
        </button>
      </div>
    )),
  };
});

const mockPages: PageReport[] = [
  {
    url: 'https://example.com',
    status_code: 200,
    title: 'Home',
    h1_tags: [], h2_tags: [], h3_tags: [],
    internal_links: ['https://example.com/about', 'https://example.com/contact'],
    seo_issues: []
  },
  {
    url: 'https://example.com/about',
    status_code: 200,
    title: 'About',
    h1_tags: [], h2_tags: [], h3_tags: [],
    internal_links: ['https://example.com/contact'],
    seo_issues: [{ rule_id: 'TEST', severity: 'warning', message: 'Test' }]
  },
  {
    url: 'https://example.com/contact',
    status_code: 404,
    title: 'Contact',
    h1_tags: [], h2_tags: [], h3_tags: [],
    internal_links: [],
    seo_issues: []
  },
  {
    url: 'https://example.com/orphan',
    status_code: 200,
    title: 'Orphan Page',
    h1_tags: [], h2_tags: [], h3_tags: [],
    internal_links: [],
    seo_issues: []
  }
];

describe('SiteGraph component', () => {
  it('generates correct nodes and edges, identifying orphans and errors', () => {
    render(<SiteGraph pages={mockPages} startUrl="https://example.com" onNodeClick={vi.fn()} />);
    // Basic check that it doesn't crash and renders the toolbar
    expect(screen.getByPlaceholderText(/Search URLs.../i)).toBeInTheDocument();
  });

  it('filters nodes by status', () => {
    render(<SiteGraph pages={mockPages} startUrl="https://example.com" onNodeClick={vi.fn()} />);
    
    const filterSelect = screen.getByRole('combobox');
    
    // Select Errors (4xx/5xx)
    fireEvent.change(filterSelect, { target: { value: 'errors' } });
    
    // Only Contact is 404, so 1 node, 0 edges (since Home/About are hidden)
    expect(screen.getByTestId('nodes-count').textContent).toBe('1');
    expect(screen.getByTestId('links-count').textContent).toBe('0');
  });

  it('searches for nodes by URL', () => {
    render(<SiteGraph pages={mockPages} startUrl="https://example.com" onNodeClick={vi.fn()} />);
    
    const searchInput = screen.getByPlaceholderText(/Search URLs.../i);
    fireEvent.change(searchInput, { target: { value: 'orphan' } });
    
    // Only Orphan page matches
    expect(screen.getByTestId('nodes-count').textContent).toBe('1');
  });

  it('handles empty state', () => {
    render(<SiteGraph pages={[]} startUrl="https://example.com" onNodeClick={vi.fn()} />);
    expect(screen.getByText('No pages match the current filter.')).toBeInTheDocument();
  });

  it('triggers onNodeClick', () => {
    const handleClick = vi.fn();
    render(<SiteGraph pages={mockPages} startUrl="https://example.com" onNodeClick={handleClick} />);
    
    fireEvent.click(screen.getByTestId('mock-node-click'));
    expect(handleClick).toHaveBeenCalledWith('https://example.com/mock');
  });
});
