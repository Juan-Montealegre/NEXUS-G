import React from 'react';

interface DataPanelsProps {
  metrics: {
    disk: number;
    temp: number;
    uptime: string;
  };
  chatHistory: Array<{ role: string; text: string; timestamp: Date }> | undefined;
}

const DataPanels: React.FC<DataPanelsProps> = ({ metrics, chatHistory }) => {
  // Asegura que chatHistory siempre sea un array
  const safeHistory = Array.isArray(chatHistory) ? chatHistory : [];
  // Limitar valores para evitar glitches visuales
  const disk = Math.max(0, Math.min(100, metrics.disk ?? 0));
  const temp = Math.max(-20, Math.min(120, metrics.temp ?? 0)); // Rango seguro para temperatura

  // Obtenemos solo los últimos 6 eventos para el panel de registro
  const recentLogs = safeHistory.slice(-6).reverse();

  return (
    <div className="absolute inset-0 pointer-events-none z-0">
      
      {/* Marcadores de Esquina */}
      <div className="absolute top-12 left-12 w-24 h-24 border-t-2 border-l-2 border-red-500/10"></div>
      <div className="absolute bottom-12 right-12 w-24 h-24 border-b-2 border-r-2 border-red-500/10"></div>

      {/* PANEL DE HARDWARE */}
      <div className="absolute top-24 right-12 w-72 p-7 hud-glass rounded-3xl pointer-events-auto border-r-2 border-r-red-600">
        <div className="orbitron text-[10px] text-red-900 mb-6 tracking-[0.4em] font-black border-b border-red-900/10 pb-3 uppercase">Telemetría_Núcleo</div>
        
        <div className="space-y-8">
          <div className="flex justify-between items-center">
            <div className="space-y-1">
              <span className="text-[9px] orbitron text-red-950 font-black block uppercase">Temperatura</span>
              <div className="text-[8px] text-red-900/50 uppercase">Núcleo_Central</div>
            </div>
            <div className={`text-2xl font-black orbitron ${metrics.temp > 45 ? 'text-amber-500 animate-pulse' : 'text-red-500'}`}>
              {temp}°C
            </div>
          </div>
          
          <div className="space-y-3">
            <div className="flex justify-between text-[9px] orbitron text-red-950 font-black">
              <span>ALMACENAMIENTO</span>
              <span className="text-red-500">{disk}%</span>
            </div>
            <div className="h-2 w-full bg-red-950/20 rounded-full flex gap-1 p-0.5">
              {[...Array(5)].map((_, i) => (
                <div 
                  key={i} 
                  className={`h-full flex-1 rounded-sm transition-all duration-700 ${
                    disk > (i * 20) ? 'bg-red-600' : 'bg-red-900/10'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* REGISTRO DE CONSCIENCIA (DINÁMICO) */}
      <div className="absolute bottom-24 right-12 w-80 h-72 p-7 hud-glass rounded-3xl pointer-events-auto flex flex-col">
        <div className="orbitron text-[10px] text-red-900 mb-5 tracking-[0.3em] font-black border-b border-red-900/10 pb-3 uppercase">Registro_de_Consciencia</div>
        <div className="flex-1 overflow-y-auto space-y-4">
           {recentLogs.map((log, idx) => (
             <div key={idx} className={`flex gap-3 text-[9px] font-mono border-l pl-3 transition-opacity duration-500 ${
               idx === 0 ? 'text-red-500 border-red-500 animate-pulse' : 'text-red-900/60 border-red-900/20'
             }`}>
               <span className="opacity-40 whitespace-nowrap">
                 {log.timestamp instanceof Date
                   ? log.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
                   : new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
               </span>
               <span className="line-clamp-2 uppercase">
                 {log.role === 'jarvis' ? 'NEXUS' : 'USER'}: {log.text}
               </span>
             </div>
           ))}
           {recentLogs.length === 0 && (
             <div className="text-[9px] font-mono text-red-900/30 italic">ESPERANDO ACTIVIDAD...</div>
           )}
        </div>
      </div>

      {/* Elementos Decorativos */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-[0.02]">
        <div className="w-[85vw] h-[85vw] border-[0.5px] border-red-500 rounded-full animate-[spin_180s_linear_infinite]"></div>
      </div>

    </div>
  );
};

export default DataPanels;