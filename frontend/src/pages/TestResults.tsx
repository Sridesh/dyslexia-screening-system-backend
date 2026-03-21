import React, { useEffect, useState } from "react";
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  Alert,
  CircularProgress,
  Divider,
  LinearProgress,
  Tooltip,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import {
  ArrowBack as BackIcon,
  CheckCircle as CheckIcon,
  Warning as WarnIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Print as PrintIcon,
  Speed as SpeedIcon,
  Psychology as BrainIcon,
  BatteryAlert as FatigueIcon,
} from "@mui/icons-material";
import { useNavigate, useParams } from "react-router";
import { getTest, getModuleSummaries, getXai } from "../api";
import type { Test, ModuleSummary, TestXAI } from "../types";
import RiskChip from "../components/RiskChip";
import ModuleBarChart from "../components/ModuleBarChart";

const MODULE_LABELS: Record<string, string> = {
  phonemic_awareness: "Phonemic Awareness",
  ran: "Rapid Automatized Naming (RAN)",
  object_recognition: "Object Recognition",
};

const SUBTYPE_DESCRIPTIONS: Record<string, string> = {
  Double_deficit: "Deficits in both Phonemic Awareness and Rapid Naming — the most severe dyslexia profile.",
  PA_deficit: "Primarily a Phonemic Awareness deficit — difficulty processing and manipulating sounds.",
  RAN_deficit: "Primarily a Rapid Automatized Naming deficit — difficulty with speed and fluency of symbol recognition.",
  Visual_primary: "Visual processing difficulty is the primary concern.",
  Mixed_or_uncertain: "Mixed or uncertain profile — further assessment recommended.",
  None: "No significant dyslexia indicators detected.",
};

  const RiskBanner: React.FC<{ test: Test; xai?: TestXAI | null }> = ({ test, xai }) => {
  const risk = test.final_risk_label?.toLowerCase();
  const bgMap: Record<string, string> = {
    high: "#FFEBEE",
    moderate: "#FFF8E1",
    low: "#E8F5E9",
  };
  const iconMap: Record<string, React.ReactNode> = {
    high: <ErrorIcon sx={{ fontSize: 48, color: "error.main" }} />,
    moderate: <WarnIcon sx={{ fontSize: 48, color: "warning.main" }} />,
    low: <CheckIcon sx={{ fontSize: 48, color: "success.main" }} />,
  };

  let subtype: string | undefined;
  if (xai?.payload_json) {
    try {
      const parsed = JSON.parse(xai.payload_json);
      subtype = parsed.subtype;
    } catch {}
  }

  return (
    <Paper
      elevation={0}
      sx={{
        bgcolor: bgMap[risk ?? "low"] ?? "#f5f5f5",
        border: "1px solid",
        borderColor: risk === "high" ? "error.light" : risk === "moderate" ? "warning.light" : "success.light",
        borderRadius: 3,
        p: 4,
        mb: 3,
        display: "flex",
        gap: 3,
        alignItems: "center",
        flexWrap: "wrap",
      }}
    >
      {iconMap[risk ?? "low"] ?? <InfoIcon sx={{ fontSize: 48 }} />}
      <Box sx={{ flex: 1 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 1 }}>
          <Typography variant="h4" fontWeight={800}>
            {risk === "high" ? "High Risk" : risk === "moderate" ? "Moderate Risk" : "Low Risk"}
          </Typography>
          {test.final_risk_label && <RiskChip risk={test.final_risk_label} />}
        </Box>
        {subtype && (
          <Chip
            label={subtype.replace(/_/g, " ")}
            variant="outlined"
            size="small"
            sx={{ mb: 1 }}
          />
        )}
        {subtype && SUBTYPE_DESCRIPTIONS[subtype] && (
          <Typography variant="body2" color="text.secondary">
            {SUBTYPE_DESCRIPTIONS[subtype]}
          </Typography>
        )}
      </Box>
      <Box sx={{ textAlign: "center" }}>
        <Typography variant="caption" color="text.secondary" display="block">Risk Score</Typography>
        <Typography variant="h3" fontWeight={800} color={
          risk === "high" ? "error.main" : risk === "moderate" ? "warning.main" : "success.main"
        }>
          {test.final_risk_score !== null && test.final_risk_score !== undefined
            ? (test.final_risk_score * 100).toFixed(0)
            : "—"}
          <Typography component="span" variant="h6">%</Typography>
        </Typography>
        {test.final_risk_entropy !== null && test.final_risk_entropy !== undefined && (
          <Box>
            <Typography variant="caption" color="text.secondary" display="block">
              Confidence: {(() => {
                // Option 1: Map Confidence to the dominant probability
                const prob = test.final_risk_score || 0;
                const dominantProb = Math.max(prob, 1 - prob);
                
                // Optional: Penalize slightly if entropy is very high (noisy data)
                const ent = test.final_risk_entropy || 0;
                const penalty = Math.max(0, ent - 0.4) * 0.2; // Only penalize if entropy > 0.4
                
                return ((dominantProb - penalty) * 100).toFixed(0);
              })()}%
            </Typography>
            <Typography variant="caption" color="text.disabled">
              Uncertainty (Entropy): {test.final_risk_entropy.toFixed(2)}
            </Typography>
          </Box>
        )}
      </Box>
    </Paper>
  );
};

const TestResults: React.FC = () => {
  const { testId } = useParams<{ testId: string }>();
  const navigate = useNavigate();

  const [test, setTest] = useState<Test | null>(null);
  const [moduleSummaries, setModuleSummaries] = useState<ModuleSummary[]>([]);
  const [xaiData, setXaiData] = useState<TestXAI | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!testId) return;
    (async () => {
      try {
        const [t, ms, xai] = await Promise.all([
          getTest(Number(testId)),
          getModuleSummaries(Number(testId)),
          getXai(Number(testId)),
        ]);
        setTest(t);
        setModuleSummaries(ms);
        setXaiData(xai?.[0] ?? null);
      } catch {
        setError("Failed to load test results.");
      } finally {
        setLoading(false);
      }
    })();
  }, [testId]);

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}>
        <CircularProgress size={56} />
      </Box>
    );
  }

  if (error || !test) {
    return (
      <Box sx={{ maxWidth: 500, mx: "auto", mt: 6 }}>
        <Alert severity="error">{error ?? "Test not found."}</Alert>
        <Button sx={{ mt: 2 }} onClick={() => navigate("/")}>
          Go to Dashboard
        </Button>
      </Box>
    );
  }

  // ── Parse XAI explanation JSON ──
  let explanationModules: Record<string, {
    label: string;
    notes: string[];
    p_weak: number;
    p_strong: number;
    entropy: number;
    num_items: number;
    avg_time_s: number;
  }> = {};
  if (xaiData?.payload_json) {
    try {
      const parsed = JSON.parse(xaiData.payload_json);
      explanationModules = parsed?.modules ?? {};
    } catch {
      /* ignore */
    }
  }

  const accuracy =
    moduleSummaries.length > 0
      ? moduleSummaries.reduce((sum, m) => sum + (m.total_correct_count ?? 0), 0) /
        Math.max(moduleSummaries.reduce((sum, m) => sum + (m.num_items ?? 0), 1))
      : null;

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 3 }}>
        <Button
          startIcon={<BackIcon />}
          onClick={() =>
            test.child_id ? navigate(`/children/${test.child_id}`) : navigate("/")
          }
        >
          Back to Child
        </Button>
        <Button startIcon={<PrintIcon />} variant="outlined" onClick={() => window.print()}>
          Print Report
        </Button>
      </Box>

      {/* Risk banner */}
      <RiskBanner test={test} xai={xaiData} />

      {/* Session summary cards */}
      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        {[
          {
            label: "Total Items",
            value: test.total_items ?? "—",
            icon: <BrainIcon />,
            color: "#1565C0",
          },
          {
            label: "Duration",
            value: test.total_time_s ? `${Math.round(test.total_time_s)}s` : "—",
            icon: <SpeedIcon />,
            color: "#00796B",
          },
          {
            label: "Overall Accuracy",
            value: accuracy !== null ? `${(accuracy * 100).toFixed(0)}%` : "—",
            icon: <CheckIcon />,
            color: "#2E7D32",
          },
          {
            label: "Fatigue Penalty",
            value: test.final_fatigue_level ? `+${(test.final_fatigue_level * 100).toFixed(1)}%` : "0%",
            icon: <FatigueIcon />,
            color: test.final_fatigue_level && test.final_fatigue_level > 0.05 ? "#D32F2F" : "#757575",
          },
        ].map((stat) => (
          <Grid key={stat.label} size={{ xs: 12, sm: 3 }}>
            <Card>
              <CardContent sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                <Box
                  sx={{
                    bgcolor: stat.color,
                    borderRadius: 2,
                    p: 1.2,
                    color: "#fff",
                    display: "flex",
                  }}
                >
                  {stat.icon}
                </Box>
                <Box>
                  <Typography variant="h5" fontWeight={700}>{stat.value}</Typography>
                  <Typography variant="caption" color="text.secondary">{stat.label}</Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Module breakdown */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 0.5 }}>Module Breakdown</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Bayesian confidence scores per cognitive domain
          </Typography>

          {moduleSummaries.length === 0 ? (
            <Typography color="text.secondary">
              No module data available for this test.
            </Typography>
          ) : (
            moduleSummaries.map((m) => (
              <Box key={m.id} sx={{ mb: 3 }}>
                <ModuleBarChart
                  moduleId={m.module ?? ""}
                  label={MODULE_LABELS[m.module ?? ""] ?? m.module ?? "Unknown"}
                  pWeak={m.p_weak_final ?? 0}
                  pStrong={m.p_strong_final ?? 0}
                  entropy={m.entropy_final ?? undefined}
                />
                <Grid container spacing={2} sx={{ mt: 0.5, pl: 0 }}>
                  {[
                    { label: "Items", value: m.num_items ?? "—" },
                    { label: "Correct", value: m.total_correct_count ?? "—" },
                    { label: "Avg RT", value: m.avg_time_s ? `${m.avg_time_s.toFixed(1)}s` : "—" },
                    { 
                      label: "Adaptation", 
                      value: m.avg_switch_rt_s ? `${m.avg_switch_rt_s.toFixed(1)}s` : "0s" 
                    },
                    {
                      label: "Compensated",
                      value: m.slow_correct_ratio !== undefined && m.slow_correct_ratio !== null ? `${(m.slow_correct_ratio * 100).toFixed(0)}%` : "—"
                    },
                    { label: "Label", value: m.risk_label ?? "uncertain" },
                  ].map((stat) => (
                    <Grid key={stat.label} size={{ xs: 6, sm: 2 }}>
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          {stat.label}
                        </Typography>
                        <Typography 
                          variant="body2" 
                          fontWeight={600}
                          sx={{ textTransform: stat.label === "Label" ? "capitalize" : "none" }}
                        >
                          {stat.value}
                        </Typography>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
                <Divider sx={{ mt: 2 }} />
              </Box>
            ))
          )}

          {/* Also show from XAI explanation if module summaries are empty */}
          {moduleSummaries.length === 0 && Object.keys(explanationModules).length > 0 &&
            Object.entries(explanationModules).map(([moduleId, data]) => (
              <Box key={moduleId} sx={{ mb: 3 }}>
                <ModuleBarChart
                  moduleId={moduleId}
                  label={MODULE_LABELS[moduleId] ?? moduleId}
                  pWeak={data.p_weak}
                  pStrong={data.p_strong}
                  entropy={data.entropy}
                />
                <Divider sx={{ mt: 2 }} />
              </Box>
            ))
          }
        </CardContent>
      </Card>

      {/* Explanation / XAI section */}
      {Object.keys(explanationModules).length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
              <InfoIcon color="primary" />
              <Typography variant="h6">Clinical Explanation</Typography>
            </Box>
            <Divider sx={{ mb: 2 }} />
            {Object.entries(explanationModules).map(([moduleId, data]) => (
              <Box key={moduleId} sx={{ mb: 3 }}>
                <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 1 }}>
                  {MODULE_LABELS[moduleId] ?? moduleId}
                </Typography>
                <List dense disablePadding>
                  {data.notes?.map((note, idx) => (
                    <ListItem key={idx} disablePadding sx={{ mb: 0.5 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <InfoIcon fontSize="small" color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={note}
                        primaryTypographyProps={{ variant: "body2" }}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Confidence meter */}
      {test.final_risk_entropy !== null && test.final_risk_entropy !== undefined && (
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 1 }}>
              Overall Confidence
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              How certain the system is in this classification
            </Typography>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <Tooltip title={`Entropy Score: ${test.final_risk_entropy.toFixed(3)} (Higher = More Uncertain)`}>
                <Box sx={{ flex: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={(() => {
                      const prob = test.final_risk_score || 0;
                      const dominantProb = Math.max(prob, 1 - prob);
                      const ent = test.final_risk_entropy || 0;
                      const penalty = Math.max(0, ent - 0.4) * 0.2;
                      return (dominantProb - penalty) * 100;
                    })()}
                    sx={{
                      height: 14,
                      borderRadius: 7,
                      "& .MuiLinearProgress-bar": { bgcolor: "primary.main" },
                    }}
                  />
                </Box>
              </Tooltip>
              <Typography variant="body1" fontWeight={700}>
                {(() => {
                  const prob = test.final_risk_score || 0;
                  const dominantProb = Math.max(prob, 1 - prob);
                  const ent = test.final_risk_entropy || 0;
                  const penalty = Math.max(0, ent - 0.4) * 0.2;
                  return ((dominantProb - penalty) * 100).toFixed(0);
                })()}%
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default TestResults;
