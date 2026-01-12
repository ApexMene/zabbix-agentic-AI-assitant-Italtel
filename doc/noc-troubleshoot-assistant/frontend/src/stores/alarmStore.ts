import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Alarm, AlarmFilters } from '@/types';

interface AlarmState {
  alarms: Alarm[];
  filters: AlarmFilters;
  lastPollTime: Date | null;
  setAlarms: (alarms: Alarm[]) => void;
  setFilters: (filters: AlarmFilters) => void;
  clearFilters: () => void;
  updateLastPollTime: () => void;
}

const defaultFilters: AlarmFilters = {
  severities: [],
  acknowledged: undefined,
  host: undefined,
};

export const useAlarmStore = create<AlarmState>()(
  persist(
    (set) => ({
      alarms: [],
      filters: defaultFilters,
      lastPollTime: null,
      setAlarms: (alarms) => set({ alarms: Array.isArray(alarms) ? alarms : [] }),
      setFilters: (filters) => set({ filters }),
      clearFilters: () => set({ filters: defaultFilters }),
      updateLastPollTime: () => set({ lastPollTime: new Date() }),
    }),
    {
      name: 'alarm-filters',
      partialize: (state: AlarmState) => ({ filters: state.filters }),
    }
  )
);
