"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import TaskChart from "@/components/TaskChart";
import WorldTimePanel from "@/components/WorldTimePanel";
import {
  createTask,
  createTemplate,
  deleteTask,
  deleteTemplate,
  deleteTimeEntry,
  getDashboard,
  getTaskStats,
  listTasks,
  listTemplates,
  listTimeEntries,
  populateTasks,
  startTimer,
  stopTimer,
  updateTask,
  updateTemplate,
} from "@/lib/api";
import type { DashboardMetrics } from "@/types/dashboard";
import type { TaskStats } from "@/lib/api";
import type { HabitTemplate } from "@/types/habitTemplate";
import type { Task } from "@/types/task";
import type { TimeEntry } from "@/types/timeEntry";

function todayISO() {
  // en-CA is reliably YYYY-MM-DD in most browsers.
  return new Date().toLocaleDateString("en-CA");
}

function toSeconds(hours: number, minutes: number) {
  return Math.max(0, Math.floor(hours)) * 3600 + Math.max(0, Math.floor(minutes)) * 60;
}

function formatSeconds(total: number) {
  const s = Math.max(0, Math.floor(total));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const ss = s % 60;
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${ss}s`;
  return `${ss}s`;
}

function liveProgressSeconds(task: Task, nowMs: number) {
  if (!task.has_active_timer || !task.active_entry_start_time) return task.total_time_seconds;
  const started = new Date(task.active_entry_start_time).getTime();
  const delta = Math.max(0, Math.floor((nowMs - started) / 1000));
  return task.total_time_seconds + delta;
}

export default function TasksPage() {
  const [selectedDate, setSelectedDate] = useState(todayISO());

  const [templates, setTemplates] = useState<HabitTemplate[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [dashboard, setDashboard] = useState<DashboardMetrics | null>(null);
  const [stats, setStats] = useState<TaskStats | null>(null);

  const [apiErrors, setApiErrors] = useState<{
    templates?: string;
    tasks?: string;
    dashboard?: string;
    stats?: string;
    entries?: string;
  }>({});

  const [expandedTaskId, setExpandedTaskId] = useState<number | null>(null);
  const [entries, setEntries] = useState<TimeEntry[]>([]);

  const [nowMs, setNowMs] = useState(() => Date.now());

  // Create template form
  const [newTemplateTitle, setNewTemplateTitle] = useState("");
  const [newTemplateDescription, setNewTemplateDescription] = useState("");
  const [newTemplateHours, setNewTemplateHours] = useState(0);
  const [newTemplateMinutes, setNewTemplateMinutes] = useState(30);

  // Create ad-hoc task form
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [newTaskDescription, setNewTaskDescription] = useState("");
  const [newTaskHours, setNewTaskHours] = useState(0);
  const [newTaskMinutes, setNewTaskMinutes] = useState(30);

  // Live ticking for running timer display
  useEffect(() => {
    const id = window.setInterval(() => setNowMs(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, []);

  const refreshTemplates = useCallback(() => {
    listTemplates()
      .then(data => {
        setApiErrors(prev => ({ ...prev, templates: undefined }));
        setTemplates(data);
      })
      .catch(() => {
        setTemplates([]);
        setApiErrors(prev => ({ ...prev, templates: "Failed to load templates." }));
      });
  }, []);

  const refreshTasksAndSummary = useCallback((date: string) => {
    Promise.allSettled([listTasks(date), getDashboard(date), getTaskStats(date)]).then(results => {
      const [tasksRes, dashboardRes, statsRes] = results;

      if (tasksRes.status === "fulfilled") {
        setApiErrors(prev => ({ ...prev, tasks: undefined }));
        setTasks(tasksRes.value);
      } else {
        setTasks([]);
        setApiErrors(prev => ({ ...prev, tasks: "Failed to load tasks." }));
      }

      if (dashboardRes.status === "fulfilled") {
        setApiErrors(prev => ({ ...prev, dashboard: undefined }));
        setDashboard(dashboardRes.value);
      } else {
        // Keep dashboard rendering stable even if the API fails.
        setDashboard({
          date,
          summary: {
            tasks_count: 0,
            tasks_completed: 0,
            targets_reached: 0,
            total_target_seconds: 0,
            total_tracked_seconds: 0,
          },
          tasks_by_status: [
            { status: "completed", count: 0 },
            { status: "pending", count: 0 },
          ],
          time_per_task: [],
          productivity_trend: [],
        });
        setApiErrors(prev => ({ ...prev, dashboard: "Failed to load dashboard." }));
      }

      if (statsRes.status === "fulfilled") {
        setApiErrors(prev => ({ ...prev, stats: undefined }));
        setStats(statsRes.value);
      } else {
        setStats({ date, total: 0, completed: 0, pending: 0 });
        setApiErrors(prev => ({ ...prev, stats: "Failed to load stats." }));
      }
    });
  }, []);

  useEffect(() => {
    refreshTemplates();
  }, [refreshTemplates]);

  useEffect(() => {
    refreshTasksAndSummary(selectedDate);

    // Collapse entries panel when switching days (avoid setState directly in effect body).
    Promise.resolve().then(() => {
      setExpandedTaskId(null);
      setEntries([]);
    });
  }, [selectedDate, refreshTasksAndSummary]);

  const statusCounts = useMemo(() => {
    // Prefer the dedicated /api/tasks/stats/ endpoint (assignment requirement).
    if (stats) {
      return { completed: stats.completed, pending: stats.pending };
    }

    // Fallback to dashboard data while initial fetch is in flight.
    const completed = dashboard?.tasks_by_status.find(x => x.status === "completed")?.count ?? 0;
    const pending = dashboard?.tasks_by_status.find(x => x.status === "pending")?.count ?? 0;
    return { completed, pending };
  }, [dashboard, stats]);

  const runningTask = useMemo(() => tasks.find(t => t.has_active_timer), [tasks]);

  const openEntries = (taskId: number) => {
    if (expandedTaskId === taskId) {
      setExpandedTaskId(null);
      setEntries([]);
      return;
    }

    setExpandedTaskId(taskId);
    listTimeEntries(taskId)
      .then(data => {
        setApiErrors(prev => ({ ...prev, entries: undefined }));
        setEntries(data);
      })
      .catch(() => {
        setEntries([]);
        setApiErrors(prev => ({ ...prev, entries: "Failed to load time entries." }));
      });
  };

  const errorMessages = useMemo(
    () => Object.values(apiErrors).filter((x): x is string => Boolean(x)),
    [apiErrors]
  );

  return (
    <div className="min-h-screen p-6">
      {errorMessages.length > 0 ? (
        <div className="bg-red-50 border border-red-200 text-red-800 rounded-xl p-4 mb-6 text-sm">
          <div className="font-medium">Some data failed to load</div>
          <ul className="list-disc pl-5 mt-1 space-y-1">
            {errorMessages.map((msg, idx) => (
              <li key={idx}>{msg}</li>
            ))}
          </ul>
        </div>
      ) : null}

      <div className="flex items-center justify-between gap-4 flex-wrap mb-6">
        <h1 className="text-3xl font-semibold">Habit / Task Tracker</h1>
        <div className="flex items-center gap-3">
          <label className="text-sm text-gray-700">Date</label>
          <input
            className="border rounded-lg px-3 py-2"
            type="date"
            value={selectedDate}
            onChange={e => setSelectedDate(e.target.value)}
          />
          <button
            className="border rounded-lg px-3 py-2"
            onClick={() => refreshTasksAndSummary(selectedDate)}
          >
            Refresh
          </button>
        </div>
      </div>

      {runningTask ? (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-6">
          <div className="text-sm text-yellow-800">
            Timer running: <strong>{runningTask.title}</strong>
          </div>
        </div>
      ) : null}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Habit templates */}
          <div className="bg-white rounded-xl shadow p-5">
            <h2 className="text-lg font-medium mb-3">Habit templates</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <input
                className="border rounded-lg px-3 py-2"
                placeholder="Template title"
                value={newTemplateTitle}
                onChange={e => setNewTemplateTitle(e.target.value)}
              />
              <input
                className="border rounded-lg px-3 py-2"
                placeholder="Description (optional)"
                value={newTemplateDescription}
                onChange={e => setNewTemplateDescription(e.target.value)}
              />
              <div className="flex gap-2 items-center">
                <input
                  className="border rounded-lg px-3 py-2 w-24"
                  type="number"
                  min={0}
                  value={newTemplateHours}
                  onChange={e => setNewTemplateHours(Number(e.target.value))}
                />
                <span className="text-sm text-gray-600">hours</span>
                <input
                  className="border rounded-lg px-3 py-2 w-24"
                  type="number"
                  min={0}
                  value={newTemplateMinutes}
                  onChange={e => setNewTemplateMinutes(Number(e.target.value))}
                />
                <span className="text-sm text-gray-600">minutes</span>
              </div>
              <button
                className="bg-black text-white px-4 py-2 rounded-lg"
                onClick={() => {
                  const title = newTemplateTitle.trim();
                  if (!title) return;

                  createTemplate({
                    title,
                    description: newTemplateDescription.trim() || undefined,
                    default_target_seconds: toSeconds(newTemplateHours, newTemplateMinutes),
                    is_active: true,
                  }).then(() => {
                    setNewTemplateTitle("");
                    setNewTemplateDescription("");
                    refreshTemplates();
                  });
                }}
              >
                Add template
              </button>
            </div>

            <div className="mt-4">
              {templates.length === 0 ? (
                <p className="text-sm text-gray-500">No templates yet.</p>
              ) : (
                <ul className="space-y-2">
                  {templates.map(t => (
                    <li key={t.id} className="border rounded-lg p-3">
                      <div className="flex items-center justify-between gap-3 flex-wrap">
                        <div>
                          <div className="font-medium">{t.title}</div>
                          {t.description ? (
                            <div className="text-sm text-gray-600">{t.description}</div>
                          ) : null}
                          <div className="text-sm text-gray-700 mt-1">
                            Target: {formatSeconds(t.default_target_seconds)}
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <label className="text-sm flex items-center gap-2">
                            <input
                              type="checkbox"
                              checked={t.is_active}
                              onChange={() =>
                                updateTemplate(t.id, { is_active: !t.is_active }).then(refreshTemplates)
                              }
                            />
                            Active
                          </label>
                          <button
                            className="border rounded-lg px-3 py-2"
                            onClick={() => {
                              const newTitle = window.prompt("Template title", t.title);
                              if (!newTitle) return;
                              const secondsStr = window.prompt(
                                "Daily target seconds",
                                String(t.default_target_seconds)
                              );
                              if (secondsStr === null) return;
                              const secs = Number(secondsStr);

                              updateTemplate(t.id, {
                                title: newTitle,
                                default_target_seconds: Number.isFinite(secs) ? secs : t.default_target_seconds,
                              }).then(refreshTemplates);
                            }}
                          >
                            Edit
                          </button>
                          <button
                            className="border rounded-lg px-3 py-2"
                            onClick={() => deleteTemplate(t.id).then(refreshTemplates)}
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Daily plan */}
          <div className="bg-white rounded-xl shadow p-5">
            <div className="flex items-center justify-between gap-3 flex-wrap">
              <h2 className="text-lg font-medium">Daily plan</h2>
              <button
                className="bg-black text-white px-4 py-2 rounded-lg"
                onClick={() => populateTasks(selectedDate).then(() => refreshTasksAndSummary(selectedDate))}
              >
                Populate from templates
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
              <input
                className="border rounded-lg px-3 py-2"
                placeholder="Task title"
                value={newTaskTitle}
                onChange={e => setNewTaskTitle(e.target.value)}
              />
              <input
                className="border rounded-lg px-3 py-2"
                placeholder="Description (optional)"
                value={newTaskDescription}
                onChange={e => setNewTaskDescription(e.target.value)}
              />
              <div className="flex gap-2 items-center">
                <input
                  className="border rounded-lg px-3 py-2 w-24"
                  type="number"
                  min={0}
                  value={newTaskHours}
                  onChange={e => setNewTaskHours(Number(e.target.value))}
                />
                <span className="text-sm text-gray-600">hours</span>
                <input
                  className="border rounded-lg px-3 py-2 w-24"
                  type="number"
                  min={0}
                  value={newTaskMinutes}
                  onChange={e => setNewTaskMinutes(Number(e.target.value))}
                />
                <span className="text-sm text-gray-600">minutes</span>
              </div>
              <button
                className="border rounded-lg px-4 py-2"
                onClick={() => {
                  const title = newTaskTitle.trim();
                  if (!title) return;

                  createTask({
                    title,
                    description: newTaskDescription.trim() || undefined,
                    date: selectedDate,
                    target_seconds: toSeconds(newTaskHours, newTaskMinutes),
                  }).then(() => {
                    setNewTaskTitle("");
                    setNewTaskDescription("");
                    refreshTasksAndSummary(selectedDate);
                  });
                }}
              >
                Add task
              </button>
            </div>

            <div className="mt-5">
              {tasks.length === 0 ? (
                <p className="text-sm text-gray-500">No tasks for this day yet.</p>
              ) : (
                <ul className="space-y-3">
                  {tasks.map(task => {
                    const progress = liveProgressSeconds(task, nowMs);
                    const target = task.target_seconds;
                    const percent = target > 0 ? Math.min(100, (progress / target) * 100) : 0;

                    return (
                      <li key={task.id} className="border rounded-xl p-4">
                        <div className="flex items-start justify-between gap-3 flex-wrap">
                          <div className="min-w-[240px]">
                            <div className="flex items-center gap-3">
                              <input
                                type="checkbox"
                                checked={task.completed}
                                onChange={() =>
                                  updateTask(task.id, { completed: !task.completed }).then(() =>
                                    refreshTasksAndSummary(selectedDate)
                                  )
                                }
                              />
                              <div className="font-medium">{task.title}</div>
                              {task.habit_template_id ? (
                                <span className="text-xs bg-gray-200 px-2 py-1 rounded">template</span>
                              ) : (
                                <span className="text-xs bg-gray-100 px-2 py-1 rounded">ad-hoc</span>
                              )}
                            </div>
                            {task.description ? (
                              <div className="text-sm text-gray-600 mt-1">{task.description}</div>
                            ) : null}

                            <div className="text-sm text-gray-700 mt-2">
                              Progress: {formatSeconds(progress)} /{" "}
                              {target > 0 ? formatSeconds(target) : "No target"}
                              {task.target_reached ? " (reached)" : ""}
                            </div>

                            <div className="h-2 bg-gray-200 rounded mt-2 overflow-hidden">
                              <div
                                className="h-2 bg-green-600"
                                style={{ width: `${percent}%` }}
                              />
                            </div>
                          </div>

                          <div className="flex items-center gap-2 flex-wrap">
                            {task.has_active_timer ? (
                              <button
                                className="bg-black text-white px-3 py-2 rounded-lg"
                                onClick={() => stopTimer(task.id).then(() => refreshTasksAndSummary(selectedDate))}
                              >
                                Stop
                              </button>
                            ) : (
                              <button
                                className="bg-black text-white px-3 py-2 rounded-lg"
                                onClick={() => startTimer(task.id).then(() => refreshTasksAndSummary(selectedDate))}
                              >
                                Start
                              </button>
                            )}

                            <button
                              className="border rounded-lg px-3 py-2"
                              onClick={() => openEntries(task.id)}
                            >
                              {expandedTaskId === task.id ? "Hide entries" : "Time entries"}
                            </button>

                            <button
                              className="border rounded-lg px-3 py-2"
                              onClick={() => {
                                const newTitle = window.prompt("Task title", task.title);
                                if (!newTitle) return;
                                updateTask(task.id, { title: newTitle }).then(() => refreshTasksAndSummary(selectedDate));
                              }}
                            >
                              Rename
                            </button>

                            <button
                              className="border rounded-lg px-3 py-2"
                              onClick={() => {
                                const secondsStr = window.prompt(
                                  "Daily target seconds",
                                  String(task.target_seconds)
                                );
                                if (secondsStr === null) return;
                                const secs = Number(secondsStr);
                                if (!Number.isFinite(secs)) return;
                                updateTask(task.id, { target_seconds: secs }).then(() => refreshTasksAndSummary(selectedDate));
                              }}
                            >
                              Set target
                            </button>

                            <button
                              className="border rounded-lg px-3 py-2"
                              onClick={() => deleteTask(task.id).then(() => refreshTasksAndSummary(selectedDate))}
                            >
                              Delete
                            </button>
                          </div>
                        </div>

                        {expandedTaskId === task.id ? (
                          <div className="mt-4 border-t pt-3">
                            <div className="font-medium mb-2">Time entries</div>
                            {entries.length === 0 ? (
                              <p className="text-sm text-gray-500">No entries yet.</p>
                            ) : (
                              <ul className="space-y-2">
                                {entries.map(e => (
                                  <li
                                    key={e.id}
                                    className="flex items-center justify-between gap-3 border rounded-lg px-3 py-2"
                                  >
                                    <div className="text-sm">
                                      {new Date(e.start_time).toLocaleString()} →{" "}
                                      {e.end_time
                                        ? new Date(e.end_time).toLocaleString()
                                        : "(running)"}
                                      {" "}
                                      <span className="text-gray-600">
                                        ({formatSeconds(e.duration_seconds)})
                                      </span>
                                    </div>
                                    <button
                                      className="text-sm underline"
                                      onClick={() =>
                                        deleteTimeEntry(e.id)
                                          .then(() => listTimeEntries(task.id))
                                          .then(data => {
                                            setApiErrors(prev => ({ ...prev, entries: undefined }));
                                            setEntries(data);
                                          })
                                          .catch(() => setApiErrors(prev => ({ ...prev, entries: "Failed to update time entries." })))
                                      }
                                    >
                                      Delete
                                    </button>
                                  </li>
                                ))}
                              </ul>
                            )}
                          </div>
                        ) : null}
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <WorldTimePanel />

          <div className="bg-white rounded-xl shadow p-5">
            <h2 className="font-medium mb-2">Daily summary</h2>
            {dashboard ? (
              <div className="text-sm text-gray-700 space-y-1">
                <div>
                  Tasks: {dashboard.summary.tasks_count} (completed: {dashboard.summary.tasks_completed})
                </div>
                <div>Targets reached: {dashboard.summary.targets_reached}</div>
                <div>
                  Total tracked: {formatSeconds(dashboard.summary.total_tracked_seconds)}
                </div>
                <div>
                  Total target: {formatSeconds(dashboard.summary.total_target_seconds)}
                </div>
              </div>
            ) : (
              <p className="text-sm text-gray-500">Loading…</p>
            )}
          </div>

          <TaskChart completed={statusCounts.completed} pending={statusCounts.pending} />
        </div>
      </div>
    </div>
  );
}
