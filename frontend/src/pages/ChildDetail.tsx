import React, { useEffect, useState } from "react";

import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Avatar,
  Chip,
  Skeleton,
  Alert,
  Divider,
  Grid,
} from "@mui/material";
import {
  ArrowBack as BackIcon,
  PlayCircle as PlayIcon,
  ChildCare as ChildIcon,
  CalendarToday as CalIcon,
  Translate as LangIcon,
  Person as PersonIcon,
} from "@mui/icons-material";
import { useNavigate, useParams } from "react-router";
import { getChild, getTests } from "../api";
import type { Child, Test } from "../types";
import RiskChip from "../components/RiskChip";

const InfoPill: React.FC<{
  icon: React.ReactNode;
  label: string;
  value: string;
}> = ({ icon, label, value }) => (
  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
    <Box sx={{ color: "primary.main" }}>{icon}</Box>
    <Box>
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="body2" fontWeight={600}>
        {value}
      </Typography>
    </Box>
  </Box>
);

const calcAge = (dob?: string | null) => {
  if (!dob) return "—";
  const age = Math.floor(
    (Date.now() - new Date(dob).getTime()) / (365.25 * 24 * 3600 * 1000),
  );
  return `${age} years old`;
};

const ChildDetail: React.FC = () => {
  const { childId } = useParams<{ childId: string }>();
  const navigate = useNavigate();
  const [child, setChild] = useState<Child | null>(null);
  const [tests, setTests] = useState<Test[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!childId) return;
    (async () => {
      try {
        const [c, t] = await Promise.all([
          getChild(Number(childId)),
          getTests(Number(childId)),
        ]);
        setChild(c);
        setTests(t);
      } catch {
        setError("Failed to load child data.");
      } finally {
        setLoading(false);
      }
    })();
  }, [childId]);

  const sortedTests = [...tests].sort(
    (a, b) =>
      new Date(b.start_time ?? 0).getTime() -
      new Date(a.start_time ?? 0).getTime(),
  );

  if (loading) {
    return (
      <Box>
        <Skeleton variant="rounded" height={140} sx={{ mb: 2 }} />
        <Skeleton variant="rounded" height={300} />
      </Box>
    );
  }

  if (error || !child) {
    return <Alert severity="error">{error ?? "Child not found."}</Alert>;
  }

  return (
    <Box>
      <Button
        startIcon={<BackIcon />}
        onClick={() => navigate("/children")}
        sx={{ mb: 2 }}
      >
        Back to Children
      </Button>

      {/* Profile card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid size={{ xs: "auto" }}>
              <Avatar
                sx={{
                  bgcolor: "primary.main",
                  width: 80,
                  height: 80,
                  fontSize: 32,
                }}
              >
                {child.name?.[0]?.toUpperCase() ?? <ChildIcon />}
              </Avatar>
            </Grid>
            <Grid size={{ xs: 12, sm: "grow" }}>
              <Typography variant="h5" fontWeight={700}>
                {child.name ?? `Child #${child.id}`}
              </Typography>
              {child.notes && (
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mt: 0.5 }}
                >
                  {child.notes}
                </Typography>
              )}
              <Box sx={{ display: "flex", gap: 3, mt: 2, flexWrap: "wrap" }}>
                <InfoPill
                  icon={<CalIcon fontSize="small" />}
                  label="Date of Birth"
                  value={
                    child.dob ? new Date(child.dob).toLocaleDateString() : "—"
                  }
                />
                <InfoPill
                  icon={<ChildIcon fontSize="small" />}
                  label="Age"
                  value={calcAge(child.dob)}
                />
                <InfoPill
                  icon={<PersonIcon fontSize="small" />}
                  label="Gender"
                  value={child.gender ?? "—"}
                />
                <InfoPill
                  icon={<LangIcon fontSize="small" />}
                  label="Language"
                  value={child.language ?? "—"}
                />
              </Box>
            </Grid>
            <Grid size={{ xs: 12, sm: "auto" }}>
              <Button
                variant="contained"
                size="large"
                startIcon={<PlayIcon />}
                onClick={() => navigate(`/children/${child.id}/test`)}
              >
                Start New Test
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Test history */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Test History ({tests.length})
          </Typography>
          <Divider sx={{ mb: 2 }} />

          {sortedTests.length === 0 ? (
            <Box sx={{ py: 4, textAlign: "center" }}>
              <Typography color="text.secondary">
                No tests have been run for this child yet.
              </Typography>
              <Button
                variant="contained"
                sx={{ mt: 2 }}
                startIcon={<PlayIcon />}
                onClick={() => navigate(`/children/${child.id}/test`)}
              >
                Start First Test
              </Button>
            </Box>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Risk</TableCell>
                    <TableCell align="center">Items</TableCell>
                    <TableCell align="center">Duration</TableCell>
                    <TableCell align="center">Score</TableCell>
                    <TableCell />
                  </TableRow>
                </TableHead>
                <TableBody>
                  {sortedTests.map((test) => (
                    <TableRow
                      key={test.id}
                      hover
                      sx={{ cursor: "pointer" }}
                      onClick={() => navigate(`/tests/${test.id}/results`)}
                    >
                      <TableCell>
                        {test.start_time
                          ? new Date(test.start_time).toLocaleDateString()
                          : "—"}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={test.status ?? "unknown"}
                          size="small"
                          color={
                            test.status === "completed"
                              ? "success"
                              : test.status === "in_progress"
                                ? "info"
                                : "default"
                          }
                        />
                      </TableCell>
                      <TableCell>
                        {test.final_risk_label ? (
                          <RiskChip risk={test.final_risk_label} size="small" />
                        ) : (
                          "—"
                        )}
                      </TableCell>
                      <TableCell align="center">
                        {test.total_items ?? "—"}
                      </TableCell>
                      <TableCell align="center">
                        {test.total_time_s
                          ? `${Math.round(test.total_time_s)}s`
                          : "—"}
                      </TableCell>
                      <TableCell align="center">
                        {test.final_risk_score !== null &&
                        test.final_risk_score !== undefined
                          ? (test.final_risk_score * 100).toFixed(0) + "%"
                          : "—"}
                      </TableCell>
                      <TableCell>
                        <Button size="small">View</Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default ChildDetail;
