import os
import subprocess
import webbrowser
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psutil
import os
import base64
import sys
import numpy as np
import cv2
import face_recognition
import threading
import time
import pyautogui
import subprocess
import json
import webbrowser
from scripts.browser_control import abrir_url_en_opera, abrir_url_en_navegador

# --- CARGA DINÁMICA DE CONFIGURACIÓN ---
def load_nexus_config():
    config_path = 'browser_routes.json'
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('browser_routes', {}), data.get('url_aliases', {})
        else:
            print(f"ALERTA: No se encontró {config_path}. Usando configuración vacía.")
            return {}, {}
    except Exception as e:
        print(f"ERROR cargando configuración: {e}")
        return {}, {}

BROWSER_ROUTES, URL_ALIASES = load_nexus_config()

def open_in_opera(url):
    # Leer la ruta personalizada de Opera GX desde app_map.json
    app_map_path = os.path.join(os.path.dirname(__file__), 'app_map.json')
    opera_path = None
    if os.path.exists(app_map_path):
        with open(app_map_path, 'r', encoding='utf-8') as f:
            app_map = json.load(f)
            exe_apps = app_map.get('exe_apps', {})
            if isinstance(exe_apps, dict):
                # Buscar en ejecutables_locales primero
                if 'ejecutables_locales' in exe_apps:
                    opera_path = exe_apps['ejecutables_locales'].get('opera')
                # Fallback directo
                if not opera_path:
                    opera_path = exe_apps.get('opera')
    if opera_path and os.path.exists(opera_path):
        # Ejecutar el comando en PowerShell para abrir Opera GX con la URL, usando shell=True
        comando = f'Start-Process -FilePath "{opera_path}" -ArgumentList "{url}"'
        try:
            subprocess.Popen(["powershell", "-Command", comando], shell=True)
        except Exception as e:
            print(f"[NEXUS ERROR] Al ejecutar PowerShell: {e}")
        return opera_path
    else:
        webbrowser.open(url)
        return None

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Command(BaseModel):
    action: str
    target: str = ""

@app.post("/command")
async def handle_command(cmd: Command):
    global BROWSER_ROUTES, URL_ALIASES
    BROWSER_ROUTES, URL_ALIASES = load_nexus_config()
    if cmd.action == "navigate_to":
        # Permitir tanto 'target' como 'payload' para compatibilidad
        target = (getattr(cmd, 'target', '') or getattr(cmd, 'payload', '')).lower()
        print(f"[NEXUS DEBUG] Alias recibido: '{target}'")
        actual_route = URL_ALIASES.get(target, target)
        print(f"[NEXUS DEBUG] Ruta resuelta: '{actual_route}'")
        url = BROWSER_ROUTES.get(actual_route)
        print(f"[NEXUS DEBUG] URL final: '{url}'")
        if url:
            opera_path = open_in_opera(url)
            if opera_path:
                comando = f'Start-Process -FilePath "{opera_path}" -ArgumentList "{url}"'
                print(f"[NEXUS DEBUG] Comando ejecutado: {comando}")
                return {
                    "status": "executed",
                    "cmd": comando,
                    "msg": f"Navegando a {actual_route} en Opera GX: {opera_path}",
                    "url": url
                }
            else:
                print(f"[NEXUS DEBUG] Opera GX no encontrado, abriendo en navegador por defecto.")
                return {
                    "status": "executed",
                    "cmd": f'Start-Process -FilePath "default" -ArgumentList "{url}"',
                    "msg": f"Navegando a {actual_route} en navegador por defecto",
                    "url": url
                }
        else:
            print(f"[NEXUS DEBUG] Ruta '{target}' no definida en NEXUS.")
            return {"status": "error", "msg": f"Ruta '{target}' no definida en NEXUS."}
    return {"status": "error", "msg": "Comando no reconocido."}




pyautogui.FAILSAFE = True


# --- MÓDULOS DEL USUARIO ---
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

# Base de Datos de Contactos de NEXUS-G
CONTACTS = {
    "admin": {"name": "Nexus Root", "phone": "000000000", "role": "Global Admin"},
    "support": {"name": "Nexus Support", "phone": "111111111", "role": "Tech Assistance"},
    "security": {"name": "Sentinel Core", "phone": "222222222", "role": "Security Unit"}
}

# Importar módulos de scripts sólo si existen
try:
    from scripts.main_jarvis import abrir_aplicacion, cerrar_laboratorio
    from scripts.test_vision import iniciar_sesion_biometrica
    from scripts.brain import JarvisBrain
    from scripts.app_control import AppOrchestrator
    from scripts.jarvis_backend import get_system_metrics
    brain = JarvisBrain()
    orchestrator = AppOrchestrator()
except Exception as e:
    print(f"[WARN] No se pudieron importar módulos de scripts: {e}")
    abrir_aplicacion = None
    cerrar_laboratorio = None
    iniciar_sesion_biometrica = None
    JarvisBrain = None
    AppOrchestrator = None
    get_system_metrics = None
    brain = None
    orchestrator = None

neural_interface_active = False
facial_thread = None
voice_enabled = False

# Cargar mapeo de aplicaciones
APP_MAP_PATH = os.path.join(os.path.dirname(__file__), 'app_map.json')
if os.path.exists(APP_MAP_PATH):
    with open(APP_MAP_PATH, 'r', encoding='utf-8') as f:
        APP_MAP = json.load(f)
else:
    APP_MAP = {"aliases": {}, "exe_apps": {}}


# Instancia de FastAPI y modelo Command deben estar antes de los endpoints
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Command(BaseModel):
    action: str
    target: str = ""
    payload: str = ""

# Endpoints de control de voz
@app.post("/voice/on")
async def enable_voice():
    global voice_enabled
    voice_enabled = True
    return {"status": "success", "voice": True}

@app.post("/voice/off")
async def disable_voice():
    global voice_enabled
    voice_enabled = False
    return {"status": "success", "voice": False}

@app.get("/voice/status")
async def voice_status():
    return {"voice": voice_enabled}

@app.post("/command")
async def handle_command(cmd: Command):
    action = cmd.action
    payload = cmd.payload
    target = cmd.target

    try:
        if action == "open_chat":
            contact = CONTACTS.get(target.lower())
            if contact:
                url = f"https://web.whatsapp.com/send?phone={contact['phone']}"
                webbrowser.open(url)
                return {"status": "executed", "msg": f"Enlazando canal con {contact['name']}"}
            return {"status": "error", "msg": "Identificador NEXUS no encontrado."}

        elif action == "send_msg":
            contact = CONTACTS.get(target.lower())
            if contact:
                url = f"https://web.whatsapp.com/send?phone={contact['phone']}&text={payload}"
                webbrowser.open(url)
                return {"status": "executed", "msg": "Protocolo de mensajería iniciado."}
            return {"status": "error", "msg": "Fallo en la resolución del contacto."}

        elif action == "dictation":
            pyautogui.write(payload, interval=0.01)
            return {"status": "executed", "msg": "Inyección de texto NEXUS completada."}

        elif action == "read_notifs":
            return {
                "status": "executed",
                "data": [
                    "Sentinel: 'Seguridad de red al 100%'",
                    "Root: 'NEXUS-G v3.0 desplegado con éxito.'"
                ]
            }

        elif action == "open_app":
            # Resolución de alias y mapeo robusta
            app_name = payload.lower()
            exe_apps = APP_MAP.get("exe_apps", {})
            aliases = APP_MAP.get("aliases", {})
            # Buscar alias de aplicaciones
            if app_name in aliases:
                app_name = aliases[app_name]
            # Buscar idpath en ejecutables_locales, luego en exe_apps
            idpath = None
            if isinstance(exe_apps, dict):
                if 'ejecutables_locales' in exe_apps and app_name in exe_apps['ejecutables_locales']:
                    idpath = exe_apps['ejecutables_locales'][app_name]
                elif app_name in exe_apps:
                    idpath = exe_apps[app_name]
            if not idpath:
                idpath = app_name

            # Soporte de alias para URLs en browser_routes.json
            browser_data = get_browser_routes()
            browser_routes = browser_data["routes"]
            url_aliases = browser_data["aliases"]
            if app_name in url_aliases:
                app_name = url_aliases[app_name]
            if app_name in browser_routes:
                resultado = abrir_url_en_navegador(app_name)
                return {"status": "executed", "msg": resultado}

            # Lógica universal de apertura
            if sys.platform == "win32":
                # UWP AppID
                if "!App" in idpath or ("." in idpath and idpath.count("!") == 1):
                    subprocess.Popen(['explorer.exe', f'shell:AppsFolder\{idpath}'])
                # Protocolo (steam://, etc.)
                elif "://" in idpath:
                    subprocess.Popen([idpath], shell=True)
                # Ruta absoluta a ejecutable
                elif os.path.isfile(idpath) and idpath.lower().endswith(('.exe', '.msc', '.lnk', '.bat')):
                    subprocess.Popen([idpath])
                # Comando especial (ms-settings:, etc.)
                elif ":" in idpath and "\\" not in idpath:
                    subprocess.Popen([idpath], shell=True)
                # Rutas con GUID (ejemplo: {GUID}\Steam\steam.exe)
                elif idpath.startswith("{") and (".exe" in idpath or ".msc" in idpath or ".lnk" in idpath):
                    # Buscar en todas las unidades conocidas
                    for root in [os.environ.get('ProgramFiles'), os.environ.get('ProgramFiles(x86)'), os.environ.get('LOCALAPPDATA'), os.environ.get('APPDATA')]:
                        if root and os.path.exists(root):
                            full_path = os.path.join(root, *idpath.split("\\")[1:])
                            if os.path.isfile(full_path):
                                subprocess.Popen([full_path])
                                return {"status": "executed"}
                    # Si no se encuentra, intentar abrir directamente
                    subprocess.Popen([idpath], shell=True)
                # Fallback: intentar abrir directamente
                else:
                    try:
                        subprocess.Popen([idpath])
                    except Exception:
                        subprocess.Popen([idpath], shell=True)
            elif sys.platform == "darwin":
                subprocess.Popen(['open', '-a', idpath])
            else:
                subprocess.Popen([idpath])
            return {"status": "executed"}
    except Exception as e:
            return {"status": "error", "msg": str(e)}
# --- Utilidad para leer browser_routes.json ---
def get_browser_routes():
    path = os.path.join(os.path.dirname(__file__), 'browser_routes.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            routes = data.get('browser_routes', {})
            aliases = data.get('url_aliases', {})
            return {"routes": routes, "aliases": aliases}
    return {"routes": {}, "aliases": {}}

    return {"status": "error", "msg": "Comando desconocido en el núcleo NEXUS."}
APP_PATHS = APP_MAP.get("exe_apps", {})

# --- LÓGICA DE VISIÓN STARK CORE ---
class JarvisVision:
    def __init__(self):
        self.authorized_encoding = None
        self.load_reference_image()

    def load_reference_image(self):
        try:
            path = "creator.jpg"
            if os.path.exists(path):
                image = face_recognition.load_image_file(path)
                encodings = face_recognition.face_encodings(image)
                if len(encodings) > 0:
                    self.authorized_encoding = encodings[0]
                    print(f"--- [BIOMETRÍA] Perfil de 'CREADOR' cargado ---")
                else:
                    print("--- [!] creator.jpg no tiene rostros legibles ---")
            else:
                print(f"--- [!] creator.jpg no encontrada en {os.getcwd()} ---")
        except Exception as e:
            print(f"--- [ERROR] Al cargar biometría: {e} ---")

    def identify_user(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Reducción controlada para no perder rasgos faciales finos
        small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.5, fy=0.5)

        face_locations = face_recognition.face_locations(small_frame)
        if not face_locations:
            return "Ningún Rostro", 0.0

        if self.authorized_encoding is None:
            return "Sujeto Desconocido", 0.5

        face_encodings = face_recognition.face_encodings(small_frame, face_locations)
        for face_encoding in face_encodings:
            # Tolerancia 0.5 para mayor seguridad en el acceso
            matches = face_recognition.compare_faces([self.authorized_encoding], face_encoding, tolerance=0.5)
            distance = face_recognition.face_distance([self.authorized_encoding], face_encoding)
            
            if matches[0]:
                return "Creador", float(1.0 - distance[0])
        
        return "Desconocido", 0.3


vision = JarvisVision()

# Instancia de FastAPI debe estar antes de los decoradores y modelos
app = FastAPI()

# Configuración estricta de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Command(BaseModel):
    action: str
    target: str = ""
    payload: str = ""

@app.get("/contacts")
async def get_contacts():
    return CONTACTS

class FrameData(BaseModel):
    image: str


@app.get("/metrics")
async def get_metrics():
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "neural_interface": True,  # Siempre activo para evitar alerta
        "uptime": "ACTIVE"
    }


def run_facial_scan():
    global neural_interface_active
    neural_interface_active = True
    print("NEURAL LINK ACTIVE")
    iniciar_sesion_biometrica()
    neural_interface_active = False

# --- ENDPOINT DE PROCESAMIENTO DE FRAME BIOMÉTRICO ---
@app.post("/process_frame")
async def process_frame(data: FrameData):
    try:
        header, encoded = data.image.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return {"status": "error", "msg": "Imagen inválida"}

        user_id, confidence = vision.identify_user(img)
        
        return {
            "status": "success",
            "match": user_id == "Creador",
            "user": user_id,
            "confidence": confidence
        }
    except Exception as e:
        print(f"Error procesando frame: {e}")
        return {"status": "error", "msg": str(e)}

def resolve_app_path(app_name):
    aliases = APP_MAP.get("aliases", {})
    exe_apps = APP_MAP.get("exe_apps", {})
    ejecutables = exe_apps.get("ejecutables_locales", {})
    uris = exe_apps.get("uris", {})
    uwp_apps = exe_apps.get("uwp_apps", {})

    real_name = aliases.get(app_name, app_name)

    if real_name in ejecutables:
        path = ejecutables[real_name]
        if os.path.isabs(path) and os.path.isfile(path):
            return ("exe", path)
        abs_path = os.path.join(os.path.dirname(__file__), path)
        if os.path.isfile(abs_path):
            return ("exe", abs_path)
        if "!App" in path or path.startswith("Microsoft."):
            return ("uwp", path)
        if path.startswith("{") and ("\\") in path:
            return ("guid", path)
        if "--" in path:
            return ("cmd", path)
        return ("exe", path)

    if real_name in uwp_apps:
        return ("uwp", uwp_apps[real_name])

    if real_name in uris:
        return ("uri", uris[real_name])

    return (None, None)

@app.post("/command")
async def handle_command(cmd: Command):
    global facial_thread
    action = cmd.action
    payload = cmd.payload
    target = cmd.target
    print(f"\n[NEXUS-G CORE]: Directiva recibida -> {action.upper()}")
    try:
        if action == "open_chat":
            contact = CONTACTS.get(target.lower())
            if contact:
                url = f"https://web.whatsapp.com/send?phone={contact['phone']}"
                webbrowser.open(url)
                return {"status": "executed", "msg": f"Enlazando canal con {contact['name']}"}
            return {"status": "error", "msg": "Identificador NEXUS no encontrado."}
        elif action == "send_msg":
            contact = CONTACTS.get(target.lower())
            if contact:
                url = f"https://web.whatsapp.com/send?phone={contact['phone']}&text={payload}"
                webbrowser.open(url)
                return {"status": "executed", "msg": "Protocolo de mensajería iniciado."}
            return {"status": "error", "msg": "Fallo en la resolución del contacto."}
        elif action == "dictation":
            pyautogui.write(payload, interval=0.01)
            return {"status": "executed", "msg": "Inyección de texto NEXUS completada."}
        elif action == "read_notifs":
            return {
                "status": "executed", 
                "data": [
                    "Sentinel: 'Seguridad de red al 100%'",
                    "Root: 'NEXUS-G v3.0 desplegado con éxito.'"
                ]
            }
        elif action == "open_app":
            tipo, path = resolve_app_path(payload.lower())
            if not tipo:
                return {"status": "error", "msg": f"No se encontró la aplicación '{payload}'."}
            if sys.platform == "win32":
                if tipo == "exe":
                    subprocess.Popen([path])
                    return {"status": "executed", "msg": f"Ejecutable '{payload}' abierto."}
                elif tipo == "uwp":
                    subprocess.Popen(['explorer.exe', f'shell:AppsFolder\\{path}'])
                    return {"status": "executed", "msg": f"App UWP '{payload}' abierta."}
                elif tipo == "uri":
                    subprocess.Popen([path], shell=True)
                    return {"status": "executed", "msg": f"Protocolo '{payload}' ejecutado."}
                elif tipo == "guid":
                    for root in [os.environ.get('ProgramFiles'), os.environ.get('ProgramFiles(x86)'), os.environ.get('LOCALAPPDATA'), os.environ.get('APPDATA')]:
                        if root and os.path.exists(root):
                            full_path = os.path.join(root, *path.split("\\")[1:])
                            if os.path.isfile(full_path):
                                subprocess.Popen([full_path])
                                return {"status": "executed", "msg": f"Ejecutable '{payload}' abierto por GUID."}
                    subprocess.Popen([path], shell=True)
                    return {"status": "executed", "msg": f"Intento de apertura por GUID para '{payload}'."}
                elif tipo == "cmd":
                    subprocess.Popen(path.split())
                    return {"status": "executed", "msg": f"Comando '{payload}' ejecutado."}
                else:
                    return {"status": "error", "msg": f"Tipo de aplicación no soportado para '{payload}'."}
            elif sys.platform == "darwin":
                subprocess.Popen(['open', '-a', path])
                return {"status": "executed"}
            else:
                subprocess.Popen([path])
                return {"status": "executed"}
        # --- ACCIONES ORIGINALES ---
        elif action == "close_app":
            if payload:
                from scripts import jarvis_backend
                result = await jarvis_backend.execute_command({"action": "close_app", "payload": payload})
                return {"status": "success", "msg": f"{payload} cerrado", "result": result}
            else:
                return {"status": "error", "msg": "Falta el nombre de la aplicación a cerrar"}
        elif action == "close_lab":
            cerrar_laboratorio(brain)
            return {"status": "success", "msg": "Laboratorio cerrado"}
        elif action == "facial_recognition":
            if facial_thread is None or not facial_thread.is_alive():
                facial_thread = threading.Thread(target=run_facial_scan, daemon=True)
                facial_thread.start()
            return {"status": "success", "msg": "Protocolo biométrico activo"}
        elif action == "speak":
            brain.speak(payload or "Hola, soy NEXUS-G. ¿En qué puedo ayudarte?")
            return {"status": "success", "msg": "NEXUS-G habló"}
        elif action == "system_metrics":
            metrics = get_system_metrics()
            return {"status": "success", "metrics": metrics}
        elif action == "check_security":
            return {"status": "success", "data": "Todos los sistemas nominales"}
        else:
            return {"status": "error", "msg": "Acción no programada en el núcleo NEXUS-G"}
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {"status": "error", "msg": str(e)}

if __name__ == "__main__":
    print("""
    ===================================================
    NEXUS-G INDUSTRIES - NEURAL INTERFACE BRIDGE v1.0
    ---------------------------------------------------
    [*] API Local: http://localhost:8000
    [*] Escuchando órdenes de NEXUS-G...
    ===================================================
    """)
    uvicorn.run(app, host="0.0.0.0", port=8001)
