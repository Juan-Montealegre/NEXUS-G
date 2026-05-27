import React, { useState, useEffect, useRef } from 'react';
import { GoogleGenAI, Modality, LiveServerMessage, Type, FunctionDeclaration } from '@google/genai';
import { ConnectionStatus, SystemMetrics } from './types';
import Sidebar from './components/Sidebar';
import HUDCenter from './components/HUDCenter';
import DataPanels from './components/DataPanels';
import BiometricHUD from './components/BiometricHUD';
// Eliminar imports de @tauri-apps/api y @tauri-apps/plugin-permission-api

// Funciones de codificación/decodificación requeridas por el protocolo
function encode(bytes: Uint8Array) {
  let binary = '';
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

function decode(base64: string) {
  const binaryString = atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes;
}

async function decodeAudioData(
  data: Uint8Array,
  ctx: AudioContext,
  sampleRate: number,
  numChannels: number,
): Promise<AudioBuffer> {
  const dataInt16 = new Int16Array(data.buffer);
  const frameCount = dataInt16.length / numChannels;
  const buffer = ctx.createBuffer(numChannels, frameCount, sampleRate);

  for (let channel = 0; channel < numChannels; channel++) {
    const channelData = buffer.getChannelData(channel);
    for (let i = 0; i < frameCount; i++) {
      channelData[i] = dataInt16[i * numChannels + channel] / 32768.0;
    }
  }
  return buffer;
}

// Tool para navegación web por alias
const navigateWebTool = {
  name: 'navigate_web',
  parameters: {
    type: Type.OBJECT,
    description: 'Navega a una URL o alias definido en el sistema (por ejemplo, "youtube", "github", "notion", etc).',
    properties: {
      target: {
        type: Type.STRING,
        description: 'Alias o nombre del sitio a abrir (ej: "youtube", "notion", "github", etc).',
      },
    },
    required: ['target'],
  },
};

const controlSystemTool: FunctionDeclaration = {
  name: 'control_local_system',
  parameters: {
    type: Type.OBJECT,
    description: 'Controla el hardware y software de la computadora local (apps, cámara, archivos, WhatsApp, Spotify, VSCode, Opera, archivos).',
    properties: {
      action: {
        type: Type.STRING,
        description: `La acción a ejecutar. Opciones:
  - open_app: Abrir una aplicación
  - close_app: Cerrar una aplicación
  - escribir_en_app: Escribir texto en la app activa
  - buscar_contacto_whatsapp: Buscar contacto en WhatsApp
  - escribir_en_whatsapp: Enviar mensaje a contacto de WhatsApp
  - buscar_en_opera: Buscar en Opera GX
  - buscar_archivo: Buscar archivo por nombre
  - crear_archivo: Crear archivo con contenido
  - programar_en_vscode: Crear archivo y abrir en VSCode
  - poner_musica_spotify: Controlar Spotify (play, pausa, siguiente, anterior, volumen)
  - facial_recognition: Autenticación biométrica
  - check_security: Revisar seguridad del sistema`
      },
      payload: {
        type: Type.STRING,
        description: `Parámetro adicional según la acción. Ejemplos:
  - open_app: "chrome"
  - close_app: "chrome"
  - escribir_en_app: "Texto a escribir"
  - buscar_contacto_whatsapp: "Nombre del contacto"
  - escribir_en_whatsapp: "Nombre|Mensaje"
  - buscar_en_opera: "término de búsqueda"
  - buscar_archivo: "nombre.ext|carpeta_opcional"
  - crear_archivo: "ruta.ext|contenido"
  - programar_en_vscode: "ruta.ext|código"
  - poner_musica_spotify: "reproduce", "pausa", "siguiente", "anterior", "sube volumen", "baja volumen"`
      },
    },
    required: ['action'],
  },
};


const App: React.FC = () => {
  const [status, setStatus] = useState<ConnectionStatus>(ConnectionStatus.DISCONNECTED);
  const [isListening, setIsListening] = useState(false);
  const [backendLinked, setBackendLinked] = useState(false);
  const [transcription, setTranscription] = useState({ user: '', jarvis: '' });
  const [metrics, setMetrics] = useState<any>({ cpu: 0, ram: 0, disk: 45, uptime: 'INICIANDO', battery: 100, temp: 42 });
  const [chatHistory, setChatHistory] = useState<any[]>([
    { role: 'jarvis', text: "SISTEMAS NEXUS-G ACTIVOS. PROTOCOLO NEURAL EN LÍNEA." }
  ]);
  const [authenticated, setAuthenticated] = useState(false);
  const [micError, setMicError] = useState<string | null>(null);
  const [criticalAlert, setCriticalAlert] = useState<string | null>(null);

  const audioContextRef = useRef<AudioContext | null>(null);
  const nextStartTimeRef = useRef(0);
  const sourcesRef = useRef<Set<AudioBufferSourceNode>>(new Set());
  const BACKEND_URL = 'http://localhost:8000';


  useEffect(() => {
    // Actualización de batería real del sistema
    const updateBattery = async () => {
      try {
        const battery: any = await (navigator as any).getBattery();
        const setBat = () => setMetrics((prev: typeof metrics) => ({
          ...prev,
          battery: Math.round(battery.level * 100)
        }));
        battery.addEventListener('levelchange', setBat);
        setBat();
      } catch (e) { console.log("Hardware de batería no detectado"); }
    };

    // Petición de telemetría al backend
    const fetchSystemMetrics = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/metrics`);
        if (res.ok) {
          const data = await res.json();
          setMetrics((prev: typeof metrics) => ({
            ...prev,
            cpu: data.cpu,
            ram: data.ram,
            disk: data.disk,
            temp: 35 + Math.floor(data.cpu / 2),
            uptime: data.uptime ?? prev.uptime
          }));
          setBackendLinked(true);
          // --- Lógica de alerta crítica ---
          let alertMsg = null;
          if (data.cpu > 90) alertMsg = `ALERTA: Carga de procesador crítica (${data.cpu}%)`;
          else if (data.ram > 90) alertMsg = `ALERTA: Memoria dinámica crítica (${data.ram}%)`;
          else if (data.battery !== undefined && data.battery < 10) alertMsg = `ALERTA: Nivel de energía bajo (${data.battery}%)`;
          // else if (data.neural_interface === false) alertMsg = `ALERTA: Enlace de seguridad desconectado`;
          setCriticalAlert(alertMsg);
        }
      } catch (e) {
        setBackendLinked(false);
      }
    };

    const itv = setInterval(fetchSystemMetrics, 1000); // Actualiza cada segundo
    updateBattery();
    return () => {
      clearInterval(itv);
    };
  }, []);

  // Función para desbloquear tras autenticación biométrica
  const handleAuthSuccess = () => {
    setAuthenticated(true);
    setTranscription({ user: '', jarvis: 'Bienvenido, acceso concedido.' });
  };

  // --- Llamada directa a backend, sin biometría para acciones ---
  const callPython = async (action: string, payload?: string) => {
    if (action === 'facial_recognition') {
      setTranscription((p: typeof transcription) => ({ ...p, jarvis: "Iniciando escaneo biométrico. Por favor, mire a la cámara." }));
    }
    try {
      const res = await fetch(`${BACKEND_URL}/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload !== undefined ? { action, payload } : { action })
      });
      return await res.json();
    } catch {
      return { error: "Link offline" };
    }
  };

  // --- Cambio 2: Activación por clic, no auto ---
  const handleInitialize = async () => {
    if (status === ConnectionStatus.CONNECTED || status === ConnectionStatus.CONNECTING) return;
    await startVoiceSession();
  };

  const startVoiceSession = async () => {
    if (status === ConnectionStatus.CONNECTED) {
      window.location.reload(); // Forma rápida de limpiar buffers
      return;
    }
    try {
      setMicError(null);
      setStatus(ConnectionStatus.CONNECTING);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      const outCtx = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 24000 });
      const inCtx = new AudioContext({ sampleRate: 16000 });
      audioContextRef.current = outCtx;

      const ai = new GoogleGenAI({ apiKey: import.meta.env.VITE_API_KEY });
      // --- Refuerzo de instrucciones para uso correcto de herramientas ---
      const sessionPromise = ai.live.connect({
        model: 'gemini-2.5-flash-native-audio-preview-12-2025',
        config: {
          responseModalities: [Modality.AUDIO],
          speechConfig: { 
            voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Puck' } }
          },
          systemInstruction: `

Eres NEXUS-G, el asistente de inteligencia artificial personal del señor David. Tu comunicación es profesional, precisa y eficiente. Dirígete siempre como "señor David" con respeto y cortesía.

Responde de forma breve y clara, sin información innecesaria. Solo menciona la hora, fecha o ubicación de Colombia si el señor David lo solicita explícitamente. Siempre que te pregunten por la hora o fecha, responde usando la zona horaria de Bogotá, Colombia (GMT-5) y la fecha actual.

No repitas datos de contexto salvo que se te pregunte. Prioriza la seguridad, la eficiencia y la experiencia premium en cada acción.

IMPORTANTE: Cuando el señor David solicite abrir una aplicación instalada en el sistema operativo (como WhatsApp, Spotify, Visual Studio Code, Opera, etc.), utiliza SIEMPRE la herramienta control_local_system con la acción 'open_app'.

Cuando el señor David solicite abrir un sitio web, servicio online, o cualquier URL (como YouTube, Aulas Virtuales, GPT, Notion, etc.), utiliza SIEMPRE la herramienta navigate_web, pasando el alias o nombre definido en el sistema.

No mezcles herramientas: 'control_local_system' es solo para apps locales, 'navigate_web' es solo para URLs/alias web.

Ejemplos:
- "Abre YouTube": usa navigate_web con target "youtube"
- "Abre WhatsApp": usa control_local_system con action "open_app" y payload "whatsapp"
- "Abre aulas virtuales": usa navigate_web con target "aulasvirtuales"
- "Abre Visual Studio Code": usa control_local_system con action "open_app" y payload "vscode"

`,
          tools: [{ functionDeclarations: [controlSystemTool, navigateWebTool] }],
          inputAudioTranscription: {},
          outputAudioTranscription: {}
        },
        callbacks: {
          onopen: () => {
            setStatus(ConnectionStatus.CONNECTED);
            setIsListening(true);
            const source = inCtx.createMediaStreamSource(stream);
            const scriptProcessor = inCtx.createScriptProcessor(4096, 1, 1);
            scriptProcessor.onaudioprocess = (e) => {
              const inputData = e.inputBuffer.getChannelData(0);
              const int16 = new Int16Array(inputData.length);
              for (let i = 0; i < inputData.length; i++) int16[i] = inputData[i] * 32768;
              const pcmBlob = {
                data: encode(new Uint8Array(int16.buffer)),
                mimeType: 'audio/pcm;rate=16000',
              };
              sessionPromise.then(session => {
                session.sendRealtimeInput({ media: pcmBlob });
              });
            };
            source.connect(scriptProcessor);
            scriptProcessor.connect(inCtx.destination);
          },
          onmessage: async function (msg: LiveServerMessage) {
            // Manejo de Herramientas
            if (msg.toolCall && msg.toolCall.functionCalls) {
              for (const fc of msg.toolCall.functionCalls) {
                if (fc.name === 'navigate_web') {
                  const result = await callPython('navigate_to', fc.args?.target as string);
                  sessionPromise.then(s => s.sendToolResponse({
                    functionResponses: [{ id: fc.id, name: fc.name, response: { result } }]
                  }));
                } else {
                  const result = await callPython(fc.args?.action as string, fc.args?.payload as string);
                  sessionPromise.then(s => s.sendToolResponse({
                    functionResponses: [{ id: fc.id, name: fc.name, response: { result } }]
                  }));
                }
              }
            }

            // Transcripciones
            if (msg.serverContent?.inputTranscription) setTranscription((p: typeof transcription) => ({ ...p, user: msg.serverContent!.inputTranscription!.text ?? '' }));
            if (msg.serverContent?.outputTranscription) setTranscription((p: typeof transcription) => ({ ...p, jarvis: p.jarvis + (msg.serverContent!.outputTranscription!.text ?? '') }));
            if (msg.serverContent?.turnComplete) setTranscription((p: typeof transcription) => ({ ...p, jarvis: '' }));

            // Audio de Salida
            const audioBase64 = msg.serverContent?.modelTurn?.parts?.[0]?.inlineData?.data;
            if (audioBase64) {
              const buffer = await decodeAudioData(decode(audioBase64), outCtx, 24000, 1);
              const source = outCtx.createBufferSource();
              source.buffer = buffer;
              source.connect(outCtx.destination);
              nextStartTimeRef.current = Math.max(nextStartTimeRef.current, outCtx.currentTime);
              source.start(nextStartTimeRef.current);
              nextStartTimeRef.current += buffer.duration;
              sourcesRef.current.add(source);
              source.onended = () => sourcesRef.current.delete(source);
            }

            if (msg.serverContent?.interrupted) {
              sourcesRef.current.forEach((s: AudioBufferSourceNode) => { try { s.stop(); } catch {} });
              sourcesRef.current.clear();
              nextStartTimeRef.current = 0;
            }
          },
          onclose: () => setStatus(ConnectionStatus.DISCONNECTED),
          onerror: (e) => console.error("Neural link error:", e)
        }
      });

    } catch (err: any) {
      console.error("Mic error:", err);
      setStatus(ConnectionStatus.DISCONNECTED);
      if (err && (err.name === 'NotAllowedError' || err.message?.includes('denied'))) {
        setMicError('Permiso de micrófono denegado. Ve a Configuración > Privacidad > Micrófono y habilita el acceso para aplicaciones de escritorio. Luego reinicia NEXUS-G.');
      }
    }
  };


  // Mostrar BiometricHUD si no está autenticado
  if (!authenticated) {
    return (
      <div className="flex h-screen w-full relative bg-black overflow-hidden select-none">
        <BiometricHUD 
          active={true}
          backendUrl={BACKEND_URL}
          onSuccess={handleAuthSuccess}
          isGatekeeper={true}
        />
        <div className="absolute top-0 w-full h-8 bg-gradient-to-b from-red-950/40 to-transparent z-40 flex items-center px-6 justify-between border-b border-red-500/10 pointer-events-none">
          <div className="flex items-center gap-3">
            <div className={`w-1.5 h-1.5 rounded-full animate-pulse shadow-[0_0_5px_#f00] ${backendLinked ? 'bg-red-500' : 'bg-red-900'}`}></div>
            <div className="text-[9px] font-bold text-red-500/60 tracking-[0.3em] orbitron">MARK_85_OS_V2.5</div>
          </div>
          <div className="text-[8px] font-bold text-red-500/40 uppercase tracking-widest">
            {'PROTOCOL_BIOMETRIC_ENGAGED'}
          </div>
        </div>
      </div>
    );
  }

  // Si está autenticado, mostrar la app normal
  // --- Cambio 2: Activación por clic, no auto ---
  return (
    <div className="flex h-screen w-full bg-[#020202] overflow-hidden font-['JetBrains_Mono'] relative">
      <Sidebar status={status} metrics={metrics} />
      <main className="flex-1 flex flex-col items-center justify-center relative z-10">
        {/* Indicador de Estado Superior */}
        <div className={`absolute top-12 right-16 flex items-center gap-6 pointer-events-none`}>
          <div className="text-right">
            <div className="text-[9px] orbitron text-red-950 tracking-[0.6em] uppercase font-black">Núcleo_Neural</div>
            <div className={`text-[12px] font-bold orbitron tracking-wider ${status === ConnectionStatus.CONNECTED ? 'text-red-500' : 'text-red-900 animate-pulse'}`}>
              {status === ConnectionStatus.CONNECTED ? 'ENLACE_ESTABLE' : 'BUSCANDO_RED'}
            </div>
          </div>
          <div className={`w-4 h-4 rounded-full ${status === ConnectionStatus.CONNECTED ? 'bg-red-500 shadow-[0_0_15px_#ff0000]' : 'bg-red-950'}`}></div>
        </div>
        {/* --- Activación por clic en el núcleo --- */}
        <div className="relative group cursor-pointer" onClick={handleInitialize}>
          <HUDCenter 
            status={status} 
            isListening={isListening} 
            chatHistory={chatHistory}
            transcription={transcription}
            onToggle={startVoiceSession}
          />
        </div>
        {/* Paneles de métricas y registro de consciencia */}
        <DataPanels metrics={metrics} chatHistory={chatHistory} />
        {/* Alerta crítica en tiempo real */}
        {criticalAlert && (
          <div className="absolute top-24 left-1/2 -translate-x-1/2 bg-red-800/90 text-red-100 px-6 py-2 rounded-lg shadow-lg border border-red-500/40 text-xs font-bold z-50 animate-pulse">
            {criticalAlert}
          </div>
        )}
        {/* Mensaje de error de micrófono y botón para pedir permiso */}
        {micError && (
          <div className="absolute bottom-24 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 z-50">
            <div className="bg-yellow-900/90 text-yellow-200 px-6 py-2 rounded-lg shadow-lg border border-yellow-500/40 text-xs font-bold animate-pulse">
              {micError}
            </div>
            <button
              className="mt-2 px-4 py-1 bg-yellow-700 hover:bg-yellow-600 text-yellow-100 rounded shadow border border-yellow-400 text-xs font-bold transition"
              onClick={async () => {
                try {
                  await navigator.mediaDevices.getUserMedia({ audio: true });
                  setMicError(null);
                } catch (err: any) {
                  setMicError('Permiso de micrófono denegado. Ve a Configuración > Privacidad > Micrófono y habilita el acceso para aplicaciones de escritorio. Luego reinicia NEXUS-G.');
                }
              }}
            >
              Solicitar permiso de micrófono
            </button>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;

declare global {
  interface ImportMeta {
    env: {
      VITE_API_KEY: string;
      [key: string]: any;
    };
  }
}
