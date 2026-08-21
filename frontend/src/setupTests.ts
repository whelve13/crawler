import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => {
  cleanup();
});
vi.mock('react-force-graph-2d', () => ({ default: vi.fn(() => null) }));
