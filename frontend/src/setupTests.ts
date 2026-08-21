import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => {
  cleanup();
});
import { vi } from 'vitest';
vi.mock('react-force-graph-2d', () => ({ default: vi.fn(() => null) }));
