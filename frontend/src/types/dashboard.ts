export type TasksByStatus = {
  status: string;
  count: number;
};

export type TimePerTask = {
  task_id: number;
  task__title: string;
  task__target_seconds: number;
  total_time: number;
};

export type ProductivityTrend = {
  date: string;
  total_time: number;
};

export type DashboardSummary = {
  tasks_count: number;
  tasks_completed: number;
  targets_reached: number;
  total_target_seconds: number;
  total_tracked_seconds: number;
};

export interface DashboardMetrics {
  date: string;
  summary: DashboardSummary;
  tasks_by_status: TasksByStatus[];
  time_per_task: TimePerTask[];
  productivity_trend: ProductivityTrend[];
}
