import React from "react";
import { Box, Typography, Button } from "@mui/material";
import { useNavigate } from "react-router";
import { SentimentDissatisfied as SadIcon } from "@mui/icons-material";

const NotFound: React.FC = () => {
  const navigate = useNavigate();
  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        py: 12,
        gap: 2,
      }}
    >
      <SadIcon sx={{ fontSize: 80, color: "text.disabled" }} />
      <Typography variant="h4" fontWeight={700} color="text.secondary">
        Page Not Found
      </Typography>
      <Typography color="text.secondary">
        The page you're looking for doesn't exist.
      </Typography>
      <Button variant="contained" onClick={() => navigate("/")}>
        Back to Dashboard
      </Button>
    </Box>
  );
};

export default NotFound;
