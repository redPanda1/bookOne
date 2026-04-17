import { Box, Chip, Divider, Grid, Stack, Typography, useTheme } from '@mui/material';
import { PageContainer } from '../components/PageContainer';
import { SectionCard } from '../components/SectionCard';

type SwatchProps = { label: string; hex: string; textColor?: string };

function Swatch({ label, hex, textColor = '#fff' }: SwatchProps) {
  return (
    <Stack
      sx={{
        borderRadius: 2,
        overflow: 'hidden',
        border: '1px solid',
        borderColor: 'divider',
        minWidth: 130,
      }}
    >
      <Box sx={{ bgcolor: hex, height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography variant="caption" sx={{ color: textColor, fontWeight: 700, fontSize: '0.7rem' }}>
          {hex.toUpperCase()}
        </Typography>
      </Box>
      <Box sx={{ px: 1.25, py: 0.75, bgcolor: 'background.paper' }}>
        <Typography variant="caption" sx={{ fontWeight: 700, display: 'block' }}>{label}</Typography>
      </Box>
    </Stack>
  );
}

function PaletteGroup({ title, swatches }: { title: string; swatches: SwatchProps[] }) {
  return (
    <Box>
      <Typography variant="overline" sx={{ mb: 1.5, display: 'block' }}>{title}</Typography>
      <Grid container spacing={1.5}>
        {swatches.map((s) => (
          <Grid key={s.label} size={{ xs: 6, sm: 4, md: 3 }}>
            <Swatch {...s} />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

export function ThemePage() {
  const t = useTheme();

  const paletteGroups = [
    {
      title: 'Primary',
      swatches: [
        { label: 'primary.main', hex: t.palette.primary.main },
        { label: 'primary.light', hex: t.palette.primary.light },
        { label: 'primary.dark', hex: t.palette.primary.dark },
        { label: 'primary.contrastText', hex: t.palette.primary.contrastText, textColor: t.palette.primary.main },
      ],
    },
    {
      title: 'Secondary — Accent Lime',
      swatches: [
        { label: 'secondary.main', hex: t.palette.secondary.main, textColor: t.palette.text.primary },
        { label: 'secondary.light', hex: t.palette.secondary.light, textColor: t.palette.text.primary },
        { label: 'secondary.dark', hex: t.palette.secondary.dark, textColor: t.palette.text.primary },
      ],
    },
    {
      title: 'Success',
      swatches: [
        { label: 'success.main', hex: t.palette.success.main },
        { label: 'success.light', hex: t.palette.success.light },
        { label: 'success.dark', hex: t.palette.success.dark },
      ],
    },
    {
      title: 'Warning',
      swatches: [
        { label: 'warning.main', hex: t.palette.warning.main, textColor: t.palette.text.primary },
        { label: 'warning.light', hex: t.palette.warning.light, textColor: t.palette.text.primary },
        { label: 'warning.dark', hex: t.palette.warning.dark },
      ],
    },
    {
      title: 'Error',
      swatches: [
        { label: 'error.main', hex: t.palette.error.main },
        { label: 'error.light', hex: t.palette.error.light },
        { label: 'error.dark', hex: t.palette.error.dark },
      ],
    },
    {
      title: 'Info',
      swatches: [
        { label: 'info.main', hex: t.palette.info.main },
        { label: 'info.light', hex: t.palette.info.light },
        { label: 'info.dark', hex: t.palette.info.dark },
      ],
    },
    {
      title: 'Text',
      swatches: [
        { label: 'text.primary', hex: t.palette.text.primary },
        { label: 'text.secondary', hex: t.palette.text.secondary },
        { label: 'text.disabled', hex: t.palette.text.disabled },
      ],
    },
    {
      title: 'Background & Surface',
      swatches: [
        { label: 'background.default', hex: t.palette.background.default, textColor: t.palette.text.primary },
        { label: 'background.paper', hex: t.palette.background.paper, textColor: t.palette.text.primary },
        { label: 'divider', hex: t.palette.divider, textColor: t.palette.text.primary },
      ],
    },
    {
      title: 'Grey scale',
      swatches: Object.entries(t.palette.grey).map(([key, hex]) => ({
        label: `grey.${key}`,
        hex,
        textColor: Number(key) >= 600 ? '#fff' : t.palette.text.primary,
      })),
    },
  ];

  const typographyVariants: Array<{
    variant: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'subtitle1' | 'subtitle2' | 'body1' | 'body2' | 'button' | 'caption' | 'overline';
    label: string;
    sample: string;
  }> = [
    { variant: 'h1', label: 'h1 — 2.25 rem / 800', sample: 'The quick brown fox' },
    { variant: 'h2', label: 'h2 — 1.875 rem / 800', sample: 'The quick brown fox' },
    { variant: 'h3', label: 'h3 — 1.5 rem / 700', sample: 'The quick brown fox' },
    { variant: 'h4', label: 'h4 — 1.25 rem / 700', sample: 'The quick brown fox jumps over the lazy dog' },
    { variant: 'h5', label: 'h5 — 1.125 rem / 700', sample: 'The quick brown fox jumps over the lazy dog' },
    { variant: 'h6', label: 'h6 — 1 rem / 700', sample: 'The quick brown fox jumps over the lazy dog' },
    { variant: 'subtitle1', label: 'subtitle1 — 1 rem / 700', sample: 'The quick brown fox jumps over the lazy dog' },
    { variant: 'subtitle2', label: 'subtitle2 — 0.875 rem / 700', sample: 'The quick brown fox jumps over the lazy dog' },
    { variant: 'body1', label: 'body1 — 1 rem / 400', sample: 'The quick brown fox jumps over the lazy dog. Used for paragraphs and main content.' },
    { variant: 'body2', label: 'body2 — 0.875 rem / 400', sample: 'The quick brown fox jumps over the lazy dog. Used for secondary content and descriptions.' },
    { variant: 'button', label: 'button — 0.875 rem / 700', sample: 'Button Label' },
    { variant: 'caption', label: 'caption — 0.75 rem / 400', sample: 'Caption text — metadata, timestamps, helper text' },
    { variant: 'overline', label: 'overline — 0.75 rem / 700 uppercase', sample: 'Section heading label' },
  ];

  const chipVariants: Array<{ label: string; color: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info' }> = [
    { label: 'default', color: 'default' },
    { label: 'primary', color: 'primary' },
    { label: 'secondary', color: 'secondary' },
    { label: 'success', color: 'success' },
    { label: 'warning', color: 'warning' },
    { label: 'error', color: 'error' },
    { label: 'info', color: 'info' },
  ];

  return (
    <PageContainer title="Theme Reference" subtitle={`Font: ${t.typography.fontFamily?.split(',')[0]} · Border radius: ${t.shape.borderRadius}px · Mode: ${t.palette.mode}`}>
      <Grid container spacing={3}>

        {/* Typography */}
        <Grid size={{ xs: 12 }}>
          <SectionCard title="Typography" subtitle="All variants — Onest font family">
            <Stack divider={<Divider />} spacing={0}>
              {typographyVariants.map(({ variant, label, sample }) => (
                <Grid
                  key={variant}
                  container
                  spacing={{ xs: 0.25, sm: 2 }}
                  sx={{
                    py: 1.75,
                    alignItems: { xs: 'flex-start', sm: 'baseline' },
                  }}
                >
                  <Grid size={{ xs: 12, sm: 3, md: 3 }}>
                    <Typography variant="caption" sx={{ color: 'text.disabled', fontFamily: 'monospace' }}>
                      {label}
                    </Typography>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 9, md: 9 }}>
                    <Typography variant={variant}>{sample}</Typography>
                  </Grid>
                </Grid>
              ))}
            </Stack>
          </SectionCard>
        </Grid>

        {/* Colour palette */}
        <Grid size={{ xs: 12 }}>
          <SectionCard title="Colour palette" subtitle="All semantic tokens resolved from the live theme">
            <Stack spacing={3}>
              {paletteGroups.map((group) => (
                <PaletteGroup key={group.title} title={group.title} swatches={group.swatches} />
              ))}
            </Stack>
          </SectionCard>
        </Grid>

        {/* Chips */}
        <Grid size={{ xs: 12, md: 6 }}>
          <SectionCard title="Chips — filled" subtitle="Color variants">
            <Stack direction="row" sx={{ flexWrap: 'wrap', gap: 1 }}>
              {chipVariants.map(({ label, color }) => (
                <Chip key={label} label={label} color={color} />
              ))}
            </Stack>
          </SectionCard>
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <SectionCard title="Chips — outlined" subtitle="Color variants">
            <Stack direction="row" sx={{ flexWrap: 'wrap', gap: 1 }}>
              {chipVariants.map(({ label, color }) => (
                <Chip key={label} label={label} color={color} variant="outlined" />
              ))}
            </Stack>
          </SectionCard>
        </Grid>

        {/* Shape & spacing */}
        <Grid size={{ xs: 12, md: 6 }}>
          <SectionCard title="Border radius" subtitle="theme.shape.borderRadius">
            <Stack direction="row" sx={{ gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
              {[0, 4, 8, 12, 16, 24, 9999].map((r) => (
                <Box key={r} sx={{ width: 64, height: 64, bgcolor: 'primary.main', borderRadius: `${r}px`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Typography variant="caption" sx={{ color: '#fff', fontWeight: 700 }}>{r}px</Typography>
                </Box>
              ))}
            </Stack>
          </SectionCard>
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <SectionCard title="Elevation / shadows" subtitle="Box shadow samples">
            <Stack direction="row" sx={{ gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
              {[1, 2, 4, 8, 16].map((e) => (
                <Box key={e} sx={{ width: 72, height: 72, bgcolor: 'background.paper', boxShadow: e, borderRadius: 2, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Typography variant="caption" sx={{ fontWeight: 700 }}>dp{e}</Typography>
                </Box>
              ))}
            </Stack>
          </SectionCard>
        </Grid>

      </Grid>
    </PageContainer>
  );
}
