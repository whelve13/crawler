import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect } from 'vitest';
import CrawlForm from '../components/CrawlForm';
import * as api from '../services/api';

vi.mock('../services/api');
const mockedApi = vi.mocked(api);

describe('CrawlForm component', () => {
  it('submits correctly and calls onSuccess', async () => {
    mockedApi.startCrawl.mockResolvedValue({ task_id: '123', status: 'pending' });
    const onSuccess = vi.fn();

    render(<CrawlForm onSuccess={onSuccess} />);

    const urlInput = screen.getByPlaceholderText('https://example.com');
    const submitBtn = screen.getByRole('button', { name: /start/i });

    const user = userEvent.setup();
    await user.type(urlInput, 'https://test.com');
    await user.click(submitBtn);

    await waitFor(() => {
      expect(mockedApi.startCrawl).toHaveBeenCalledWith('https://test.com', 50, 3);
      expect(onSuccess).toHaveBeenCalled();
      expect(urlInput).toHaveValue(''); // Resets
    });
  });

  it('shows error if submission fails', async () => {
    mockedApi.startCrawl.mockRejectedValue(new Error('Failed'));
    const onSuccess = vi.fn();

    render(<CrawlForm onSuccess={onSuccess} />);

    const urlInput = screen.getByPlaceholderText('https://example.com');
    const submitBtn = screen.getByRole('button', { name: /start/i });

    const user = userEvent.setup();
    await user.type(urlInput, 'https://test.com');
    await user.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText(/Failed to start new crawl task./i)).toBeInTheDocument();
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });
});
