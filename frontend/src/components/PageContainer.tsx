import type { ReactNode } from 'react';
import { Grid, Typography } from '@mui/material';

interface PageContainerProps {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
  children: ReactNode;
}

export function PageContainer({ title, subtitle, actions, children }: PageContainerProps) {
  return (
    <Grid container sx={{ width: '100%', maxWidth: 1240, mx: 'auto' }}>
      <Grid size={12} sx={{ mb: 3 }}>
        <Grid container spacing={2} sx={{ alignItems: 'flex-start' }}>
          <Grid size={{ xs: 12, md: 'grow' }}>
            <Typography variant="h3">{title}</Typography>
            {subtitle ? (
              <Typography variant="body2" sx={{ mt: 0.75, maxWidth: 720 }}>
                {subtitle}
              </Typography>
            ) : null}
          </Grid>
          {actions ? (
            <Grid
              size={{ xs: 12, md: 'auto' }}
              sx={{
                display: 'flex',
                justifyContent: { xs: 'flex-start', md: 'flex-end' },
                alignItems: 'flex-start',
              }}
            >
              {actions}
            </Grid>
          ) : null}
        </Grid>
      </Grid>
      <Grid size={12}>{children}</Grid>
    </Grid>
  );
}
