import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Input } from '../../components';

describe('Input', () => {
  it('renders input with label', () => {
    render(<Input label="Email" />);
    expect(screen.getByText('Email')).toBeInTheDocument();
  });

  it('shows error message', () => {
    render(<Input label="Email" error="Invalid email" />);
    expect(screen.getByText('Invalid email')).toBeInTheDocument();
  });

  it('updates value on change', async () => {
    const user = userEvent.setup();
    const { container } = render(<Input type="text" />);
    const input = container.querySelector('input');
    await user.type(input, 'test');
    expect(input.value).toBe('test');
  });

  it('marks required fields', () => {
    render(<Input label="Username" required />);
    expect(screen.getByText('*')).toBeInTheDocument();
  });
});
