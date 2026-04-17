import { Box, CircularProgress, Stack, Typography } from '@mui/material';

interface LoadingStateProps {
  message?: string;
}

export function LoadingState({ message = 'Loading' }: LoadingStateProps) {
  return (
    <Box role="status" sx={{ py: 6 }}>
      <Stack sx={{ alignItems: 'center', gap: 2 }}>
        <CircularProgress size={28} />
        <Typography variant="body2">{message}</Typography>
      </Stack>
    </Box>
  );
}
