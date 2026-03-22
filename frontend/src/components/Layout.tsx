import React, { useState } from "react";
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  AppBar,
  Typography,
  IconButton,
  Tooltip,
  Divider,
  Avatar,
} from "@mui/material";
import {
  Dashboard as DashboardIcon,
  ChildCare as ChildIcon,
  Psychology as BrainIcon,
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  Science as ScienceIcon,
} from "@mui/icons-material";
import { useNavigate, useLocation } from "react-router";

const DRAWER_WIDTH = 240;
const DRAWER_COLLAPSED = 72;

const navItems = [
  { label: "Dashboard", icon: <DashboardIcon />, path: "/" },
  { label: "Children", icon: <ChildIcon />, path: "/children" },
];

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [open, setOpen] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  const drawerWidth = open ? DRAWER_WIDTH : DRAWER_COLLAPSED;

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      {/* ───── Sidebar ───── */}
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          "& .MuiDrawer-paper": {
            width: drawerWidth,
            boxSizing: "border-box",
            transition: "width 0.22s ease",
            overflowX: "hidden",
          },
        }}
      >
        {/* Logo area */}
        <Box
          sx={{
            px: 2,
            py: 2.5,
            display: "flex",
            alignItems: "center",
            gap: 1.5,
            minHeight: 64,
          }}
        >
          <Avatar
            sx={{
              bgcolor: "rgba(255,255,255,0.15)",
              width: 38,
              height: 38,
              flexShrink: 0,
            }}
          >
            <ScienceIcon sx={{ color: "#fff", fontSize: 22 }} />
          </Avatar>
          {open && (
            <Box>
              <Typography
                variant="subtitle1"
                fontWeight={700}
                sx={{ color: "#fff", lineHeight: 1.2 }}
              >
                DyslexiaScreen
              </Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                EF-ADS System
              </Typography>
            </Box>
          )}
        </Box>

        <Divider sx={{ borderColor: "rgba(255,255,255,0.12)" }} />

        {/* Nav items */}
        <List sx={{ pt: 1 }}>
          {navItems.map((item) => {
            const active = location.pathname === item.path || 
              (item.path !== "/" && location.pathname.startsWith(item.path));
            return (
              <ListItem key={item.path} disablePadding>
                <Tooltip title={!open ? item.label : ""} placement="right">
                  <ListItemButton
                    onClick={() => navigate(item.path)}
                    sx={{
                      mx: 1,
                      my: 0.25,
                      borderRadius: 2,
                      backgroundColor: active
                        ? "rgba(255,255,255,0.15)"
                        : "transparent",
                      "&:hover": {
                        backgroundColor: "rgba(255,255,255,0.10)",
                      },
                      minHeight: 46,
                    }}
                  >
                    <ListItemIcon
                      sx={{
                        color: active ? "#fff" : "rgba(255,255,255,0.65)",
                        minWidth: open ? 40 : "auto",
                      }}
                    >
                      {item.icon}
                    </ListItemIcon>
                    {open && (
                      <ListItemText
                        primary={item.label}
                        primaryTypographyProps={{
                          fontSize: 14,
                          fontWeight: active ? 700 : 400,
                          color: "#fff",
                        }}
                      />
                    )}
                  </ListItemButton>
                </Tooltip>
              </ListItem>
            );
          })}
        </List>

        {/* Collapse toggle at bottom */}
        <Box sx={{ mt: "auto", pb: 2, display: "flex", justifyContent: open ? "flex-end" : "center", px: 1.5 }}>
          <Tooltip title={open ? "Collapse" : "Expand"} placement="right">
            <IconButton
              onClick={() => setOpen(!open)}
              sx={{ color: "rgba(255,255,255,0.65)" }}
            >
              {open ? <ChevronLeftIcon /> : <MenuIcon />}
            </IconButton>
          </Tooltip>
        </Box>
      </Drawer>

      {/* ───── Main area ───── */}
      <Box sx={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
        <AppBar
          position="sticky"
          elevation={0}
          sx={{
            bgcolor: "background.paper",
            borderBottom: "1px solid",
            borderColor: "divider",
          }}
        >
          <Toolbar sx={{ gap: 1 }}>
            <BrainIcon sx={{ color: "primary.main", mr: 1 }} />
            <Typography
              variant="h6"
              sx={{ color: "text.primary", fontWeight: 700 }}
            >
              Dyslexia Screening System
            </Typography>
          </Toolbar>
        </AppBar>

        <Box
          component="main"
          sx={{ flex: 1, p: { xs: 2, sm: 3 }, bgcolor: "background.default" }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
};

export default Layout;
