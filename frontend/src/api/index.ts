import axios from "axios";
import type {
  Child,
  ChildCreate,
  Test,
  StartTestResponse,
  SubmitResponsePayload,
  SubmitResponseResult,
  ModuleSummary,
  TestXAI,
  TestItemLog,
} from "../types";

// ──────────────────────────────────────────────
// Axios instance
// ──────────────────────────────────────────────
const api = axios.create({
  baseURL: "http://localhost:8000/api/v1",
  headers: { "Content-Type": "application/json" },
});

// ──────────────────────────────────────────────
// Children
// ──────────────────────────────────────────────

export const getChildren = async (): Promise<Child[]> => {
  const { data } = await api.get<Child[]>("/children/");
  console.log("data", data);
  return data;
};

export const getChild = async (childId: number): Promise<Child> => {
  const { data } = await api.get<Child>(`/children/${childId}`);
  return data;
};

export const createChild = async (child: ChildCreate): Promise<Child> => {
  const { data } = await api.post<Child>("/children/", child);
  return data;
};

export const deleteChild = async (childId: number): Promise<Child> => {
  const { data } = await api.delete<Child>(`/children/${childId}`);
  return data;
};

// ──────────────────────────────────────────────
// Tests
// ──────────────────────────────────────────────

export const getTests = async (childId?: number): Promise<Test[]> => {
  const params = childId !== undefined ? { child_id: childId } : {};
  const { data } = await api.get<Test[]>("/tests/", { params });
  return data;
};

export const getTest = async (testId: number): Promise<Test> => {
  const { data } = await api.get<Test>(`/tests/${testId}`);
  console.log("getTest", data);
  return data;
};

// ──────────────────────────────────────────────
// Adaptive testing
// ──────────────────────────────────────────────

export const startAdaptiveTest = async (
  childId: number,
  deviceId?: string,
): Promise<StartTestResponse> => {
  const { data } = await api.post<StartTestResponse>("/adaptive/start", {
    child_id: childId,
    device_id: deviceId ?? null,
  });
  return data;
};

export const submitResponse = async (
  testId: number,
  payload: SubmitResponsePayload,
): Promise<SubmitResponseResult> => {
  console.log("payload", payload);
  const { data } = await api.post<SubmitResponseResult>(
    `/adaptive/${testId}/responses`,
    payload,
  );
  return data;
};

// ──────────────────────────────────────────────
// Module summaries
// ──────────────────────────────────────────────

export const getModuleSummaries = async (
  testId: number,
): Promise<ModuleSummary[]> => {
  const { data } = await api.get<ModuleSummary[]>(
    `/module-summaries/test/${testId}`,
  );
  console.log("getXai", data);

  console.log("getModuleSummaries", data);

  return data;
};

// ──────────────────────────────────────────────
// XAI / Explainability
// ──────────────────────────────────────────────

export const getXai = async (testId: number): Promise<TestXAI[]> => {
  const { data } = await api.get<TestXAI[]>(`/xai/test/${testId}`);
  return data;
};

// ──────────────────────────────────────────────
// Item Logs (Trajectory)
// ──────────────────────────────────────────────

export const getTestItemLogs = async (testId: number): Promise<TestItemLog[]> => {
  const { data } = await api.get<TestItemLog[]>(`/logs/test/${testId}`);
  return data;
};

export default api;
