import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import Dashboard from './Dashboard';
import * as api from '../services/api';

vi.mock('../services/api');

const mockedApi = vi.mocked(api);

describe('Dashboard component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders Dashboard correctly with empty tasks', async () => {
    mockedApi.fetchRecentTasks.mockResolvedValue([]);

    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );

    expect(screen.getByText('Website Auditor')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('No tasks found. Start a crawl above.')).toBeInTheDocument();
    });
  });

  it('renders a list of tasks', async () => {
    mockedApi.fetchRecentTasks.mockResolvedValue([
      {
        task_id: 'task-1234',
        status: 'completed',
        pages_crawled: 10,
        pages_failed: 0,
        duration_seconds: 5.5
      }
    ]);

    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('task...')).toBeInTheDocument();
      expect(screen.getByText('Completed')).toBeInTheDocument();
      expect(screen.getByText('View Report')).toBeInTheDocument();
    });
  });

  it('shows error banner on API failure', async () => {
    mockedApi.fetchRecentTasks.mockRejectedValue(new Error('Network error'));

    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Failed to reach backend API./i)).toBeInTheDocument();
    });
  });
});
