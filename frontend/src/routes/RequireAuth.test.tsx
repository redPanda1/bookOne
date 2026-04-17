import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { RequireAuth } from './RequireAuth';
import { renderWithStore } from '../test/renderWithStore';

describe('RequireAuth', () => {
  it('redirects unauthenticated users to login', async () => {
    renderWithStore(
      <MemoryRouter initialEntries={['/app/dashboard']}>
        <Routes>
          <Route
            path="/app/dashboard"
            element={
              <RequireAuth>
                <div>Protected content</div>
              </RequireAuth>
            }
          />
          <Route path="/login" element={<div>Login page</div>} />
        </Routes>
      </MemoryRouter>,
      {
        auth: {
          token: null,
          session: null,
          status: 'unauthenticated',
          error: null,
          hasBootstrapped: true,
        },
        health: {
          status: 'idle',
          data: null,
          error: null,
          checkedAt: null,
        },
      },
    );

    expect(await screen.findByText('Login page')).toBeInTheDocument();
  });
});
