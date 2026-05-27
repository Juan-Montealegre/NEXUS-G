
import React from 'react';
import { ConnectionStatus } from '../types';

interface SidebarProps {
  status: ConnectionStatus;
  metrics: {
    cpu: number;
    ram: number;
    battery: number;
    temp: number;
  };
}

const Sidebar: React.FC<SidebarProps> = ({ metrics }) => {
  // Limitar valores para evitar errores visuales
  const battery = Math.max(0, Math.min(100, metrics.battery ?? 0));
  const cpu = Math.max(0, Math.min(100, metrics.cpu ?? 0));
  const ram = Math.max(0, Math.min(100, metrics.ram ?? 0));
  return (
    <div className="absolute left-0 top-0 h-full w-80 p-12 flex flex-col z-40 pointer-events-none">
      {/* Identidad de Marca HUD */}
      <div className="mb-20 border-l-4 border-red-600 pl-6 transform skew-x-[-10deg] flex flex-col items-start">
        <img src="/nexus.jpg" alt="Nexus Logo" className="w-16 h-16 rounded-full mb-3 shadow-[0_0_24px_#ff0000] border-2 border-red-600 bg-black object-cover" />
        <div className="orbitron text-4xl font-black text-red-600 tracking-tighter italic glow-red">NEXUS-G</div>
        <div className="text-[10px] text-red-900 font-bold uppercase tracking-[0.5em] mt-2 ml-1">NÚCLEO_GLOBAL_V3</div>
      </div>
      {/* Monitor de Energía Real */}
      <div className="mb-14 p-5 hud-glass rounded-2xl pointer-events-auto border-l-2 border-l-red-600">
        <div className="flex justify-between items-center mb-4">
          <span className="text-[10px] orbitron text-red-900 font-black tracking-widest uppercase">Nivel_Energía</span>
          <span className={`text-[12px] font-black orbitron ${battery < 20 ? 'text-amber-500 animate-pulse' : 'text-red-500'}`}>
            {battery}%
          </span>
        </div>
        <div className="flex gap-1.5 h-2 items-center">
          {[...Array(10)].map((_, i) => (
            <div 
              key={i} 
              className={`h-full flex-1 rounded-sm transition-all duration-1000 ${
                (i + 1) * 10 <= battery ? 'bg-red-600 shadow-[0_0_8px_rgba(255,0,0,0.4)]' : 'bg-red-950/20'
              }`}
            />
          ))}
        </div>
      </div>
      {/* Telemetría de Rendimiento */}
      <div className="space-y-12 pl-2">
        <MetricBlock label="CARGA_PROCESADOR" value={cpu} unit="%" />
        <MetricBlock label="MEMORIA_DINÁMICA" value={ram} unit="%" />
      </div>
      {/* Estado de Encriptación */}
      <div className="mt-auto opacity-40">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-2 h-2 bg-red-600 rounded-full animate-pulse"></div>
          <div className="text-[8px] orbitron font-bold tracking-[0.3em] uppercase">Enlace_Seguro</div>
        </div>
        <div className="text-[10px] font-mono leading-relaxed text-red-900">
          PROT: SSL_NEURAL_v4<br/>
          SYNC: ESTABLE<br/>
          ZONA: GLOBAL_CORE
        </div>
      </div>
    </div>
  );
};

const MetricBlock = ({ label, value, unit }: { label: string, value: number, unit: string }) => (
  <div className="space-y-4">
    <div className="flex justify-between items-end border-b border-red-900/20 pb-2">
      <span className="text-[9px] font-black text-red-900 orbitron tracking-[0.2em]">{label}</span>
      <span className="text-[14px] font-black text-red-500 orbitron">{value}{unit}</span>
    </div>
    <div className="relative h-[2px] w-full bg-red-950/20 overflow-hidden">
      <div 
        className="absolute top-0 left-0 h-full bg-red-600 transition-all duration-1000"
        style={{ width: `${value}%`, boxShadow: '0 0 10px rgba(255,0,0,0.5)' }}
      />
    </div>
  </div>
);

export default Sidebar;
