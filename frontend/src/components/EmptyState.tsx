import { Box, Button, Stack, Typography } from '@mui/material';

interface EmptyStateProps {
  title: string;
  message: string;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({ title, message, actionLabel, onAction }: EmptyStateProps) {
  return (
    <Box sx={{ py: 5, px: 2, textAlign: 'center' }}>
      <Stack sx={{ alignItems: 'center', gap: 1.5 }}>
        <Typography variant="h6">{title}</Typography>
        <Typography variant="body2" sx={{ maxWidth: 520 }}>
          {message}
        </Typography>
        {actionLabel && onAction ? (
          <Button variant="outlined" onClick={onAction}>
            {actionLabel}
          </Button>
        ) : null}
      </Stack>
    </Box>
  );
}
