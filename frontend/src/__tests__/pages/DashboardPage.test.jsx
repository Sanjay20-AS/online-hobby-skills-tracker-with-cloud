import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DashboardPage } from '../../pages';

// Mock API
vi.mock('../../services', () => ({
  api: {
    get: vi.fn().mockResolvedValue({
      data: {
        total_hobbies: 5,
        total_skills: 10,
        total_practice_hours: 50.5,
        total_goals: 3,
        completed_milestones: 2,
        public_posts: 1,
      },
    }),
  },
}));

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders dashboard title', async () => {
    render(<DashboardPage />);
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('displays analytics stats', async () => {
    render(<DashboardPage />);
    // Wait for data to load
    await vi.waitFor(() => {
      expect(screen.getByText('Total Hobbies')).toBeInTheDocument();
    });
    expect(screen.getByText('Total Skills')).toBeInTheDocument();
    expect(screen.getByText('Practice Hours')).toBeInTheDocument();
  });
});
