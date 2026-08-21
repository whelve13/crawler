import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import CrawlReportPage from './CrawlReport';
import * as api from '../services/api';
import { CrawlReport } from '../types/api';

vi.mock('../services/api');
const mockedApi = vi.mocked(api);

const mockReport: CrawlReport = {
  start_url: 'https://example.com',
  stats: {
    pages_crawled: 2,
    pages_failed: 0,
    duration_seconds: 1.5,
  },
  health_issues: [
    { url: 'https://example.com/bad', issue_type: 'broken_link', description: '404 Not Found' }
  ],
  pages: [
    {
      url: 'https://example.com',
      status_code: 200,
      title: 'Home',
      h1_tags: ['Welcome'],
      h2_tags: [],
      h3_tags: [],
      internal_links: ['https://example.com/about'],
      seo_issues: [
        { rule_id: 'MISSING_META_DESC', severity: 'warning', message: 'No meta description' }
      ]
    }
  ]
};

describe('CrawlReportPage component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state initially', () => {
    mockedApi.fetchCrawlReport.mockReturnValue(new Promise(() => {})); // Never resolves
    render(
      <MemoryRouter initialEntries={['/report/123']}>
        <Routes>
          <Route path="/report/:taskId" element={<CrawlReportPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText(/Loading report data.../i)).toBeInTheDocument();
  });

  it('renders report data when loaded', async () => {
    mockedApi.fetchCrawlReport.mockResolvedValue(mockReport);
    render(
      <MemoryRouter initialEntries={['/report/123']}>
        <Routes>
          <Route path="/report/:taskId" element={<CrawlReportPage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      // URL Title
      expect(screen.getByText('https://example.com')).toBeInTheDocument();
      // Status codes
      expect(screen.getByText('2xx Success')).toBeInTheDocument();
      // SEO Issues section
      expect(screen.getByText('MISSING_META_DESC')).toBeInTheDocument();
      // Broken links
      expect(screen.getByText('404 Not Found')).toBeInTheDocument();
      // Table data
      expect(screen.getByText('Home')).toBeInTheDocument();
    });
  });

  it('handles API errors', async () => {
    mockedApi.fetchCrawlReport.mockRejectedValue(new Error('Failed to load'));
    render(
      <MemoryRouter initialEntries={['/report/123']}>
        <Routes>
          <Route path="/report/:taskId" element={<CrawlReportPage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Failed to load report. Ensure the task is completed./i)).toBeInTheDocument();
    });
  });
});
