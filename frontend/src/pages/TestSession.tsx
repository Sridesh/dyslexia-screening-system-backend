import React, { useEffect, useState, useRef, useCallback } from "react";
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Alert,
  CircularProgress,
  Grid,
  Divider,
} from "@mui/material";
import {
  Timer as TimerIcon,
  CheckCircle as CheckIcon,
} from "@mui/icons-material";
import { useNavigate, useParams } from "react-router";
import { startAdaptiveTest, submitResponse } from "../api";
import type { AdaptiveItem, ItemOption } from "../types";

type Phase = "loading" | "answering" | "completed" | "error";

const MODULE_LABELS: Record<string, string> = {
  phonemic_awareness: "Phonemic Awareness",
  ran: "Rapid Automatized Naming",
  object_recognition: "Object Recognition",
};

const MODULE_COLORS: Record<string, string> = {
  phonemic_awareness: "#1565C0",
  ran: "#BF360C",
  object_recognition: "#4527A0",
};

const TestSession: React.FC = () => {
  const { childId } = useParams<{ childId: string }>();
  const navigate = useNavigate();

  const [phase, setPhase] = useState<Phase>("loading");
  const [testId, setTestId] = useState<number | null>(null);
  const [currentItem, setCurrentItem] = useState<AdaptiveItem | null>(null);
  const [itemCount, setItemCount] = useState(0);
  const [timeLeft, setTimeLeft] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Track response time
  const itemStartTime = useRef<number>(Date.now());
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const clearTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  const startItemTimer = useCallback((maxSeconds: number) => {
    clearTimer();
    setTimeLeft(maxSeconds);
    itemStartTime.current = Date.now();
    timerRef.current = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearTimer();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  }, []);

  // Start the test on mount
  useEffect(() => {
    if (!childId) return;
    (async () => {
      try {
        const result = await startAdaptiveTest(Number(childId));
        setTestId(result.test_id);
        if (result.first_item) {
          setCurrentItem(result.first_item);
          setItemCount(1);
          setPhase("answering");
          startItemTimer(result.first_item.max_time_seconds ?? 30);
        } else {
          setPhase("completed");
        }
      } catch {
        setErrorMsg("Failed to start test. Check the backend is running.");
        setPhase("error");
      }
    })();

    return () => clearTimer();
  }, [childId, startItemTimer]);

  const handleAnswer = async (optionId: string) => {
    if (submitting || !currentItem || !testId) return;
    setSelectedAnswer(optionId);
    clearTimer();

    const rt = (Date.now() - itemStartTime.current) / 1000;
    const isCorrect = optionId === currentItem.correct_option;

    setSubmitting(true);
    try {
      const result = await submitResponse(testId, {
        item_id: currentItem.id,
        is_correct: isCorrect,
        response_time_s: rt,
        test_id: testId,
      });

      // Small delay so selection feedback is visible
      await new Promise((r) => setTimeout(r, 500));

      if (result.status === "completed" || result.status === "completed_fallback") {
        setPhase("completed");
        setTimeout(() => navigate(`/tests/${testId}/results`), 1200);
      } else if (result.next_item) {
        setCurrentItem(result.next_item);
        setItemCount((c) => c + 1);
        setSelectedAnswer(null);
        startItemTimer(result.next_item.max_time_seconds ?? 30);
      } else {
        setPhase("completed");
        setTimeout(() => navigate(`/tests/${testId}/results`), 1200);
      }
    } catch {
      setErrorMsg("Failed to submit response. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  // Auto-submit on timeout (treat as incorrect, max RT)
  useEffect(() => {
    if (timeLeft === 0 && phase === "answering" && currentItem && !submitting && !selectedAnswer) {
      handleAnswer("__timeout__");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [timeLeft]);

  // ─── Parse options ───────────────────────────────────────────────────────────
  let options: ItemOption[] = [];
  if (currentItem?.options_json) {
    try {
      const parsed = JSON.parse(currentItem.options_json);
      options = Array.isArray(parsed) ? parsed : [];
    } catch {
      options = [];
    }
  }

  const moduleLabel = currentItem
    ? MODULE_LABELS[currentItem.module_id] ?? currentItem.module_id
    : "";
  const moduleColor = currentItem
    ? MODULE_COLORS[currentItem.module_id] ?? "#00796B"
    : "#00796B";

  const timerPct = currentItem
    ? (timeLeft / (currentItem.max_time_seconds ?? 30)) * 100
    : 100;

  // ─── Render ──────────────────────────────────────────────────────────────────

  if (phase === "loading") {
    return (
      <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", py: 10, gap: 3 }}>
        <CircularProgress size={56} />
        <Typography variant="h6" color="text.secondary">
          Preparing adaptive test…
        </Typography>
      </Box>
    );
  }

  if (phase === "error") {
    return (
      <Box sx={{ maxWidth: 500, mx: "auto", mt: 6 }}>
        <Alert severity="error" sx={{ mb: 2 }}>{errorMsg}</Alert>
        <Button variant="outlined" onClick={() => navigate(`/children/${childId}`)}>
          Go Back
        </Button>
      </Box>
    );
  }

  if (phase === "completed") {
    return (
      <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", py: 10, gap: 3 }}>
        <CheckIcon sx={{ fontSize: 72, color: "success.main" }} />
        <Typography variant="h5" fontWeight={700}>
          Test Complete!
        </Typography>
        <Typography color="text.secondary">
          Loading results…
        </Typography>
        <CircularProgress size={32} />
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 680, mx: "auto" }}>
      {/* Header row */}
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
        <Chip
          label={moduleLabel}
          sx={{ bgcolor: moduleColor, color: "#fff", fontWeight: 700 }}
        />
        <Typography variant="body2" color="text.secondary">
          Item #{itemCount}
        </Typography>
      </Box>

      {/* Timer bar */}
      <Box sx={{ mb: 2 }}>
        <Box sx={{ display: "flex", justifyContent: "space-between", mb: 0.5 }}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
            <TimerIcon fontSize="small" color={timeLeft <= 5 ? "error" : "action"} />
            <Typography
              variant="body2"
              color={timeLeft <= 5 ? "error.main" : "text.secondary"}
              fontWeight={timeLeft <= 5 ? 700 : 400}
            >
              {timeLeft}s remaining
            </Typography>
          </Box>
          <Typography variant="caption" color="text.secondary">
            Difficulty: {currentItem?.difficulty?.toFixed(1) ?? "—"}
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={timerPct}
          sx={{
            height: 8,
            borderRadius: 4,
            "& .MuiLinearProgress-bar": {
              bgcolor: timeLeft <= 5 ? "error.main" : "primary.main",
              transition: "none",
            },
          }}
        />
      </Box>

      {/* Question card */}
      <Card sx={{ mb: 3, border: "1px solid", borderColor: "divider" }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h6" fontWeight={600} sx={{ mb: 1 }}>
            Question
          </Typography>
          <Divider sx={{ mb: 3 }} />
          <Typography
            variant="body1"
            sx={{ fontSize: 18, lineHeight: 1.7, color: "text.primary" }}
          >
            {currentItem?.prompt_text ?? "No prompt text available."}
          </Typography>
        </CardContent>
      </Card>

      {/* Answer options */}
      {errorMsg && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setErrorMsg(null)}>
          {errorMsg}
        </Alert>
      )}

      <Grid container spacing={2}>
        {options.length > 0
          ? options.map((opt) => {
              const isSelected = selectedAnswer === opt.id;
              return (
                <Grid key={opt.id} size={{ xs: 12, sm: 6 }}>
                  <Button
                    fullWidth
                    variant={isSelected ? "contained" : "outlined"}
                    onClick={() => handleAnswer(opt.id)}
                    disabled={submitting || selectedAnswer !== null}
                    sx={{
                      py: 2,
                      fontSize: 16,
                      borderRadius: 3,
                      justifyContent: "flex-start",
                      px: 3,
                      textAlign: "left",
                      borderColor: isSelected ? "primary.main" : "divider",
                      "&:hover": { borderColor: "primary.main" },
                    }}
                  >
                    {opt.text}
                  </Button>
                </Grid>
              );
            })
          : /* Fallback: correct / incorrect binary */
            ["Correct", "Incorrect"].map((label, idx) => (
              <Grid key={label} size={{ xs: 12, sm: 6 }}>
                <Button
                  fullWidth
                  variant="outlined"
                  color={idx === 0 ? "success" : "error"}
                  onClick={() => handleAnswer(idx === 0 ? "correct" : "incorrect")}
                  disabled={submitting || selectedAnswer !== null}
                  sx={{ py: 2, fontSize: 16, borderRadius: 3 }}
                >
                  {label}
                </Button>
              </Grid>
            ))}
      </Grid>

      {submitting && (
        <Box sx={{ display: "flex", justifyContent: "center", mt: 3 }}>
          <CircularProgress size={28} />
        </Box>
      )}
    </Box>
  );
};

export default TestSession;
