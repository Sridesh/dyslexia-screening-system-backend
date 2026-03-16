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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  IconButton,
  InputAdornment,
  Alert,
  Skeleton,
  Tooltip,
  Avatar,
} from "@mui/material";
import {
  Add as AddIcon,
  Search as SearchIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  ChildCare as ChildIcon,
} from "@mui/icons-material";
import { useNavigate } from "react-router";
import { getChildren, createChild, deleteChild } from "../api";
import type { Child, ChildCreate } from "../types";

const GENDERS = ["Male", "Female", "Other", "Prefer not to say"];
const LANGUAGES = ["English", "Sinhala", "Tamil", "Other"];

const emptyForm: ChildCreate = {
  name: "",
  dob: "",
  gender: "",
  language: "",
  notes: "",
  external_id: "",
};

const ChildrenList: React.FC = () => {
  const navigate = useNavigate();
  const [children, setChildren] = useState<Child[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [form, setForm] = useState<ChildCreate>(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);

  const fetchChildren = async () => {
    try {
      const data = await getChildren();
      setChildren(data);
    } catch {
      setError("Failed to load children.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChildren();
  }, []);

  const filtered = children.filter((c) =>
    [c.name, c.external_id, c.language].some((v) =>
      v?.toLowerCase().includes(search.toLowerCase())
    )
  );

  const handleAdd = async () => {
    setSaving(true);
    setError(null);
    try {
      await createChild({ ...form });
      setDialogOpen(false);
      setForm(emptyForm);
      await fetchChildren();
    } catch {
      setError("Failed to create child profile.");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteChild(id);
      setDeleteConfirm(null);
      await fetchChildren();
    } catch {
      setError("Failed to delete child profile.");
    }
  };

  const calcAge = (dob?: string | null) => {
    if (!dob) return "—";
    const age = Math.floor(
      (Date.now() - new Date(dob).getTime()) / (365.25 * 24 * 3600 * 1000)
    );
    return `${age} yrs`;
  };

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 3 }}>
        <Box>
          <Typography variant="h5">Children</Typography>
          <Typography variant="subtitle1">Manage patient profiles</Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setDialogOpen(true)}
        >
          Add Child
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Search */}
      <TextField
        placeholder="Search by name, ID, or language…"
        size="small"
        fullWidth
        sx={{ mb: 2.5, maxWidth: 420 }}
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        slotProps={{
          input: {
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
          },
        }}
      />

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Child</TableCell>
                <TableCell>Age</TableCell>
                <TableCell>Gender</TableCell>
                <TableCell>Language</TableCell>
                <TableCell>External ID</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading
                ? [1, 2, 3].map((i) => (
                    <TableRow key={i}>
                      {[1, 2, 3, 4, 5, 6].map((j) => (
                        <TableCell key={j}>
                          <Skeleton />
                        </TableCell>
                      ))}
                    </TableRow>
                  ))
                : filtered.length === 0
                ? (
                    <TableRow>
                      <TableCell colSpan={6} align="center" sx={{ py: 5 }}>
                        <Avatar sx={{ bgcolor: "primary.light", mx: "auto", mb: 1 }}>
                          <ChildIcon />
                        </Avatar>
                        <Typography color="text.secondary">
                          {search ? "No matching children found." : "No children registered yet."}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  )
                : filtered.map((child) => (
                    <TableRow
                      key={child.id}
                      hover
                      sx={{ cursor: "pointer" }}
                      onClick={() => navigate(`/children/${child.id}`)}
                    >
                      <TableCell>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
                          <Avatar sx={{ bgcolor: "primary.main", width: 34, height: 34, fontSize: 14 }}>
                            {child.name?.[0]?.toUpperCase() ?? "#"}
                          </Avatar>
                          <Typography fontWeight={600}>
                            {child.name ?? `Child #${child.id}`}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>{calcAge(child.dob)}</TableCell>
                      <TableCell>{child.gender ?? "—"}</TableCell>
                      <TableCell>{child.language ?? "—"}</TableCell>
                      <TableCell>
                        <Typography variant="caption" color="text.secondary">
                          {child.external_id ?? "—"}
                        </Typography>
                      </TableCell>
                      <TableCell align="right" onClick={(e) => e.stopPropagation()}>
                        <Tooltip title="View Profile">
                          <IconButton
                            size="small"
                            onClick={() => navigate(`/children/${child.id}`)}
                          >
                            <ViewIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => setDeleteConfirm(child.id)}
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      {/* Add Child Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Register New Child</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: "16px !important" }}>
          <TextField
            label="Full Name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            fullWidth
            required
          />
          <TextField
            label="Date of Birth"
            type="date"
            value={form.dob}
            onChange={(e) => setForm({ ...form, dob: e.target.value })}
            fullWidth
            slotProps={{ inputLabel: { shrink: true } }}
          />
          <TextField
            select
            label="Gender"
            value={form.gender}
            onChange={(e) => setForm({ ...form, gender: e.target.value })}
            fullWidth
          >
            {GENDERS.map((g) => (
              <MenuItem key={g} value={g}>{g}</MenuItem>
            ))}
          </TextField>
          <TextField
            select
            label="Primary Language"
            value={form.language}
            onChange={(e) => setForm({ ...form, language: e.target.value })}
            fullWidth
          >
            {LANGUAGES.map((l) => (
              <MenuItem key={l} value={l}>{l}</MenuItem>
            ))}
          </TextField>
          <TextField
            label="External ID / Student Number"
            value={form.external_id}
            onChange={(e) => setForm({ ...form, external_id: e.target.value })}
            fullWidth
          />
          <TextField
            label="Notes (optional)"
            value={form.notes}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
            fullWidth
            multiline
            rows={2}
          />
          {error && <Alert severity="error">{error}</Alert>}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleAdd}
            disabled={saving || !form.name}
          >
            {saving ? "Saving…" : "Register"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete confirmation dialog */}
      <Dialog open={deleteConfirm !== null} onClose={() => setDeleteConfirm(null)}>
        <DialogTitle>Delete Child Profile?</DialogTitle>
        <DialogContent>
          <Typography>
            This will permanently remove this child's profile and all associated data.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirm(null)}>Cancel</Button>
          <Button
            color="error"
            variant="contained"
            onClick={() => deleteConfirm !== null && handleDelete(deleteConfirm)}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ChildrenList;
