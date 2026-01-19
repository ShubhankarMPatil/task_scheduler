import api from "./axios";

import type { DashboardMetrics } from "@/types/dashboard";
import type { HabitTemplate } from "@/types/habitTemplate";
import type { Task } from "@/types/task";
import type { TimeEntry } from "@/types/timeEntry";

// Backwards-compatible default export so existing code can do:
//   import api from "@/lib/api";
export default api;

export type DateString = string; // YYYY-MM-DD

// -----------------------------
// Habit templates
// -----------------------------
export const listTemplates = async () => {
  const res = await api.get<HabitTemplate[]>("/templates/");
  return res.data;
};

export const createTemplate = async (payload: {
  title: string;
  description?: string;
  default_target_seconds?: number;
  is_active?: boolean;
}) => {
  const res = await api.post<HabitTemplate>("/templates/", payload);
  return res.data;
};

export const updateTemplate = async (
  id: number,
  patch: Partial<Pick<HabitTemplate, "title" | "description" | "default_target_seconds" | "is_active">>
) => {
  const res = await api.patch<HabitTemplate>(`/templates/${id}/`, patch);
  return res.data;
};

export const deleteTemplate = async (id: number) => {
  await api.delete(`/templates/${id}/`);
};

// -----------------------------
// Daily tasks
// -----------------------------
export const listTasks = async (date?: DateString) => {
  const res = await api.get<Task[]>("/tasks/", {
    params: date ? { date } : undefined,
  });
  return res.data;
};

// Backwards-compat for older components
export const getTasks = listTasks;

export const populateTasks = async (date?: DateString) => {
  const res = await api.post<{ created: number; date: string }>("/tasks/populate/", null, {
    params: date ? { date } : undefined,
  });
  return res.data;
};

export const createTask = async (payload: {
  title: string;
  description?: string;
  date?: DateString;
  target_seconds?: number;
}) => {
  const res = await api.post<Task>("/tasks/", payload);
  return res.data;
};

export const updateTask = async (
  id: number,
  patch: Partial<Pick<Task, "title" | "description" | "completed" | "target_seconds" | "date">>
) => {
  const res = await api.patch<Task>(`/tasks/${id}/`, patch);
  return res.data;
};

export const deleteTask = async (id: number) => {
  await api.delete(`/tasks/${id}/`);
};

export const startTimer = async (taskId: number) => {
  const res = await api.post<TimeEntry>(`/tasks/${taskId}/start-timer/`);
  return res.data;
};

export const stopTimer = async (taskId: number) => {
  const res = await api.post<TimeEntry>(`/tasks/${taskId}/stop-timer/`);
  return res.data;
};

export const listTimeEntries = async (taskId: number) => {
  const res = await api.get<TimeEntry[]>("/time-entries/", { params: { task: taskId } });
  return res.data;
};

export const deleteTimeEntry = async (id: number) => {
  await api.delete(`/time-entries/${id}/`);
};

// -----------------------------
// Dashboard + external APIs
// -----------------------------
export const getDashboard = async (date?: DateString) => {
  const res = await api.get<DashboardMetrics>("/dashboard/", {
    params: date ? { date } : undefined,
  });
  return res.data;
};

export type TaskStats = {
  date: string | null;
  total: number;
  completed: number;
  pending: number;
};

export const getTaskStats = async (date?: DateString) => {
  const res = await api.get<TaskStats>("/tasks/stats/", {
    params: date ? { date } : undefined,
  });
  return res.data;
};

export const getWorldTime = async () => {
  const res = await api.get<{ timezone?: string; datetime?: string; utc_offset?: string }>(
    "/tasks/world-time/"
  );
  return res.data;
};
