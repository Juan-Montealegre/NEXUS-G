
import React, { useEffect, useRef } from 'react';
import { ConnectionStatus } from '../types';

interface HUDCenterProps {
  status: ConnectionStatus;
  isListening: boolean;
  onToggle: () => void;
  chatHistory: Array<{role: 'user' | 'jarvis', text: string, image?: string, isAction?: boolean}>;
  transcription: { user: string; jarvis: string };
}


const HUDCenter: React.FC<HUDCenterProps> = ({ status, isListening, chatHistory }) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
    }
  }, [chatHistory]);

  const lastResponse = chatHistory.filter(m => m.role === 'jarvis').pop()?.text || "PULSE PARA INICIAR NEXUS-G";

  return (
    <div className="flex flex-col items-center justify-center w-full h-full relative z-10 select-none">
      {/* NÚCLEO REACTOR MASIVO */}
      <div className={`relative w-[600px] h-[600px] flex items-center justify-center transition-all duration-1000 ${
        isListening ? 'scale-105' : 'scale-90 opacity-60 grayscale-[0.5]'
      }`}>
        {/* Anillos de Datos Externos */}
        <div className="absolute inset-0 border border-red-500/5 rounded-full rotate-cw"></div>
        <div className="absolute inset-12 border border-red-500/10 rounded-full border-dashed rotate-ccw"></div>
        <div className="absolute inset-28 border-[2px] border-red-600/20 rounded-full border-t-transparent border-b-transparent rotate-cw-fast"></div>
        {/* Halo de Plasma Reactivo */}
        <div className={`absolute inset-40 rounded-full blur-[100px] transition-all duration-1000 ${
          isListening ? 'bg-red-600/30 opacity-100' : 'bg-red-950/10 opacity-20'
        }`}></div>
        {/* LOGO CENTRAL NEXUS-G */}
        <div className={`relative w-56 h-56 rounded-full flex items-center justify-center transition-all duration-700 ${
          isListening 
            ? 'scale-110 drop-shadow-[0_0_50px_rgba(255,0,0,1)]' 
            : 'scale-100 opacity-40 drop-shadow-[0_0_15px_rgba(255,0,0,0.2)]'
        }`}>
          <img 
            src="logo.png" 
            alt="NEXUS-G Core" 
            className={`w-full h-full object-contain z-20 transition-all duration-500 ${isListening ? 'animate-reactor-pulse' : 'brightness-50'}`}
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = 'none';
            }}
          />
          {/* Brillo Interior */}
          <div className={`absolute inset-4 bg-red-600/15 rounded-full blur-3xl animate-pulse ${
            isListening ? 'opacity-100' : 'opacity-0'
          }`}></div>
        </div>
        {/* Marcadores de Brújula HUD */}
        {[0, 45, 90, 135, 180, 225, 270, 315].map(deg => (
          <div key={deg} className="absolute h-full flex flex-col items-center py-4 opacity-15" style={{ transform: `rotate(${deg}deg)` }}>
            <div className={`w-[2px] ${deg % 90 === 0 ? 'h-8 bg-red-500' : 'h-4 bg-red-900'}`}></div>
          </div>
        ))}
      </div>
      {/* ÁREA DE SALIDA DE COMUNICACIÓN */}
      <div className="mt-4 max-w-2xl w-full px-12 text-center h-32 flex flex-col items-center justify-center bg-gradient-to-b from-transparent via-red-500/[0.02] to-transparent py-4 rounded-3xl backdrop-blur-sm">
        <div className={`orbitron text-[10px] font-black uppercase tracking-[1.2em] mb-4 transition-all duration-700 ${
          isListening ? 'text-red-500 glow-red' : 'text-red-900/40'
        }`}>
          {isListening ? 'NEXUS_ENLACE_ACTIVO' : 'SISTEMA_STANDBY'}
        </div>
        <p className="orbitron text-lg md:text-xl text-red-500/90 leading-tight tracking-[0.05em] font-bold drop-shadow-[0_0_15px_rgba(255,0,0,0.4)] animate-in fade-in duration-1000 line-clamp-2">
          {lastResponse}
        </p>
      </div>
    </div>
  );
};

export default HUDCenter;