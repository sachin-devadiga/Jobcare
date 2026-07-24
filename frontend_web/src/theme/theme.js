'use client';
import { createTheme } from '@mui/material/styles';

const commonTypography = {
  fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  h1: { fontWeight: 700, fontSize: '2rem', lineHeight: 1.2 },
  h2: { fontWeight: 700, fontSize: '1.75rem', lineHeight: 1.25 },
  h3: { fontWeight: 600, fontSize: '1.5rem', lineHeight: 1.3 },
  h4: { fontWeight: 600, fontSize: '1.25rem', lineHeight: 1.35 },
  h5: { fontWeight: 600, fontSize: '1.1rem', lineHeight: 1.4 },
  h6: { fontWeight: 600, fontSize: '1rem', lineHeight: 1.45 },
  subtitle1: { fontWeight: 500, fontSize: '1rem', lineHeight: 1.5 },
  subtitle2: { fontWeight: 500, fontSize: '0.875rem', lineHeight: 1.5 },
  body1: { fontSize: '1rem', lineHeight: 1.6 },
  body2: { fontSize: '0.875rem', lineHeight: 1.6 },
  button: { fontWeight: 600, fontSize: '0.875rem', textTransform: 'none' },
  caption: { fontSize: '0.75rem', lineHeight: 1.5 },
  overline: { fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' },
};

const commonComponents = {
  MuiCssBaseline: {
    styleOverrides: {
      body: { scrollbarWidth: 'thin' },
      '*::-webkit-scrollbar': { width: '6px', height: '6px' },
      '*::-webkit-scrollbar-track': { background: 'transparent' },
      '*::-webkit-scrollbar-thumb': { background: 'rgba(0,0,0,0.15)', borderRadius: '3px' },
    },
  },
  MuiButton: {
    styleOverrides: {
      root: {
        borderRadius: 12,
        padding: '10px 24px',
        transition: 'all 0.2s ease-in-out',
        '&:hover': { transform: 'translateY(-1px)', boxShadow: '0 4px 12px rgba(0,0,0,0.15)' },
      },
      contained: { boxShadow: '0 2px 8px rgba(0,0,0,0.1)' },
      outlined: { borderWidth: 2, '&:hover': { borderWidth: 2 } },
      sizeSmall: { padding: '6px 16px', fontSize: '0.8125rem' },
      sizeLarge: { padding: '14px 32px', fontSize: '1rem' },
    },
  },
  MuiCard: {
    styleOverrides: {
      root: {
        borderRadius: 16,
        boxShadow: '0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)',
        transition: 'all 0.3s ease-in-out',
        backdropFilter: 'blur(20px)',
        '&:hover': { boxShadow: '0 10px 40px rgba(0,0,0,0.1)' },
      },
    },
  },
  MuiPaper: {
    styleOverrides: {
      root: { borderRadius: 16 },
      elevation1: { boxShadow: '0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)' },
      elevation2: { boxShadow: '0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.06)' },
      elevation3: { boxShadow: '0 10px 15px rgba(0,0,0,0.08), 0 4px 6px rgba(0,0,0,0.05)' },
    },
  },
  MuiTextField: {
    styleOverrides: {
      root: {
        '& .MuiOutlinedInput-root': {
          borderRadius: 12,
          transition: 'all 0.2s ease',
          '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(99,102,241,0.5)' },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderWidth: 2 },
        },
        '& .MuiInputLabel-root': { fontWeight: 500 },
        '& .MuiFormHelperText-root': { marginLeft: 0 },
      },
    },
  },
  MuiSelect: {
    styleOverrides: {
      root: { borderRadius: 12 },
    },
  },
  MuiChip: {
    styleOverrides: {
      root: { borderRadius: 8, fontWeight: 500, fontSize: '0.8125rem' },
      filled: { '&:hover': { filter: 'brightness(0.95)' } },
    },
  },
  MuiTableHead: {
    styleOverrides: {
      root: {
        '& .MuiTableCell-head': {
          fontWeight: 600,
          backgroundColor: 'rgba(99,102,241,0.04)',
          fontSize: '0.8125rem',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
        },
      },
    },
  },
  MuiTableCell: {
    styleOverrides: {
      root: { padding: '14px 16px', borderBottomColor: 'rgba(0,0,0,0.06)' },
    },
  },
  MuiTableRow: {
    styleOverrides: {
      root: { transition: 'background 0.2s', '&:hover': { backgroundColor: 'rgba(99,102,241,0.02)' } },
    },
  },
  MuiTab: {
    styleOverrides: {
      root: { borderRadius: 8, minHeight: 42, fontWeight: 500 },
    },
  },
  MuiTabs: {
    styleOverrides: {
      indicator: { borderRadius: 4, height: 3 },
    },
  },
  MuiDialog: {
    styleOverrides: {
      paper: { borderRadius: 20, padding: 8 },
    },
  },
  MuiAlert: {
    styleOverrides: {
      root: { borderRadius: 12 },
      standardSuccess: { backgroundColor: 'rgba(34,197,94,0.1)', color: '#059669' },
      standardError: { backgroundColor: 'rgba(239,68,68,0.1)', color: '#DC2626' },
      standardWarning: { backgroundColor: 'rgba(234,179,8,0.1)', color: '#D97706' },
      standardInfo: { backgroundColor: 'rgba(59,130,246,0.1)', color: '#2563EB' },
    },
  },
  MuiAvatar: {
    styleOverrides: {
      root: { fontWeight: 600, fontSize: '0.875rem' },
    },
  },
  MuiTooltip: {
    styleOverrides: {
      tooltip: { borderRadius: 8, padding: '8px 12px', fontSize: '0.75rem' },
    },
  },
  MuiMenu: {
    styleOverrides: {
      paper: { borderRadius: 12, boxShadow: '0 10px 40px rgba(0,0,0,0.12)' },
    },
  },
  MuiListItemButton: {
    styleOverrides: {
      root: { borderRadius: 12, margin: '2px 8px', transition: 'all 0.2s' },
    },
  },
  MuiSwitch: {
    styleOverrides: {
      root: { width: 44, height: 24, padding: 0, '& .MuiSwitch-switchBase': { padding: 0, margin: 2, transitionDuration: '300ms' } },
      thumb: { width: 20, height: 20, boxShadow: '0 2px 4px rgba(0,0,0,0.2)' },
      track: { borderRadius: 12, opacity: 1 },
    },
  },
  MuiLinearProgress: {
    styleOverrides: {
      root: { borderRadius: 4 },
      bar: { borderRadius: 4 },
    },
  },
};

const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#6366F1', light: '#818CF8', dark: '#4F46E5', contrastText: '#FFFFFF' },
    secondary: { main: '#8B5CF6', light: '#A78BFA', dark: '#7C3AED', contrastText: '#FFFFFF' },
    error: { main: '#EF4444', light: '#F87171', dark: '#DC2626' },
    warning: { main: '#F59E0B', light: '#FBBF24', dark: '#D97706' },
    info: { main: '#3B82F6', light: '#60A5FA', dark: '#2563EB' },
    success: { main: '#22C55E', light: '#4ADE80', dark: '#16A34A' },
    background: { default: '#F8FAFC', paper: '#FFFFFF' },
    text: { primary: '#1E293B', secondary: '#64748B', disabled: '#94A3B8' },
    divider: 'rgba(0,0,0,0.06)',
    action: { active: '#6366F1', hover: 'rgba(99,102,241,0.04)', selected: 'rgba(99,102,241,0.08)', disabled: 'rgba(0,0,0,0.26)' },
  },
  typography: commonTypography,
  shape: { borderRadius: 12 },
  components: {
    ...commonComponents,
    MuiAppBar: {
      styleOverrides: {
        root: { backgroundColor: 'rgba(255,255,255,0.8)', backdropFilter: 'blur(20px)', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: { backgroundColor: '#FFFFFF', borderRight: '1px solid rgba(0,0,0,0.06)' },
      },
    },
  },
});

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#818CF8', light: '#A5B4FC', dark: '#6366F1', contrastText: '#FFFFFF' },
    secondary: { main: '#A78BFA', light: '#C4B5FD', dark: '#8B5CF6', contrastText: '#FFFFFF' },
    error: { main: '#F87171', light: '#FCA5A5', dark: '#EF4444' },
    warning: { main: '#FBBF24', light: '#FCD34D', dark: '#F59E0B' },
    info: { main: '#60A5FA', light: '#93C5FD', dark: '#3B82F6' },
    success: { main: '#4ADE80', light: '#86EFAC', dark: '#22C55E' },
    background: { default: '#0F172A', paper: '#1E293B' },
    text: { primary: '#F1F5F9', secondary: '#94A3B8', disabled: '#64748B' },
    divider: 'rgba(255,255,255,0.06)',
    action: { active: '#818CF8', hover: 'rgba(129,140,248,0.08)', selected: 'rgba(129,140,248,0.12)', disabled: 'rgba(255,255,255,0.3)' },
  },
  typography: commonTypography,
  shape: { borderRadius: 12 },
  components: {
    ...commonComponents,
    MuiAppBar: {
      styleOverrides: {
        root: { backgroundColor: 'rgba(30,41,59,0.8)', backdropFilter: 'blur(20px)', boxShadow: '0 1px 3px rgba(0,0,0,0.2)' },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: { backgroundColor: '#1E293B', borderRight: '1px solid rgba(255,255,255,0.06)' },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: '#1E293B',
          backgroundImage: 'linear-gradient(rgba(255,255,255,0.02), rgba(255,255,255,0.02))',
        },
      },
    },
  },
});

export const gradients = {
  primary: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
  secondary: 'linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%)',
  success: 'linear-gradient(135deg, #22C55E 0%, #14B8A6 100%)',
  warning: 'linear-gradient(135deg, #F59E0B 0%, #F97316 100%)',
  error: 'linear-gradient(135deg, #EF4444 0%, #EC4899 100%)',
  info: 'linear-gradient(135deg, #3B82F6 0%, #6366F1 100%)',
  dark: 'linear-gradient(135deg, #1E293B 0%, #0F172A 100%)',
  glass: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
};

export { lightTheme, darkTheme };
