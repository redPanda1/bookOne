import { Box, Button, Card, CardContent, Chip, Grid, Stack, Typography } from '@mui/material';
import {
  TrendingUpRounded as TrendingUpRoundedIcon,
  AccountBalanceRounded as AccountBalanceRoundedIcon,
  ReceiptLongRounded as ReceiptLongRoundedIcon,
  PaidRounded as PaidRoundedIcon,
} from '@mui/icons-material';
import ReactApexChart from 'react-apexcharts';
import type { ApexOptions } from 'apexcharts';
import { useNavigate } from 'react-router-dom';

import { PageContainer } from '../components/PageContainer';
import { SectionCard } from '../components/SectionCard';
import { useAppSelector } from '../hooks/redux';

const PRIMARY = '#1A4F43';
const LIME = '#B8F15A';
const LIME_LIGHT = '#D3F78F';

const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

const barOptions: ApexOptions = {
  chart: { type: 'bar', stacked: true, toolbar: { show: false }, fontFamily: 'Onest, Inter, sans-serif' },
  plotOptions: { bar: { borderRadius: 4, columnWidth: '52%' } },
  colors: [PRIMARY, LIME],
  dataLabels: { enabled: false },
  xaxis: { categories: months, axisBorder: { show: false }, axisTicks: { show: false } },
  yaxis: { labels: { formatter: (v: number) => `$${(v / 1000).toFixed(0)}k` } },
  legend: { position: 'top', horizontalAlign: 'left', fontFamily: 'Onest, Inter, sans-serif', fontWeight: 700 },
  grid: { borderColor: '#E2E7DE', strokeDashArray: 4 },
  tooltip: { y: { formatter: (v: number) => `$${v.toLocaleString()}` } },
};

const barSeries = [
  { name: 'Revenue', data: [38000, 42000, 55000, 47000, 61000, 73000, 58000, 64000, 70000, 66000, 72000, 89000] },
  { name: 'Expenses', data: [22000, 28000, 31000, 26000, 34000, 39000, 30000, 37000, 41000, 35000, 43000, 51000] },
];

const donutOptions: ApexOptions = {
  chart: { type: 'donut', fontFamily: 'Onest, Inter, sans-serif' },
  colors: [PRIMARY, LIME, LIME_LIGHT, '#256358'],
  labels: ['Asia', 'Americas', 'Europe', 'Other'],
  dataLabels: { enabled: false },
  legend: { position: 'bottom', fontFamily: 'Onest, Inter, sans-serif', fontWeight: 700 },
  plotOptions: { pie: { donut: { size: '70%', labels: { show: true, total: { show: true, label: 'Total', formatter: () => '$395.7k', fontFamily: 'Onest, Inter, sans-serif', fontWeight: 700, fontSize: '18px', color: '#030E09' } } } } },
  tooltip: { y: { formatter: (v: number) => `$${v.toLocaleString()}` } },
  stroke: { width: 0 },
};

const donutSeries = [165000, 120000, 75000, 35700];

const kpis = [
  { label: 'All-time Revenue', value: '$395.7k', delta: '+2.7%', positive: true, Icon: PaidRoundedIcon },
  { label: 'Active Journal Entries', value: '1,284', delta: '+18%', positive: true, Icon: ReceiptLongRoundedIcon },
  { label: 'Open Accounts', value: '47', delta: '-3', positive: false, Icon: AccountBalanceRoundedIcon },
];

export function DashboardPage() {
  const navigate = useNavigate();
  const session = useAppSelector((state) => state.auth.session);
  const orgName = session?.organization.name ?? 'your organisation';

  return (
    <PageContainer title="Dashboard">
      {/* Welcome banner */}
      <Card
        sx={{
          bgcolor: 'primary.main',
          color: 'primary.contrastText',
          mb: 3,
          overflow: 'hidden',
          position: 'relative',
        }}
      >
        <CardContent sx={{ p: { xs: 3, md: 4 } }}>
          <Grid container spacing={2} sx={{ alignItems: { xs: 'stretch', sm: 'center' } }}>
            <Grid size={{ xs: 12, sm: 'grow' }}>
              <Typography variant="h4" sx={{ color: '#fff', mb: 0.75 }}>
                Good morning, {orgName}
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.75)', maxWidth: 480 }}>
                Stay updated with your organisation's bookkeeping performance. Here's a quick snapshot of key statistics.
              </Typography>
            </Grid>
            <Grid size={{ xs: 12, sm: 'auto' }} sx={{ display: 'flex', alignItems: { sm: 'center' }, justifyContent: { xs: 'flex-start', sm: 'flex-end' } }}>
              <Button
                variant="contained"
                color="secondary"
                endIcon={<TrendingUpRoundedIcon />}
                onClick={() => navigate('/app/system-health')}
                sx={{ whiteSpace: 'nowrap', flexShrink: 0 }}
              >
                View backend health
              </Button>
            </Grid>
          </Grid>
          {/* Decorative circle */}
          <Box
            sx={{
              position: 'absolute',
              right: { xs: -60, md: 180 },
              top: -50,
              width: 200,
              height: 200,
              borderRadius: '50%',
              bgcolor: 'rgba(255,255,255,0.06)',
              pointerEvents: 'none',
            }}
          />
        </CardContent>
      </Card>

      {/* KPI row */}
      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        {kpis.map(({ label, value, delta, positive, Icon }) => (
          <Grid key={label} size={{ xs: 12, sm: 4 }}>
            <SectionCard>
              <Stack sx={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Box>
                  <Typography variant="overline">{label}</Typography>
                  <Typography variant="h4" sx={{ mt: 0.5 }}>{value}</Typography>
                  <Chip
                    label={delta}
                    size="small"
                    sx={{
                      mt: 1,
                      bgcolor: positive ? LIME : 'error.light',
                      color: positive ? 'text.primary' : 'error.dark',
                      fontWeight: 700,
                    }}
                  />
                </Box>
                <Box
                  sx={{
                    width: 44,
                    height: 44,
                    borderRadius: 2,
                    bgcolor: 'secondary.main',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Icon sx={{ color: 'text.primary', fontSize: 22 }} />
                </Box>
              </Stack>
            </SectionCard>
          </Grid>
        ))}
      </Grid>

      {/* Charts row */}
      <Grid container spacing={2.5}>
        <Grid size={{ xs: 12, md: 8 }}>
          <SectionCard title="Revenue vs Expenses" subtitle="Monthly breakdown — current financial year">
            <ReactApexChart
              type="bar"
              height={280}
              options={barOptions}
              series={barSeries}
            />
          </SectionCard>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <SectionCard title="Revenue by Region" subtitle="All-time distribution">
            <ReactApexChart
              type="donut"
              height={280}
              options={donutOptions}
              series={donutSeries}
            />
          </SectionCard>
        </Grid>
      </Grid>
    </PageContainer>
  );
}
