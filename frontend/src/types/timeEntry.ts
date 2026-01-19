export interface TimeEntry {
  id: number;
  task: number;
  start_time: string;
  end_time: string | null;
  duration_seconds: number;
  created_at: string;
}
