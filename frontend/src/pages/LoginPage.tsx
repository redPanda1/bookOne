import { FormEvent, useEffect, useState } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { Box, Button, Card, CardContent, Grid, Stack, TextField, Typography } from '@mui/material';

import { LOGIN_WITH_DEV_TOKEN } from '../store/authSlice';
import { USER_MESSAGE } from '../store/statusSlice';
import { InlineErrorState } from '../components/InlineErrorState';
import { LoadingState } from '../components/LoadingState';
import { useAppDispatch, useAppSelector } from '../hooks/redux';

interface LocationState {
  from?: {
    pathname?: string;
  };
}

export function LoginPage() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { status, error, hasBootstrapped } = useAppSelector((state) => state.auth);
  const [token, setToken] = useState('');

  const redirectTo = (location.state as LocationState | null)?.from?.pathname ?? '/app/dashboard';

  useEffect(() => {
    if (status === 'authenticated') {
      navigate(redirectTo, { replace: true });
    }
  }, [navigate, redirectTo, status]);

  if (!hasBootstrapped || status === 'loading' && !token) {
    return <LoadingState message="Preparing sign in" />;
  }

  if (status === 'authenticated') {
    return <Navigate to={redirectTo} replace />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const result = await dispatch(LOGIN_WITH_DEV_TOKEN(token));
    if (LOGIN_WITH_DEV_TOKEN.fulfilled.match(result)) {
      dispatch(USER_MESSAGE({ message: 'Signed in to BookOne', type: 'SUCCESS' }));
      navigate(redirectTo, { replace: true });
    }
  }

  return (
    <Grid
      container
      sx={{
        minHeight: '100vh',
        alignItems: 'center',
        justifyContent: 'center',
        px: 2,
        py: 5,
        background: 'linear-gradient(135deg, #F7F8F4 0%, #EEF1EA 100%)',
      }}
    >
      <Grid size={{ xs: 12, sm: 10, md: 6, lg: 5 }} sx={{ width: '100%', maxWidth: 460 }}>
        <Card sx={{ width: '100%' }}>
          <CardContent sx={{ p: { xs: 3, sm: 4 } }}>
            <Stack spacing={3}>
              <Stack spacing={1}>
                <Typography variant="overline">BookOne</Typography>
                <Typography variant="h4">Sign in</Typography>
                <Typography variant="body2">
                  Enter a development bearer token. This keeps the frontend auth shell honest while Cognito sign-in is completed.
                </Typography>
              </Stack>

              {error ? <InlineErrorState title="Sign in failed" message={error.message} /> : null}

              <Box component="form" onSubmit={handleSubmit}>
                <Stack spacing={2.5}>
                  <TextField
                    label="Bearer token"
                    value={token}
                    onChange={(event) => setToken(event.target.value)}
                    placeholder="Paste a Cognito or development token"
                    autoComplete="off"
                    multiline
                    minRows={3}
                    required
                  />
                  <Button type="submit" variant="contained" size="large" disabled={status === 'loading'}>
                    {status === 'loading' ? 'Signing in...' : 'Continue'}
                  </Button>
                </Stack>
              </Box>
            </Stack>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}
