
import React from 'react';
import { JarvisConfig } from '../types';

interface SettingsProps {
  config: JarvisConfig;
  setConfig: React.Dispatch<React.SetStateAction<JarvisConfig>>;
}

const Settings: React.FC<SettingsProps> = ({ config, setConfig }) => {
  const handleChange = (key: keyof JarvisConfig, value: any) => {
    const newConfig = { ...config, [key]: value };
    setConfig(newConfig);
    localStorage.setItem('jarvis_config', JSON.stringify(newConfig));
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-in fade-in duration-500">
      <section className="glass rounded-3xl border border-slate-800 p-8 shadow-2xl">
        <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
          Network Connectivity
        </h3>
        
        <div className="space-y-6">
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-widest text-slate-500">Core REST Endpoint</label>
            <input 
              type="text" 
              value={config.backendUrl}
              onChange={(e) => handleChange('backendUrl', e.target.value)}
              className="w-full bg-slate-900/50 border border-slate-800 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 text-slate-200"
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-widest text-slate-500">Real-time WebSocket URL</label>
            <input 
              type="text" 
              value={config.wsUrl}
              onChange={(e) => handleChange('wsUrl', e.target.value)}
              className="w-full bg-slate-900/50 border border-slate-800 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 text-slate-200"
            />
          </div>

          <div className="pt-4 flex items-center justify-between">
            <div className="space-y-0.5">
              <h4 className="font-semibold">Auto-reconnect</h4>
              <p className="text-xs text-slate-500 leading-relaxed">Attempt to restore connection automatically on loss.</p>
            </div>
            <button 
              onClick={() => handleChange('autoConnect', !config.autoConnect)}
              className={`w-12 h-6 rounded-full transition-all relative ${config.autoConnect ? 'bg-indigo-600' : 'bg-slate-800'}`}
            >
              <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all ${config.autoConnect ? 'left-7' : 'left-1'}`} />
            </button>
          </div>
        </div>
      </section>

      <section className="glass rounded-3xl border border-slate-800 p-8 shadow-2xl">
        <h3 className="text-xl font-bold mb-6">Security & Authentication</h3>
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-widest text-slate-500">System API Key</label>
            <input 
              type="password" 
              value={config.apiKey}
              onChange={(e) => handleChange('apiKey', e.target.value)}
              placeholder="••••••••••••••••••••••••"
              className="w-full bg-slate-900/50 border border-slate-800 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 text-slate-200"
            />
            <p className="text-[10px] text-slate-600">Requires master administrative privileges to change.</p>
          </div>
        </div>
      </section>

      <div className="flex justify-end pt-4">
        <button className="bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold py-3 px-8 rounded-2xl transition-all shadow-xl active:scale-95">
          Reset to Factory Defaults
        </button>
      </div>
    </div>
  );
};

export default Settings;
