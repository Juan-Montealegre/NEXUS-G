
import React from 'react';
import { SystemMetrics, CommandEntry } from '../types';
import { ICONS } from '../constants';

interface DashboardProps {
  metrics: SystemMetrics;
  history: CommandEntry[];
  onSend: (cmd: string) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ metrics, history, onSend }) => {
  const [input, setInput] = React.useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSend(input);
    setInput('');
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard label="CPU Usage" value={`${metrics.cpu}%`} color="indigo" />
        <MetricCard label="RAM Usage" value={`${metrics.ram.toFixed(1)}%`} color="cyan" />
        <MetricCard label="Disk I/O" value={`${metrics.disk}%`} color="emerald" />
        <MetricCard label="Uptime" value={metrics.uptime} color="amber" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Command */}
        <div className="lg:col-span-2 space-y-6">
          <section className="glass p-6 rounded-3xl border border-slate-800 shadow-xl">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <ICONS.Terminal /> Quick Directive
            </h3>
            <form onSubmit={handleSubmit} className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask Jarvis to do something..."
                className="flex-1 bg-slate-900/50 border border-slate-800 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all text-slate-200 placeholder:text-slate-600"
              />
              <button 
                type="submit"
                className="bg-indigo-600 hover:bg-indigo-500 text-white p-3 rounded-xl transition-all shadow-lg shadow-indigo-600/20 active:scale-95"
              >
                <ICONS.Send />
              </button>
            </form>
            <div className="mt-4 flex flex-wrap gap-2">
              {['System check', 'Get local weather', 'Uptime status', 'List active tasks'].map(btn => (
                <button 
                  key={btn}
                  onClick={() => onSend(btn)}
                  className="text-[11px] font-bold uppercase tracking-wider px-3 py-1 rounded-full bg-slate-800 text-slate-400 hover:text-indigo-400 hover:bg-indigo-400/10 transition-all"
                >
                  {btn}
                </button>
              ))}
            </div>
          </section>

          {/* Recent History */}
          <section className="glass p-6 rounded-3xl border border-slate-800 shadow-xl overflow-hidden">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold">Activity Log</h3>
              <span className="text-xs text-slate-500 uppercase font-bold tracking-widest">Live Updates</span>
            </div>
            <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2">
              {history.length === 0 ? (
                <div className="text-center py-10 text-slate-600">
                  No recent activity recorded.
                </div>
              ) : (
                history.slice(0, 5).map(item => (
                  <div key={item.id} className="flex flex-col gap-1 p-4 rounded-2xl bg-slate-900/30 border border-slate-800/50">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-semibold text-indigo-400 mono">{item.command}</span>
                      <span className="text-[10px] text-slate-600">{item.timestamp.toLocaleTimeString()}</span>
                    </div>
                    <p className="text-sm text-slate-400 mt-1 line-clamp-2">{item.response}</p>
                  </div>
                ))
              )}
            </div>
          </section>
        </div>

        {/* Right Panel: Architecture Summary */}
        <div className="space-y-6">
          <section className="p-6 rounded-3xl bg-indigo-600 shadow-2xl shadow-indigo-600/20 text-white relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-20 group-hover:scale-110 transition-transform">
              <ICONS.Activity />
            </div>
            <h3 className="text-xl font-bold mb-2">Architectural Blueprint</h3>
            <p className="text-indigo-100 text-sm mb-4 leading-relaxed">
              This client is designed for maximum scalability using a unified React codebase wrapped by <strong>Tauri</strong> for Desktop and <strong>Capacitor</strong> for Mobile.
            </p>
            <ul className="text-xs space-y-2 text-indigo-200">
              <li className="flex items-center gap-2">
                <div className="w-1 h-1 bg-white rounded-full" />
                REST API for stateless actions
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1 h-1 bg-white rounded-full" />
                WebSockets for real-time telemetry
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1 h-1 bg-white rounded-full" />
                Local SQLite via Tauri-plugin-sql
              </li>
            </ul>
          </section>

          <section className="glass p-6 rounded-3xl border border-slate-800">
            <h3 className="text-sm font-bold uppercase tracking-widest text-slate-500 mb-4">System Alerts</h3>
            <div className="space-y-3">
              <div className="flex gap-3 items-start p-3 rounded-xl bg-amber-500/5 border border-amber-500/10">
                <div className="w-2 h-2 rounded-full bg-amber-500 mt-1.5 shadow-[0_0_8px_rgba(245,158,11,0.5)]" />
                <p className="text-xs text-amber-200/80">CPU thermal spike detected on Core 3 (72°C).</p>
              </div>
              <div className="flex gap-3 items-start p-3 rounded-xl bg-indigo-500/5 border border-indigo-500/10">
                <div className="w-2 h-2 rounded-full bg-indigo-500 mt-1.5 shadow-[0_0_8px_rgba(99,102,241,0.5)]" />
                <p className="text-xs text-indigo-200/80">New security patch available for Jarvis Core v2.4.</p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

const MetricCard: React.FC<{ label: string; value: string; color: string }> = ({ label, value, color }) => {
  const colorClasses = {
    indigo: 'from-indigo-500/20 text-indigo-400 border-indigo-500/20',
    cyan: 'from-cyan-500/20 text-cyan-400 border-cyan-500/20',
    emerald: 'from-emerald-500/20 text-emerald-400 border-emerald-500/20',
    amber: 'from-amber-500/20 text-amber-400 border-amber-500/20',
  }[color] || '';

  return (
    <div className={`p-6 rounded-3xl border bg-gradient-to-br bg-slate-900/40 shadow-lg ${colorClasses}`}>
      <p className="text-[10px] font-bold uppercase tracking-widest mb-1 opacity-70">{label}</p>
      <p className="text-2xl font-bold tracking-tight">{value}</p>
      <div className="mt-4 h-1 w-full bg-slate-800 rounded-full overflow-hidden">
        <div className={`h-full bg-current opacity-60 w-3/4 animate-pulse`} />
      </div>
    </div>
  );
};

export default Dashboard;
