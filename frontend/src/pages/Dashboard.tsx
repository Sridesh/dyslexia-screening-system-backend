import React, { useEffect, useState } from "react";
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Skeleton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Avatar,
  Chip,
} from "@mui/material";
import {
  ChildCare as ChildIcon,
  Assignment as TestIcon,
  Warning as WarningIcon,
  ArrowForward as ArrowIcon,
  PlayCircle as PlayIcon,
} from "@mui/icons-material";
import { useNavigate } from "react-router";
import { getChildren, getTests } from "../api";
import type { Child, Test } from "../types";
import RiskChip from "../components/RiskChip";

interface StatCardProps {
  label: string;
  value: number | string;
  icon: React.ReactNode;
  color: string;
  loading?: boolean;
}

const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  icon,
  color,
  loading,
}) => (
  <Card>
    <CardContent>
      <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
        <Avatar sx={{ bgcolor: color, width: 52, height: 52 }}>{icon}</Avatar>
        <Box>
          <Typography variant="h4" fontWeight={700}>
            {loading ? <Skeleton width={48} /> : value}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {label}
          </Typography>
        </Box>
      </Box>
    </CardContent>
  </Card>
);

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [children, setChildren] = useState<Child[]>([]);
  const [tests, setTests] = useState<Test[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [c, t] = await Promise.all([getChildren(), getTests()]);
        setChildren(c);
        setTests(t);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const today = new Date().toDateString();
  const testsToday = tests.filter(
    (t) => t.start_time && new Date(t.start_time).toDateString() === today
  );
  const highRiskCount = tests.filter(
    (t) => t.final_risk_label?.toLowerCase() === "high"
  ).length;
  const recentTests = [...tests]
    .sort(
      (a, b) =>
        new Date(b.start_time ?? 0).getTime() -
        new Date(a.start_time ?? 0).getTime()
    )
    .slice(0, 6);

  const childMap = Object.fromEntries(children.map((c) => [c.id, c]));

  return (
    <Box>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Box>
          <Typography variant="h5">Dashboard</Typography>
          <Typography variant="subtitle1">
            Overview of screening activity
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<PlayIcon />}
          onClick={() => navigate("/children")}
        >
          Start New Test
        </Button>
      </Box>

      {/* Stat cards */}
      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        <Grid size={{ xs: 12, sm: 4 }}>
          <StatCard
            label="Registered Children"
            value={children.length}
            icon={<ChildIcon />}
            color="#00796B"
            loading={loading}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 4 }}>
          <StatCard
            label="Tests Run Today"
            value={testsToday.length}
            icon={<TestIcon />}
            color="#1565C0"
            loading={loading}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 4 }}>
          <StatCard
            label="High Risk Flags"
            value={highRiskCount}
            icon={<WarningIcon />}
            color="#C62828"
            loading={loading}
          />
        </Grid>
      </Grid>

      {/* Recent tests */}
      <Card>
        <CardContent>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 2,
            }}
          >
            <Typography variant="h6">Recent Tests</Typography>
            <Button
              size="small"
              endIcon={<ArrowIcon />}
              onClick={() => navigate("/children")}
            >
              View All Children
            </Button>
          </Box>

          {loading ? (
            [1, 2, 3].map((i) => <Skeleton key={i} height={56} sx={{ mb: 1 }} />)
          ) : recentTests.length === 0 ? (
            <Box sx={{ py: 4, textAlign: "center" }}>
              <Typography variant="body1" color="text.secondary">
                No tests yet. Register a child and start screening.
              </Typography>
            </Box>
          ) : (
            <List disablePadding>
              {recentTests.map((test, idx) => {
                const child = childMap[test.child_id ?? -1];
                return (
                  <React.Fragment key={test.id}>
                    {idx > 0 && <Divider />}
                    <ListItem
                      disablePadding
                      sx={{
                        py: 1.2,
                        px: 0,
                        cursor: "pointer",
                        "&:hover": { bgcolor: "action.hover" },
                        borderRadius: 1,
                      }}
                      onClick={() => navigate(`/tests/${test.id}/results`)}
                    >
                      <ListItemText
                        primary={
                          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                            <Typography variant="body1" fontWeight={600}>
                              {child?.name ?? `Child #${test.child_id}`}
                            </Typography>
                            {test.final_risk_label && (
                              <RiskChip risk={test.final_risk_label} size="small" />
                            )}
                            {test.status === "in_progress" && (
                              <Chip label="In Progress" size="small" color="info" />
                            )}
                          </Box>
                        }
                        secondary={
                          test.start_time
                            ? new Date(test.start_time).toLocaleString()
                            : "Unknown time"
                        }
                      />
                      <ListItemSecondaryAction>
                        <Typography variant="caption" color="text.secondary">
                          {test.total_items ?? "—"} items ·{" "}
                          {test.total_time_s
                            ? `${Math.round(test.total_time_s)}s`
                            : "—"}
                        </Typography>
                      </ListItemSecondaryAction>
                    </ListItem>
                  </React.Fragment>
                );
              })}
            </List>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default Dashboard;
