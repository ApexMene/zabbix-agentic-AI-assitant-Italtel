import { create } from 'zustand';
import { Instance } from '@/types';

interface InstanceState {
  instances: Instance[];
  selectedInstanceId: string | null;
  setInstances: (instances: Instance[]) => void;
  setSelectedInstance: (id: string | null) => void;
}

export const useInstanceStore = create<InstanceState>((set) => ({
  instances: [],
  selectedInstanceId: null,
  setInstances: (instances) => set({ instances: instances || [] }),
  setSelectedInstance: (id) => set({ selectedInstanceId: id }),
}));
