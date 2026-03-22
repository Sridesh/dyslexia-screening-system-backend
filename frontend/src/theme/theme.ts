import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#00796B", // Deep teal — clinical, calm
      light: "#48A999",
      dark: "#004C40",
      contrastText: "#ffffff",
    },
    secondary: {
      main: "#FF8F00", // Amber accent for highlights
      light: "#FFC046",
      dark: "#C56000",
      contrastText: "#000000",
    },
    error: {
      main: "#D32F2F",
    },
    warning: {
      main: "#F9A825",
    },
    success: {
      main: "#2E7D32",
    },
    background: {
      default: "#F4F6F8",
      paper: "#ffffff",
    },
    text: {
      primary: "#1A2027",
      secondary: "#546E7A",
    },
  },
  typography: {
    fontFamily: '"Roboto", "Inter", "Helvetica Neue", Arial, sans-serif',
    h4: { fontWeight: 700 },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
    subtitle1: { fontWeight: 500, color: "#546E7A" },
    button: { textTransform: "none", fontWeight: 600 },
  },
  shape: {
    borderRadius: 10,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: "8px 22px",
        },
        containedPrimary: {
          boxShadow: "0 2px 8px rgba(0, 121, 107, 0.35)",
          "&:hover": {
            boxShadow: "0 4px 14px rgba(0, 121, 107, 0.45)",
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: "0 1px 6px rgba(0,0,0,0.08)",
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { fontWeight: 600 },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: "#004C40",
          color: "#ffffff",
        },
      },
    },
  },
});

export default theme;
