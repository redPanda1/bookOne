import { alpha, createTheme } from '@mui/material/styles';

const PRIMARY_MAIN = '#1A4F43';
const PRIMARY_DARK = '#12382F';
const PRIMARY_LIGHT = '#256358';
const ACCENT_LIME = '#B8F15A';
const ACCENT_LIME_DARK = '#9FD63E';
const TEXT_PRIMARY = '#030E09';
const TEXT_PRIMARY_LIGHT = '#030E09CC';
const TEXT_SECONDARY = '#5E6E69';
const BACKGROUND_DEFAULT = '#F5F5F5';
const BACKGROUND_PAPER = '#FFFFFF';
const SIDEBAR_BG = '#FFFFFF';
const BORDER = '#E2E7DE';

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: PRIMARY_MAIN,
      light: PRIMARY_LIGHT,
      dark: PRIMARY_DARK,
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: ACCENT_LIME,
      light: '#D3F78F',
      dark: ACCENT_LIME_DARK,
      contrastText: TEXT_PRIMARY,
    },
    success: {
      main: '#2E7D5A',
      light: '#5FA37F',
      dark: '#1F5B40',
      contrastText: '#FFFFFF',
    },
    warning: {
      main: '#F5B51E',
      light: '#F9CE68',
      dark: '#C4900F',
      contrastText: TEXT_PRIMARY,
    },
    error: {
      main: '#EF4444',
      light: '#F47A7A',
      dark: '#C41F1F',
      contrastText: '#FFFFFF',
    },
    info: {
      main: '#2B7A78',
      light: '#5AA5A3',
      dark: '#1F5C5A',
      contrastText: '#FFFFFF',
    },
    text: {
      primary: TEXT_PRIMARY,
      secondary: TEXT_SECONDARY,
      disabled: '#93A19C',
    },
    background: {
      default: BACKGROUND_DEFAULT,
      paper: BACKGROUND_PAPER,
    },
    divider: BORDER,
    grey: {
      50: '#FBFCF9',
      100: '#F7F8F4',
      200: '#EEF1EA',
      300: '#E2E7DE',
      400: '#C5CEC7',
      500: '#93A19C',
      600: '#5E6E69',
      700: '#41504B',
      800: '#23312D',
      900: '#030E09',
    },
  },
  shape: {
    borderRadius: 8,
  },
  typography: {
    fontFamily: ['Onest', 'Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'sans-serif'].join(','),
    h1: { fontSize: '2.25rem', fontWeight: 800, lineHeight: 1.2, color: TEXT_PRIMARY },
    h2: { fontSize: '1.875rem', fontWeight: 800, lineHeight: 1.25, color: TEXT_PRIMARY },
    h3: { fontSize: '1.5rem', fontWeight: 600, lineHeight: 1.3, color: TEXT_PRIMARY_LIGHT },
    h4: { fontSize: '1.25rem', fontWeight: 600, lineHeight: 1.35, color: TEXT_PRIMARY_LIGHT },
    h5: { fontSize: '1.125rem', fontWeight: 600, lineHeight: 1.4, color: TEXT_PRIMARY },
    h6: { fontSize: '1rem', fontWeight: 700, lineHeight: 1.4, color: TEXT_PRIMARY },
    body1: { fontSize: '1rem', lineHeight: 1.6, color: TEXT_PRIMARY },
    body2: { fontSize: '0.875rem', lineHeight: 1.6, color: TEXT_SECONDARY },
    button: { textTransform: 'none', fontWeight: 700 },
    subtitle1: { color: TEXT_PRIMARY, fontWeight: 700 },
    subtitle2: { color: TEXT_SECONDARY, fontWeight: 700 },
    caption: { color: TEXT_SECONDARY },
    overline: {
      color: TEXT_SECONDARY,
      fontWeight: 700,
      letterSpacing: '0.08em',
      textTransform: 'uppercase',
    },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: BACKGROUND_DEFAULT,
          color: TEXT_PRIMARY,
        },
        '*': {
          boxSizing: 'border-box',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: BACKGROUND_PAPER,
          color: TEXT_PRIMARY,
          boxShadow: 'none',
          borderBottom: `1px solid ${BORDER}`,
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: SIDEBAR_BG,
          borderRight: `1px solid ${BORDER}`,
          color: TEXT_PRIMARY,
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          marginBottom: 2,
          color: TEXT_SECONDARY,
          '&.active': {
            backgroundColor: ACCENT_LIME,
            color: TEXT_PRIMARY,
            fontWeight: 700,
            '& .MuiListItemIcon-root': {
              color: TEXT_PRIMARY,
            },
            '& .MuiListItemText-primary': {
              fontWeight: 700,
              color: TEXT_PRIMARY,
            },
          },
          '&:hover': {
            backgroundColor: alpha(PRIMARY_MAIN, 0.06),
            color: TEXT_PRIMARY,
          },
        },
      },
    },
    MuiListItemIcon: {
      styleOverrides: {
        root: {
          color: TEXT_SECONDARY,
          minWidth: 36,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: BACKGROUND_PAPER,
          border: `1px solid ${BORDER}`,
          borderRadius: 8,
          boxShadow: '0 2px 10px rgba(3, 14, 9, 0.04)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
        outlined: {
          borderColor: BORDER,
        },
      },
    },
    MuiButton: {
      defaultProps: {
        disableElevation: true,
      },
      styleOverrides: {
        root: {
          borderRadius: 8,
          paddingInline: 16,
          paddingBlock: 10,
        },
        contained: {
          '&.MuiButton-containedPrimary': {
            backgroundColor: PRIMARY_MAIN,
            color: '#FFFFFF',
            '&:hover': {
              backgroundColor: PRIMARY_DARK,
            },
          },
          '&.MuiButton-containedSecondary': {
            backgroundColor: ACCENT_LIME,
            color: TEXT_PRIMARY,
            '&:hover': {
              backgroundColor: ACCENT_LIME_DARK,
            },
          },
        },
        outlined: {
          '&.MuiButton-outlinedPrimary': {
            borderColor: alpha(PRIMARY_MAIN, 0.28),
            color: PRIMARY_MAIN,
            '&:hover': {
              borderColor: PRIMARY_MAIN,
              backgroundColor: alpha(PRIMARY_MAIN, 0.04),
            },
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 700,
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          backgroundColor: '#FFFFFF',
          borderRadius: 8,
          '& .MuiOutlinedInput-notchedOutline': {
            borderColor: BORDER,
          },
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: alpha(PRIMARY_MAIN, 0.35),
          },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderColor: PRIMARY_MAIN,
            borderWidth: 1,
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottom: `1px solid ${BORDER}`,
        },
        head: {
          backgroundColor: alpha(PRIMARY_MAIN, 0.02),
          color: TEXT_SECONDARY,
          fontWeight: 700,
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          '&.MuiAlert-standardSuccess': {
            backgroundColor: alpha('#2E7D5A', 0.1),
            color: '#1F5B40',
          },
          '&.MuiAlert-standardWarning': {
            backgroundColor: alpha('#D4A11E', 0.14),
            color: '#7A5A08',
          },
          '&.MuiAlert-standardError': {
            backgroundColor: alpha('#C65A46', 0.12),
            color: '#8D3426',
          },
        },
      },
    },
  },
});
