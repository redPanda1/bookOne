import { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import {
  AppBar,
  Avatar,
  Box,
  Button,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Stack,
  Toolbar,
  Tooltip,
  Typography,
} from '@mui/material';
import {
  DashboardRounded as DashboardRoundedIcon,
  MonitorHeartRounded as MonitorHeartRoundedIcon,
  ReceiptLongRounded as ReceiptLongRoundedIcon,
  BarChartRounded as BarChartRoundedIcon,
  SettingsRounded as SettingsRoundedIcon,
  PaletteRounded as PaletteRoundedIcon,
  ChevronLeftRounded as ChevronLeftRoundedIcon,
  ChevronRightRounded as ChevronRightRoundedIcon,
} from '@mui/icons-material';

import { LOGOUT } from '../store/authSlice';
import { USER_MESSAGE } from '../store/statusSlice';
import { useAppDispatch, useAppSelector } from '../hooks/redux';

const DRAWER_EXPANDED = 268;
const DRAWER_COLLAPSED = 72;

const navItems = [
  { label: 'Dashboard', to: '/app/dashboard', Icon: DashboardRoundedIcon },
  { label: 'System Health', to: '/app/system-health', Icon: MonitorHeartRoundedIcon },
  { label: 'Journal Entries', to: '/app/journal-entries', Icon: ReceiptLongRoundedIcon },
  { label: 'Reports', to: '/app/reports', Icon: BarChartRoundedIcon },
  { label: 'Settings', to: '/app/settings', Icon: SettingsRoundedIcon },
  { label: 'Theme', to: '/app/theme', Icon: PaletteRoundedIcon },
];

export function AppShell() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const session = useAppSelector((state) => state.auth.session);
  const [collapsed, setCollapsed] = useState(false);

  const drawerWidth = collapsed ? DRAWER_COLLAPSED : DRAWER_EXPANDED;

  function handleLogout() {
    dispatch(LOGOUT());
    dispatch(USER_MESSAGE({ message: 'Signed out', type: 'INFO' }));
    navigate('/login', { replace: true });
  }

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          display: { xs: 'none', md: 'block' },
          transition: (t) => t.transitions.create('width', { easing: t.transitions.easing.sharp, duration: t.transitions.duration.enteringScreen }),
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            overflowX: 'hidden',
            transition: (t) => t.transitions.create('width', { easing: t.transitions.easing.sharp, duration: t.transitions.duration.enteringScreen }),
          },
        }}
      >
        <Stack sx={{ height: '100%' }}>
          {/* Logo / brand area */}
          <Box
            sx={{
              px: collapsed ? 1.5 : 3,
              py: 2.5,
              display: 'flex',
              alignItems: 'center',
              justifyContent: collapsed ? 'center' : 'space-between',
              minHeight: 64,
            }}
          >
            {!collapsed && (
              <Box>
                <Typography variant="h5" sx={{ lineHeight: 1.2 }}>BookOne</Typography>
                <Typography variant="caption">Finance workspace</Typography>
              </Box>
            )}
            <Tooltip title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'} placement="right">
              <IconButton
                size="small"
                onClick={() => setCollapsed((c) => !c)}
                sx={{ color: 'text.secondary', ml: collapsed ? 0 : 'auto' }}
              >
                {collapsed ? <ChevronRightRoundedIcon fontSize="small" /> : <ChevronLeftRoundedIcon fontSize="small" />}
              </IconButton>
            </Tooltip>
          </Box>

          <Divider />

          {/* Nav items */}
          <List sx={{ px: 1, py: 1.5, flexGrow: 1 }}>
            {navItems.map(({ label, to, Icon }) => (
              <Tooltip key={to} title={collapsed ? label : ''} placement="right" arrow>
                <ListItemButton
                  component={NavLink}
                  to={to}
                  sx={{
                    mb: 0.5,
                    borderRadius: 2,
                    justifyContent: collapsed ? 'center' : 'flex-start',
                    px: collapsed ? 1.25 : 1.5,
                    minHeight: 44,
                  }}
                >
                  <ListItemIcon
                    sx={{
                      minWidth: collapsed ? 0 : 36,
                      justifyContent: 'center',
                      mr: collapsed ? 0 : 0.5,
                    }}
                  >
                    <Icon fontSize="small" />
                  </ListItemIcon>
                  {!collapsed && <ListItemText primary={label} />}
                </ListItemButton>
              </Tooltip>
            ))}
          </List>

          <Divider />

          {/* Sign out */}
          <Box sx={{ p: collapsed ? 1 : 2, py: 2 }}>
            {collapsed ? (
              <Tooltip title="Sign out" placement="right">
                <IconButton onClick={handleLogout} sx={{ color: 'text.secondary', width: '100%', borderRadius: 2 }}>
                  <SettingsRoundedIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            ) : (
              <Button fullWidth variant="outlined" onClick={handleLogout}>
                Sign out
              </Button>
            )}
          </Box>
        </Stack>
      </Drawer>

      {/* Main content */}
      <Box
        sx={{
          flexGrow: 1,
          minWidth: 0,
          transition: (t) => t.transitions.create('margin', { easing: t.transitions.easing.sharp, duration: t.transitions.duration.enteringScreen }),
        }}
      >
        <AppBar position="sticky" color="inherit">
          <Toolbar sx={{ gap: 2, justifyContent: 'space-between' }}>
            <Box>
              <Typography variant="subtitle1">{session?.organization.name ?? 'BookOne'}</Typography>
              <Typography variant="caption">Finance workspace</Typography>
            </Box>
            <Stack sx={{ flexDirection: 'row', alignItems: 'center', gap: 1.5 }}>
              <Avatar sx={{ width: 34, height: 34, bgcolor: 'primary.main', fontSize: 14 }}>
                {(session?.user.email ?? 'B').slice(0, 1).toUpperCase()}
              </Avatar>
              <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
                <Typography variant="body2" color="text.primary">
                  {session?.user.email ?? 'Signed in'}
                </Typography>
                <Typography variant="caption">{session?.user.id ?? 'User'}</Typography>
              </Box>
            </Stack>
          </Toolbar>
        </AppBar>
        <Box component="main" sx={{ p: { xs: 2, md: 3 }, minHeight: 'calc(100vh - 64px)' }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}
