import { Instance, Alarm, AlarmStats, HealthStatus } from '@/types';

const API_BASE = '';

class ApiService {
  // Health
  async getHealth(): Promise<HealthStatus> {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) throw new Error('Failed to fetch health');
    return response.json();
  }

  // Instances
  async getInstances(): Promise<Instance[]> {
    const response = await fetch(`${API_BASE}/api/instances`);
    if (!response.ok) throw new Error('Failed to fetch instances');
    return response.json();
  }

  async getInstanceStatus(instanceId: string): Promise<Instance> {
    const response = await fetch(`${API_BASE}/api/instances/${instanceId}/status`);
    if (!response.ok) throw new Error('Failed to fetch instance status');
    return response.json();
  }

  // Alarms
  async getAlarms(filters?: {
    instance_id?: string;
    severity?: string[];
    acknowledged?: boolean;
    host?: string;
  }): Promise<Alarm[]> {
    const params = new URLSearchParams();
    if (filters?.instance_id) params.append('instance_id', filters.instance_id);
    if (filters?.severity) filters.severity.forEach(s => params.append('severity', s));
    if (filters?.acknowledged !== undefined) params.append('acknowledged', String(filters.acknowledged));
    if (filters?.host) params.append('host', filters.host);

    const url = `${API_BASE}/api/alarms${params.toString() ? '?' + params.toString() : ''}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch alarms');
    return response.json();
  }

  async getAlarmStats(): Promise<AlarmStats> {
    const response = await fetch(`${API_BASE}/api/alarms/stats`);
    if (!response.ok) throw new Error('Failed to fetch alarm stats');
    return response.json();
  }

  async acknowledgeAlarm(alarmId: string, instanceId: string, message?: string): Promise<void> {
    const response = await fetch(`${API_BASE}/api/alarms/${alarmId}/acknowledge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ instance_id: instanceId, message: message || '' }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to acknowledge alarm');
    }
  }

  // Chat / Investigation
  async createInvestigation(alarmId: string, instanceId: string): Promise<{ investigation_id: string; alarm: any }> {
    const response = await fetch(`${API_BASE}/api/chat/investigation/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ alarm_id: alarmId, instance_id: instanceId }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create investigation');
    }
    return response.json();
  }

  streamInvestigation(investigationId: string): EventSource {
    return new EventSource(`${API_BASE}/api/chat/investigation/${investigationId}/stream`);
  }
}

export const api = new ApiService();
