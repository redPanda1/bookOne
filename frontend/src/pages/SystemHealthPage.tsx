import { useEffect } from 'react';
import { Alert, Button, Chip, Stack, Typography } from '@mui/material';

import { FETCH_DATABASE_HEALTH } from '../store/healthSlice';
import { USER_MESSAGE } from '../store/statusSlice';
import { InlineErrorState } from '../components/InlineErrorState';
import { LoadingState } from '../components/LoadingState';
import { PageContainer } from '../components/PageContainer';
import { SectionCard } from '../components/SectionCard';
import { useAppDispatch, useAppSelector } from '../hooks/redux';

export function SystemHealthPage() {
  const dispatch = useAppDispatch();
  const health = useAppSelector((state) => state.health);

  useEffect(() => {
    if (health.status === 'idle') {
      void dispatch(FETCH_DATABASE_HEALTH());
    }
  }, [dispatch, health.status]);

  async function handleRefresh() {
    const result = await dispatch(FETCH_DATABASE_HEALTH());
    if (FETCH_DATABASE_HEALTH.fulfilled.match(result)) {
      dispatch(USER_MESSAGE({ message: 'Backend health check passed', type: 'SUCCESS' }));
    }
  }

  return (
    <PageContainer
      title="System Health"
      subtitle="Protected backend test page using the shared API client and Redux thunk pattern."
      actions={
        <Button variant="contained" onClick={handleRefresh} disabled={health.status === 'loading'}>
          Refresh
        </Button>
      }
    >
      <SectionCard title="Database connectivity" subtitle="GET /health/db">
        {health.status === 'loading' ? <LoadingState message="Checking protected backend endpoint" /> : null}

        {health.status === 'failed' && health.error ? (
          <InlineErrorState title="Health check failed" message={health.error.message} />
        ) : null}

        {health.status === 'succeeded' && health.data ? (
          <Stack spacing={2}>
            <Alert severity="success">The deployed backend is reachable and can connect to Aurora.</Alert>
            <Stack sx={{ flexDirection: { xs: 'column', sm: 'row' }, gap: 1.5, alignItems: { xs: 'flex-start', sm: 'center' } }}>
              <Chip color="success" label={health.data.status} />
              <Typography variant="body2">Database OK: {health.data.database.ok ? 'Yes' : 'No'}</Typography>
              {health.checkedAt ? <Typography variant="body2">Checked at {new Date(health.checkedAt).toLocaleString()}</Typography> : null}
            </Stack>
          </Stack>
        ) : null}
      </SectionCard>
    </PageContainer>
  );
}
