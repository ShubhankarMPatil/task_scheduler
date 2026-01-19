export interface Task {
  id: number;
  title: string;
  description: string;

  habit_template_id: number | null;
  date: string; // YYYY-MM-DD
  target_seconds: number;

  completed: boolean;
  created_at: string;

  // Computed server-side
  has_active_timer: boolean;
  active_entry_start_time: string | null;
  total_time_seconds: number;
  progress_seconds: number;
  remaining_seconds: number;
  progress_percent: number;
  target_reached: boolean;
}
