// Type definitions for the application

export interface Instance {
  id: string;
  name: string;
  status: 'connected' | 'disconnected' | 'error';
  version?: string;
  error?: string;
  problem_counts?: {
    disaster: number;
    high: number;
    average: number;
    warning: number;
    information: number;
  };
  last_sync?: string;
}

export interface Alarm {
  id: string;
  instance_id: string;
  instance_name: string;
  host: string;
  description: string;
  severity: 'disaster' | 'high' | 'average' | 'warning' | 'information' | 'not_classified';
  severity_code: number;
  duration: string;
  acknowledged: boolean;
  event_id: string;
  is_synthetic: boolean;
  started_at?: string;
}

export interface AlarmStats {
  total: number;
  by_severity: {
    disaster: number;
    high: number;
    average: number;
    warning: number;
    information: number;
    not_classified: number;
  };
  synthetic: number;
  zabbix: number;
  last_poll: string | null;
}

export interface AlarmFilters {
  instance_id?: string;
  severities: string[];
  acknowledged?: boolean;
  host?: string;
}

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  services: {
    database: string;
    mcp_server: string;
  };
  alarm_stats: AlarmStats;
}
