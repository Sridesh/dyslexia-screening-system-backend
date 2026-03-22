import React from "react";
import { Box, Typography, LinearProgress, Tooltip } from "@mui/material";

interface ModuleBarChartProps {
  moduleId: string;
  label: string;
  pWeak: number;
  pStrong: number;
  entropy?: number;
}

const moduleColors: Record<string, { weak: string; strong: string }> = {
  phonemic_awareness: { weak: "#D32F2F", strong: "#2E7D32" },
  ran: { weak: "#E64A19", strong: "#00796B" },
  object_recognition: { weak: "#6A1B9A", strong: "#1565C0" },
};

const ModuleBarChart: React.FC<ModuleBarChartProps> = ({
  moduleId,
  label,
  pWeak,
  pStrong,
  entropy,
}) => {
  const colors = moduleColors[moduleId] ?? {
    weak: "#D32F2F",
    strong: "#2E7D32",
  };

  return (
    <Box sx={{ mb: 2 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 0.5 }}>
        <Typography variant="body2" fontWeight={600}>
          {label}
        </Typography>
        {entropy !== undefined && (
          <Typography variant="caption" color="text.secondary">
            Entropy: {entropy.toFixed(2)}
          </Typography>
        )}
      </Box>

      {/* P(Weak) bar */}
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 0.4 }}>
        <Typography variant="caption" sx={{ width: 64, color: colors.weak }}>
          P(Weak)
        </Typography>
        <Tooltip title={`${(pWeak * 100).toFixed(1)}%`}>
          <Box sx={{ flex: 1 }}>
            <LinearProgress
              variant="determinate"
              value={pWeak * 100}
              sx={{
                height: 10,
                borderRadius: 5,
                backgroundColor: "#f5f5f5",
                "& .MuiLinearProgress-bar": { backgroundColor: colors.weak },
              }}
            />
          </Box>
        </Tooltip>
        <Typography variant="caption" sx={{ width: 40, textAlign: "right" }}>
          {(pWeak * 100).toFixed(0)}%
        </Typography>
      </Box>

      {/* P(Strong) bar */}
      <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
        <Typography variant="caption" sx={{ width: 64, color: colors.strong }}>
          P(Strong)
        </Typography>
        <Tooltip title={`${(pStrong * 100).toFixed(1)}%`}>
          <Box sx={{ flex: 1 }}>
            <LinearProgress
              variant="determinate"
              value={pStrong * 100}
              sx={{
                height: 10,
                borderRadius: 5,
                backgroundColor: "#f5f5f5",
                "& .MuiLinearProgress-bar": {
                  backgroundColor: colors.strong,
                },
              }}
            />
          </Box>
        </Tooltip>
        <Typography variant="caption" sx={{ width: 40, textAlign: "right" }}>
          {(pStrong * 100).toFixed(0)}%
        </Typography>
      </Box>
    </Box>
  );
};

export default ModuleBarChart;
