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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
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
  AutoGraph as PlanIcon,
  Download as DownloadIcon,
} from "@mui/icons-material";
import { useNavigate, useParams } from "react-router";
import { getTest, getModuleSummaries, getXai, getTestItemLogs, getInterventionPlan } from "../api";
import type { Test, ModuleSummary, TestXAI, TestItemLog, InterventionPlan } from "../types";
import ReactMarkdown from "react-markdown";
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

const RiskBanner: React.FC<{ test: Test; xai?: TestXAI | null; globalNotes?: string }> = ({ test, xai, globalNotes }) => {
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
          <Typography variant="body2" color="text.secondary" sx={{ mb: globalNotes ? 1.5 : 0 }}>
            {SUBTYPE_DESCRIPTIONS[subtype]}
          </Typography>
        )}
        {globalNotes && (
          <Box sx={{ 
            mt: 1, 
            p: 1.5, 
            bgcolor: "rgba(255,255,255,0.6)", 
            borderRadius: 2, 
            border: "1px dashed",
            borderColor: "rgba(0,0,0,0.1)"
          }}>
            <Typography variant="body2" sx={{ fontStyle: "italic", fontWeight: 500 }}>
              💡 Clinical Summary: {globalNotes}
            </Typography>
          </Box>
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

const InterventionDialog: React.FC<{
  open: boolean;
  onClose: () => void;
  plan: InterventionPlan | null;
  loading: boolean;
}> = ({ open, onClose, plan, loading }) => {
  const handlePrint = () => {
    const printContent = document.getElementById("intervention-report-content");
    const originalContent = document.body.innerHTML;
    if (printContent) {
      document.body.innerHTML = `
        <html>
          <head>
            <title>Intervention Report</title>
            <style>
              body { font-family: sans-serif; padding: 40px; }
              h1, h2, h3 { color: #1976d2; }
              p { line-height: 1.6; }
              @media print { .no-print { display: none; } }
            </style>
          </head>
          <body>${printContent.innerHTML}</body>
        </html>
      `;
      window.print();
      document.body.innerHTML = originalContent;
      window.location.reload(); // Reload to restore React state
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <PlanIcon color="primary" />
          Personalized Intervention Plan
        </Box>
        <Typography variant="caption" color="text.secondary">
          Generated via {plan?.intervention_plan.source ?? "RAG Agent"}
        </Typography>
      </DialogTitle>
      <DialogContent dividers>
        {loading ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 8, gap: 2 }}>
            <CircularProgress />
            <Typography color="text.secondary">Clinical Agent is analyzing guidelines...</Typography>
          </Box>
        ) : plan ? (
          <Box id="intervention-report-content" sx={{ p: 2 }}>
             <ReactMarkdown 
                components={{
                  h3: ({node, ...props}: any) => <Typography variant="h5" fontWeight={700} color="primary" sx={{ mt: 3, mb: 1 }} {...props} />,
                  p: ({node, ...props}: any) => <Typography variant="body1" sx={{ mb: 2, lineHeight: 1.7 }} {...props} />,
                  li: ({node, ...props}: any) => <Typography component="li" variant="body1" sx={{ mb: 1, ml: 2 }} {...props} />,
                }}
             >
                {plan.intervention_plan.plan_markdown}
             </ReactMarkdown>
          </Box>
        ) : (
          <Alert severity="error">Failed to generate plan. Please try again.</Alert>
        )}
      </DialogContent>
      <DialogActions sx={{ p: 2, gap: 1 }}>
        <Button onClick={onClose} color="inherit">Close</Button>
        <Button 
          startIcon={<DownloadIcon />} 
          variant="contained" 
          onClick={handlePrint}
          disabled={loading || !plan}
        >
          Save as PDF
        </Button>
      </DialogActions>
    </Dialog>
  );
};

const TestResults: React.FC = () => {
  const { testId } = useParams<{ testId: string }>();
  const navigate = useNavigate();

  const [test, setTest] = useState<Test | null>(null);
  const [moduleSummaries, setModuleSummaries] = useState<ModuleSummary[]>([]);
  const [xaiData, setXaiData] = useState<TestXAI | null>(null);
  const [itemLogs, setItemLogs] = useState<TestItemLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Intervention state
  const [showIntervention, setShowIntervention] = useState(false);
  const [interventionPlan, setInterventionPlan] = useState<InterventionPlan | null>(null);
  const [interventionLoading, setInterventionLoading] = useState(false);

  const handleGeneratePlan = async () => {
    if (!testId) return;
    setShowIntervention(true);
    setInterventionLoading(true);
    try {
      const plan = await getInterventionPlan(Number(testId));
      setInterventionPlan(plan);
    } catch {
      console.error("Failed to fetch intervention plan");
    } finally {
      setInterventionLoading(false);
    }
  };

  useEffect(() => {
    if (!testId) return;
    (async () => {
      try {
        const [t, ms, xai, logs] = await Promise.all([
          getTest(Number(testId)),
          getModuleSummaries(Number(testId)),
          getXai(Number(testId)),
          getTestItemLogs(Number(testId)),
        ]);
        setTest(t);
        setModuleSummaries(ms);
        setXaiData(xai?.[0] ?? null);
        setItemLogs(logs.sort((a, b) => (a.global_index ?? 0) - (b.global_index ?? 0)));
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
  let explanationModules: Record<string, any> = {};
  let globalNotes: string | undefined;
  let featureContributions: Record<string, any> | undefined;

  if (xaiData?.payload_json) {
    try {
      const parsed = JSON.parse(xaiData.payload_json);
      explanationModules = parsed?.modules ?? {};
      globalNotes = parsed?.global_notes;
      featureContributions = parsed?.feature_contributions;
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
      <RiskBanner test={test} xai={xaiData} globalNotes={globalNotes} />

      {/* Intervention Action */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'center' }}>
        <Button 
          variant="contained" 
          size="large" 
          startIcon={<PlanIcon />} 
          onClick={handleGeneratePlan}
          sx={{ 
            borderRadius: 3, 
            px: 4, 
            py: 1.5, 
            boxShadow: 3,
            background: "linear-gradient(45deg, #1976d2 30%, #42a5f5 90%)"
          }}
        >
          Generate Personalized Intervention Plan
        </Button>
      </Box>

      {/* Intervention Dialog */}
      <InterventionDialog 
        open={showIntervention} 
        onClose={() => setShowIntervention(false)} 
        plan={interventionPlan}
        loading={interventionLoading}
      />

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
                    {
                      label: "Frustration (Guessed)",
                      value: m.rapid_guess_ratio !== undefined && m.rapid_guess_ratio !== null ? `${(m.rapid_guess_ratio * 100).toFixed(0)}%` : "—"
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
            <Grid container spacing={4}>
              <Grid size={{ xs: 12, md: 7 }}>
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
                      {data.notes?.map((note: string, idx: number) => (
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
              </Grid>

              {/* Feature Drivers section */}
              {featureContributions && (
                <Grid size={{ xs: 12, md: 5 }}>
                  <Box sx={{ p: 2, bgcolor: "grey.50", borderRadius: 3, height: "100%" }}>
                    <Typography variant="subtitle2" fontWeight={800} color="text.secondary" gutterBottom sx={{ textTransform: "uppercase", letterSpacing: 1 }}>
                      Key Feature Drivers
                    </Typography>
                    <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
                      Relative impact on the final risk classification
                    </Typography>
                    
                    <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
                      {Object.entries(featureContributions).map(([key, data]: any) => {
                        const weightColor = data.weight === "Significant" ? "error" : data.weight === "Moderate-to-High" ? "warning" : "info";
                        return (
                          <Paper key={key} variant="outlined" sx={{ p: 1.5, borderRadius: 2 }}>
                            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 0.5 }}>
                              <Typography variant="body2" fontWeight={700}>
                                {key.replace(/_/g, " ").toUpperCase()}
                              </Typography>
                              <Chip 
                                label={data.weight} 
                                size="small" 
                                color={weightColor} 
                                variant="outlined"
                                sx={{ 
                                  fontSize: "0.65rem", 
                                  height: 20, 
                                  fontWeight: 700,
                                  bgcolor: weightColor === 'error' ? 'rgba(211, 47, 47, 0.1)' : 
                                           weightColor === 'warning' ? 'rgba(237, 108, 2, 0.1)' : 
                                           'rgba(2, 136, 209, 0.1)'
                                }} 
                              />
                            </Box>
                            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                               <Typography variant="caption" color="text.secondary">
                                 {data.ability !== undefined ? `Est. Ability: ${data.ability.toFixed(2)}` : `Avg Speed: ${data.avg_rt?.toFixed(1)}s`}
                               </Typography>
                               {/* Micro Sparkline or dot indicating direction */}
                               <Box sx={{ 
                                 width: 8, 
                                 height: 8, 
                                 borderRadius: "50%", 
                                 bgcolor: (data.ability < -0.5 || data.avg_rt > 5.0) ? "error.main" : "success.main" 
                               }} />
                            </Box>
                          </Paper>
                        );
                      })}
                    </Box>
                    <Alert severity="info" sx={{ mt: 3, "& .MuiAlert-message": { fontSize: "0.75rem" } }}>
                      Weights are determined by the Random Forest classifier's interaction logic.
                    </Alert>
                  </Box>
                </Grid>
              )}
            </Grid>
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

      {/* Assessment Trajectory Chart */}
      {itemLogs.length > 0 && (
        <Card sx={{ mt: 3, mb: 3 }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 1 }}>
              Assessment Trajectory
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Item-by-item Bayesian probability of the child being "At-Risk" in the active cognitive module.
            </Typography>
            
            <Box sx={{ width: "100%", height: 300, position: "relative", mt: 2, overflowX: "auto" }}>
              <svg width={Math.max(itemLogs.length * 40 + 60, 600)} height="300" viewBox={`0 0 ${Math.max(itemLogs.length * 40 + 60, 600)} 300`}>
                {/* Background Grid */}
                {[0, 25, 50, 75, 100].map((yVal) => (
                  <g key={`grid-${yVal}`}>
                    <line x1="40" y1={280 - (yVal * 2.5)} x2="100%" y2={280 - (yVal * 2.5)} stroke="#e0e0e0" strokeDasharray="4 4" />
                    <text x="5" y={285 - (yVal * 2.5)} fill="#9e9e9e" fontSize="12">{yVal}%</text>
                  </g>
                ))}
                
                {/* Axes */}
                <line x1="40" y1="280" x2="100%" y2="280" stroke="#9e9e9e" />
                <line x1="40" y1="30" x2="40" y2="280" stroke="#9e9e9e" />
                
                {/* Data Line and Points */}
                {itemLogs.map((log, idx) => {
                  const x2 = 40 + idx * 40;
                  const y2 = 280 - ((log.p_module_weak_after || 0) * 250);
                  
                  // Color code by module
                  const colors: Record<string, string> = {
                    "phonemic_awareness": "#1976D2",
                    "ran": "#D32F2F",
                    "object_recognition": "#388E3C"
                  };
                  const strokeColor = colors[log.module] || "#757575";

                  return (
                    <g key={`line-group-${log.id}`}>
                      {/* Only link points if they are from the same module (otherwise it visually jumps) */}
                      {idx > 0 && itemLogs[idx-1].module === log.module && (
                        <line x1={40 + (idx - 1)*40} y1={280 - ((itemLogs[idx-1].p_module_weak_after || 0)*250)} x2={x2} y2={y2} stroke={strokeColor} strokeWidth="3" opacity="0.6" />
                      )}
                      {/* Dots */}
                      <circle 
                        cx={x2} 
                        cy={y2} 
                        r={log.is_correct ? 5 : 7} 
                        fill={log.is_correct ? "white" : strokeColor} 
                        stroke={strokeColor} 
                        strokeWidth="3" 
                      />
                      {/* X-axis labels (Item Number) */}
                      <text x={x2 - 5} y="295" fill="#757575" fontSize="11">{idx + 1}</text>
                    </g>
                  );
                })}
              </svg>
            </Box>
            <Box sx={{ display: 'flex', gap: 3, mt: 2, justifyContent: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ width: 12, height: 12, borderRadius: '50%', border: '2px solid #757575', bgcolor: 'white' }} />
                <Typography variant="caption" color="text.secondary">Correct Answer</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: '#757575' }} />
                <Typography variant="caption" color="text.secondary">Incorrect Answer</Typography>
              </Box>
              {Object.entries(MODULE_LABELS).map(([mod, label]) => {
                 const colors: Record<string, string> = {
                  "phonemic_awareness": "#1976D2",
                  "ran": "#D32F2F",
                  "object_recognition": "#388E3C"
                };
                return (
                  <Box key={mod} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ width: 16, height: 4, bgcolor: colors[mod] }} />
                    <Typography variant="caption" color="text.secondary">{label}</Typography>
                  </Box>
                )
              })}
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default TestResults;
