import cv2
import subprocess
import time
import os
import threading
import queue
import speech_recognition as sr
from security import JarvisVision 
from brain import JarvisBrain      
from ears import JarvisEars


# --- CONFIGURACIÓN DE RUTAS ---
# Verifique que esta ruta sea la correcta en su LENOVO
RUTA_OPERA = r"C:\Users\LENOVO\AppData\Local\Programs\Opera GX\opera.exe"

# --- PROTOCOLO DE APERTURA SELECTIVA ---
import asyncio

async def abrir_aplicacion(brain, comando):
    """Abre cualquier aplicación soportada usando la lógica de jarvis_backend.py"""
    from scripts import jarvis_backend
    comando = comando.lower().strip()
    # Extraer solo el nombre de la app si el comando es tipo "abre chrome" o "abrir spotify"
    palabras = comando.split()
    if len(palabras) >= 2 and (palabras[0] == "abre" or palabras[0] == "abrir"):
        app_name = " ".join(palabras[1:])
    else:
        app_name = comando
    # Llamar a la función moderna del backend usando await
    result = await jarvis_backend.execute_command({"action": "open_app", "payload": app_name})
    # Solo devolver el resultado, sin usar brain.speak (la voz la gestiona Gemini)
    return result

# --- PROTOCOLO DE CLAUSURA ---
def cerrar_laboratorio(brain):
    brain.speak("Cerrando procesos activos y despejando el escritorio.")
    # Lista de ejecutables exactos en Windows
    procesos = ["Code.exe", "opera.exe", "notepad.exe"]
    
    for p in procesos:
        # taskkill /f fuerza el cierre, /im filtra por nombre de imagen
        os.system(f"taskkill /f /im {p} >nul 2>&1")
    
    brain.speak("Sistemas cerrados correctamente.")

# --- MODO ESCUCHA ACTIVA ---
import threading

def modo_comandos(brain):
    # Evento y cola para sincronizar voz y escucha
    speak_event = threading.Event()
    audio_queue = queue.Queue()

    # Adaptar brain y ears para usar el evento
    brain.speak_event = speak_event
    ears = JarvisEars(speak_event)
    def speak_and_log(text):
        print("J.A.R.V.I.S.: " + text)
        audio_queue.put(text)

    def ejecutor():
        last_query = None
        while True:
            query = ears.listen()
            # Evitar procesar el mismo comando dos veces seguidas
            if query and query != last_query:
                last_query = query
                if "jarvis" in query:
                    if "abre" in query or "abrir" in query:
                        if len(query.split()) <= 2:
                            speak_and_log("¿Qué aplicación desea que despliegue, Señor?")
                        else:
                            abrir_aplicacion(brain, query)
                            speak_and_log("Aplicación desplegada correctamente.")
                    elif "cerrar" in query:
                        cerrar_laboratorio(brain)
                        speak_and_log("Protocolos de clausura ejecutados.")
                    else:
                        print("Consultando matriz de pensamiento...")
                        respuesta = brain.think(query)
                        speak_and_log(respuesta)
                    time.sleep(1.5)

    def audio_worker():
        while True:
            text = audio_queue.get()
            if text:
                speak_event.set()
                brain.speak(text)
                speak_event.clear()
            audio_queue.task_done()

    threading.Thread(target=ejecutor, daemon=True).start()
    threading.Thread(target=audio_worker, daemon=True).start()

# --- FLUJO PRINCIPAL CON HUD PROFESIONAL ---
def sistema_principal():
    vision = JarvisVision()
    brain = JarvisBrain() 
    cap = cv2.VideoCapture(0)
    confirmaciones = 0
    
    print("--- J.A.R.V.I.S. ONLINE (v3.11) ---")

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1) # Efecto espejo
        h, w, _ = frame.shape
        user = vision.identify_user(frame)
        
        # --- RENDERIZADO DEL HUD ---
        if user == "Creador":
            confirmaciones += 1
            color = (0, 255, 0) # Verde
            texto_estado = "IDENTIDAD: CONFIRMADA"
            subtexto = "DAVID - ACCESO NIVEL 5"
            
            # Dibujar esquinas de enfoque
            d = 40
            cv2.line(frame, (100, 100), (100+d, 100), color, 2)
            cv2.line(frame, (100, 100), (100, 100+d), color, 2)
            cv2.line(frame, (w-100, 100), (w-100-d, 100), color, 2)
            cv2.line(frame, (w-100, 100), (w-100, 100+d), color, 2)
            
            # Barra de carga de acceso
            progreso = int((confirmaciones / 15) * 400)
            cv2.rectangle(frame, (120, h-60), (120 + 400, h-40), (40, 40, 40), -1)
            cv2.rectangle(frame, (120, h-60), (120 + progreso, h-40), color, -1)
            cv2.putText(frame, f"SINCRO: {int((confirmaciones/15)*100)}%", (120, h-75), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
        else:
            confirmaciones = 0
            color = (0, 0, 255) # Rojo
            texto_estado = "ESTADO: BUSCANDO CREADOR"
            subtexto = "SISTEMA BLOQUEADO"
            
            # Línea de escaneo láser animada
            linea_y = int((time.time() % 1.5) * (h-200)) + 100
            cv2.line(frame, (100, linea_y), (w-100, linea_y), (0, 0, 255), 1)

        # Pintar textos en el HUD
        cv2.putText(frame, texto_estado, (50, 60), cv2.FONT_HERSHEY_TRIPLEX, 0.8, color, 2)
        cv2.putText(frame, subtexto, (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        cv2.imshow('J.A.R.V.I.S. - Control de Acceso', frame)

        # Lógica de entrada
        if confirmaciones >= 15:
            # Flash visual de éxito
            cv2.rectangle(frame, (0,0), (w,h), (0, 255, 0), 20)
            cv2.imshow('J.A.R.V.I.S. - Control de Acceso', frame)
            cv2.waitKey(400)
            
            cap.release()
            cv2.destroyAllWindows()
            
            # SALUDO INICIAL Y ENTRADA AL MODO COMANDOS
            brain.speak("Acceso concedido. Bienvenido, Señor David. Estoy a su disposición.")
            modo_comandos(brain)
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            break

if __name__ == "__main__":
    sistema_principal()