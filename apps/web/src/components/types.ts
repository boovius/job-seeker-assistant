export type Job = {
  id: string;
  canonical_url?: string | null;
  title?: string;
  company_name?: string;
  location?: string | null;
  remote_flag?: boolean | null;
  description?: string | null;
  status?: string;
};

export type QueueItem = {
  id: string;
  task_type: string;
  status: string;
  attempts: number;
  last_error?: string | null;
};

export type PipelineEvent = {
  id: string;
  event_type: string;
  message?: string | null;
  payload?: Record<string, unknown> | null;
  created_at?: string;
  task_id?: string | null;
};

export type Preferences = {
  location: string;
  work_mode: string;
  salary: string;
  salary_period: string;
  sector: string;
  target_role: string;
  company_size: string;
};
