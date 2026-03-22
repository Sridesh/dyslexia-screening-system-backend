import React from "react";
import { Chip } from "@mui/material";

type RiskLevel = "high" | "moderate" | "low" | string;

interface RiskChipProps {
  risk: RiskLevel;
  size?: "small" | "medium";
}

const labelMap: Record<string, string> = {
  high: "High Risk",
  moderate: "Moderate Risk",
  low: "Low Risk",
};

const colorMap: Record<string, "error" | "warning" | "success" | "default"> = {
  high: "error",
  moderate: "warning",
  low: "success",
};

const RiskChip: React.FC<RiskChipProps> = ({ risk, size = "medium" }) => {
  const normalized = risk?.toLowerCase();
  const color = colorMap[normalized] ?? "default";
  
  return (
    <Chip
      label={labelMap[normalized] ?? risk}
      color={color}
      size={size}
      variant="outlined"
      sx={{ 
        fontWeight: 700, 
        borderRadius: 2,
        borderWidth: 2,
        px: 1,
        bgcolor: normalized === 'high' ? 'rgba(211, 47, 47, 0.05)' : 
                 normalized === 'moderate' ? 'rgba(237, 108, 2, 0.05)' : 
                 normalized === 'low' ? 'rgba(46, 125, 50, 0.05)' : 'transparent'
      }}
    />
  );
};

export default RiskChip;
