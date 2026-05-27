
import React, { useEffect, useRef, useState } from 'react';

interface BiometricHUDProps {
  active: boolean;
  backendUrl: string;
  onSuccess?: () => void;
  isGatekeeper?: boolean;
}

const BiometricHUD: React.FC<BiometricHUDProps> = ({ active, backendUrl, onSuccess, isGatekeeper }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [scanStatus, setScanStatus] = useState<'idle' | 'scanning' | 'detected' | 'not_found'>('idle');
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<{ name: string; confidence: number } | null>(null);
  const scanInterval = useRef<number | null>(null);
  const successCount = useRef(0);

  useEffect(() => {
    if (active) {
      setScanStatus('scanning');
      setProgress(5);
      navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      })
        .then(stream => {
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
            startScanning();
          }
        })
        .catch(err => {
          console.error("Fallo de cámara:", err);
          if (!isGatekeeper) window.dispatchEvent(new CustomEvent('close-scan'));
        });
    } else {
      stopScanning();
    }
    return () => stopScanning();
  }, [active]);

  const startScanning = () => {
    scanInterval.current = window.setInterval(async () => {
      if (!videoRef.current || !canvasRef.current) return;

      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
      const imageData = canvas.toDataURL('image/jpeg', 0.8);

      try {
        const response = await fetch(`${backendUrl}/process_frame`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image: imageData })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
          if (data.user === "Ningún Rostro") {
            setScanStatus('not_found');
            setProgress(p => Math.max(5, p - 2));
            successCount.current = 0;
          } else if (data.match) {
            setScanStatus('detected');
            setResult({ name: data.user, confidence: data.confidence });
            
            // Necesitamos 3 matches seguidos para confirmar identidad (seguridad Stark)
            successCount.current += 1;
            setProgress(p => Math.min(100, p + 30));

            if (successCount.current >= 3) {
              setProgress(100);
              stopScanning();
              setTimeout(() => {
                if (onSuccess) onSuccess();
                // Lanzar evento global para que HUDCenter muestre mensaje especial
                window.dispatchEvent(new CustomEvent('biometric-auth-success'));
              }, 1500);
            }
          } else {
            setScanStatus('scanning');
            setProgress(p => (p < 80 ? p + 5 : p));
            setResult({ name: "DESCONOCIDO", confidence: data.confidence });
            successCount.current = 0;
          }
        }
      } catch (e) {
        console.warn("Core Offline. Reintentando enlace...");
      }
    }, 600);
  };

  const stopScanning = () => {
    if (scanInterval.current) clearInterval(scanInterval.current);
    if (videoRef.current?.srcObject) {
      (videoRef.current.srcObject as MediaStream).getTracks().forEach(t => t.stop());
    }
  };


  // Cerrar automáticamente si se detecta al Creador
  useEffect(() => {
    if (scanStatus === 'detected' && result?.name?.toUpperCase() === 'CREADOR') {
      setTimeout(() => {
        window.dispatchEvent(new CustomEvent('close-scan', { detail: 'authenticated' }));
      }, 800); // Pequeño delay para mostrar el acceso concedido
    }
  }, [scanStatus, result]);

  if (!active) return null;

  return (
    <div className="absolute inset-0 flex items-center justify-center z-50 bg-black/90 backdrop-blur-2xl">
      <canvas ref={canvasRef} width="640" height="480" className="hidden" />
      
      <div className={`relative w-[720px] h-[500px] hud-border bg-black transition-all duration-700 ${
        scanStatus === 'detected' ? 'shadow-[0_0_100px_rgba(0,255,100,0.2)]' : 'shadow-[0_0_80px_rgba(255,0,0,0.2)]'
      }`}>
        
        <video ref={videoRef} autoPlay playsInline muted className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-1000 ${
          scanStatus === 'detected' ? 'opacity-80' : 'opacity-40 grayscale contrast-150'
        }`} />

        {/* HUD OVERLAY */}
        <div className="absolute inset-0 p-10 flex flex-col justify-between pointer-events-none">
          
          {/* Header */}
          <div className="flex justify-between items-start orbitron">
            <div className="space-y-1">
              <div className="text-[10px] text-red-500/50 tracking-[0.4em]">STARK_IND_BIOMETRICS</div>
              <div className={`text-xl font-black ${scanStatus === 'detected' ? 'text-green-500' : 'text-red-600'}`}>
                {scanStatus === 'detected' ? 'ACCESS_GRANTED' : 'SECURE_CHANNEL_ACTIVE'}
              </div>
            </div>
            <div className="text-right text-[9px] text-red-500/40">
              FRAME_SYNC: {progress}% <br/>
              BUFFER: 128MB_LOADED
            </div>
          </div>

          {/* Central Scan Area */}
          <div className="relative self-center w-72 h-80">
             <div className={`absolute inset-0 border-2 rounded-2xl transition-colors duration-500 ${
               scanStatus === 'detected' ? 'border-green-500' : 'border-red-500/30'
             }`}>
               {/* Scanning Line */}
               <div className={`absolute w-full h-1 shadow-[0_0_20px_currentColor] animate-[scan_2s_ease-in-out_infinite] ${
                 scanStatus === 'detected' ? 'bg-green-500 text-green-500' : 'bg-red-500 text-red-500'
               }`} />
             </div>
          </div>

          {/* Footer Info & Progress Bar */}
          <div className="space-y-4">
            <div className="orbitron">
              <div className="text-[10px] text-red-500/50 mb-1 tracking-widest uppercase">
                {scanStatus === 'detected' ? 'IDENTITY_CONFIRMED' : 'NEURAL_LINK_PROGRESS'}
              </div>
              
              {/* BARRA DE PROGRESO */}
              <div className="h-2 w-full bg-red-950/20 rounded-full border border-red-900/20 overflow-hidden relative">
                <div 
                  className={`h-full transition-all duration-500 shadow-[0_0_15px_currentColor] ${
                    scanStatus === 'detected' ? 'bg-green-500 text-green-500' : 'bg-red-600 text-red-600'
                  }`}
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            <div className="flex justify-between items-end orbitron">
              <div>
                <div className="text-[8px] text-red-500/40 mb-1">USER_CLASSIFICATION</div>
                <div className={`text-2xl font-black tracking-tighter italic ${scanStatus === 'detected' ? 'text-green-400' : 'text-red-600'}`}>
                   {scanStatus === 'detected' ? result?.name.toUpperCase() : 
                    scanStatus === 'not_found' ? 'WAITING_FOR_INPUT...' : 'ANALYZING...'}
                </div>
              </div>
              <div className="text-right">
                <div className="text-[8px] text-red-500/40 mb-1">PROBABILITY</div>
                <div className={`text-xl font-bold ${scanStatus === 'detected' ? 'text-green-400' : 'text-red-700'}`}>
                  {result ? `${(result.confidence * 100).toFixed(1)}%` : '00.0%'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {!isGatekeeper && (
        <button 
          onClick={() => window.dispatchEvent(new CustomEvent('close-scan'))}
          className="absolute bottom-10 px-8 py-3 border border-red-500/30 bg-red-950/20 text-red-500 orbitron text-[10px] tracking-[0.3em] hover:bg-red-600 hover:text-black transition-all"
        >
          TERMINATE_LINK
        </button>
      )}

      <style>{`
        @keyframes scan {
          0%, 100% { top: 0%; opacity: 0; }
          50% { top: 100%; opacity: 1; }
        }
      `}</style>
    </div>
  );
};

export default BiometricHUD;