import { Alert } from '@mui/material';

interface InlineErrorStateProps {
  title?: string;
  message: string;
}

export function InlineErrorState({ title = 'Something needs attention', message }: InlineErrorStateProps) {
  return (
    <Alert severity="error" variant="standard">
      <strong>{title}</strong>
      <br />
      {message}
    </Alert>
  );
}
