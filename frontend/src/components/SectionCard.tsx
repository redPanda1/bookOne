import type { ReactNode } from 'react';
import { Card, CardContent, Stack, Typography } from '@mui/material';

interface SectionCardProps {
  title?: string;
  subtitle?: string;
  children: ReactNode;
}

export function SectionCard({ title, subtitle, children }: SectionCardProps) {
  return (
    <Card>
      <CardContent sx={{ p: { xs: 2.25, md: 3 } }}>
        {title || subtitle ? (
          <Stack sx={{ gap: 0.5, mb: 2.25 }}>
            {title ? <Typography variant="h6">{title}</Typography> : null}
            {subtitle ? <Typography variant="body2">{subtitle}</Typography> : null}
          </Stack>
        ) : null}
        {children}
      </CardContent>
    </Card>
  );
}
