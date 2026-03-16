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
  return (
    <Chip
      label={labelMap[normalized] ?? risk}
      color={colorMap[normalized] ?? "default"}
      size={size}
      variant="filled"
    />
  );
};

export default RiskChip;
