export type Mode = 'hybrid' | 'quantum' | 'predictive';
export const MODE_ORDER: Mode[] = ['hybrid', 'quantum', 'predictive'];
export const MODE_IDENTITY: Record<Mode, { name: string; shortName: string; number: number; color: string; icon: string; description: string }> = {
  hybrid: { name: 'Dynamic Hybrid Intelligence', shortName: 'Hybrid', number: 3, color: '#12B5A6', icon: '◈', description: 'Forecast, optimize, and replan after disruptions' },
  quantum: { name: 'Quantum Optimization', shortName: 'Quantum', number: 2, color: '#7C5CFF', icon: '◇', description: 'Solve a nurse-allocation QUBO locally' },
  predictive: { name: 'Predictive AI', shortName: 'Predictive', number: 1, color: '#FFB020', icon: '↗', description: 'Allocate from forecast demand forecasts' },
};
