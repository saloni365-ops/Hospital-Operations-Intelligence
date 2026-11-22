import { create } from 'zustand';
import { api, type HospitalState } from '../api/client';
import type { Mode } from '../constants/modes';

type Store = {
  state: HospitalState | null; mode: Mode; speed: number; replay: boolean; replayHour: number | null; dark: boolean;
  online: boolean; busy: boolean; error: string;
  refresh: () => Promise<void>; start: (seed?: number) => Promise<void>; pause: () => Promise<void>; reset: (seed?: number) => Promise<void>; step: () => Promise<void>; setMode: (mode: Mode) => Promise<void>; setSettings: (seed: number, horizon: number) => Promise<void>; setSpeed: (speed: number) => void; setReplay: (value: boolean, hour?: number) => void; toggleDark: () => void;
};

export const useSimulationStore = create<Store>((set, get) => ({
  state: null, mode: 'hybrid', speed: 1, replay: false, replayHour: null, dark: false, online: false, busy: false, error: '',
  refresh: async () => { try { const state = await api.state(); set({ state, mode: state.mode, online: true, error: '' }); } catch { set({ online: false, error: 'Backend offline' }); } },
  start: async (seed) => { set({ busy: true }); try { set({ state: await api.start(seed ?? get().state?.seed ?? 42) }); } finally { set({ busy: false }); } },
  pause: async () => { set({ busy: true }); try { set({ state: await api.pause() }); } finally { set({ busy: false }); } },
  reset: async (seed) => { set({ busy: true }); try { set({ state: await api.reset(seed ?? get().state?.seed ?? 42) }); } finally { set({ busy: false }); } },
  step: async () => { if (get().replay) return; set({ busy: true }); try { set({ state: await api.step() }); } finally { set({ busy: false }); } },
  setMode: async (mode) => { set({ busy: true }); try { set({ mode, state: await api.mode(mode) }); } finally { set({ busy: false }); } },
  setSettings: async (seed, horizon) => { set({ busy: true }); try { set({ state: await api.settings(seed, horizon) }); } finally { set({ busy: false }); } },
  setSpeed: (speed) => set({ speed }), setReplay: (replay, replayHour) => set({ replay, replayHour: replayHour ?? null }),
  toggleDark: () => set((store) => { document.documentElement.dataset.theme = store.dark ? 'light' : 'dark'; return { dark: !store.dark }; }),
}));
