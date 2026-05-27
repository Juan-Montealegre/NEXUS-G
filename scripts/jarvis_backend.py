from fastapi import FastAPI, Query, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import psutil
import json
import os
import numpy as np
import cv2
APP_MAP_FILE = "app_map.json"
STORE_CACHE_FILE = "store_cache.json"
try:
    from security import JarvisVision
except ImportError:
    JarvisVision = None
from scripts.test_vision import iniciar_sesion_biometrica

app = FastAPI(
    title="JARVIS Launcher API",
    version="3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restringir en producción
    allow_methods=["*"],
    allow_headers=["*"],
)

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from control_apps import escribir_texto, presionar_tecla, mover_mouse, click_mouse, scroll_mouse, abrir_aplicacion, cerrar_aplicacion
from pydantic import BaseModel

class TextInput(BaseModel):
    texto: str

class KeyInput(BaseModel):
    tecla: str

class MouseMoveInput(BaseModel):
    x: int
    y: int
    duracion: float = 0.5

class MouseClickInput(BaseModel):
    boton: str = 'left'

class MouseScrollInput(BaseModel):
    cantidad: int

@app.post("/type_text")
def api_escribir_texto(data: TextInput):
    try:
        escribir_texto(data.texto)
        return {"result": f"Texto escrito: {data.texto}"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/press_key")
def api_presionar_tecla(data: KeyInput):
    try:
        presionar_tecla(data.tecla)
        return {"result": f"Tecla presionada: {data.tecla}"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/move_mouse")
def api_mover_mouse(data: MouseMoveInput):
    try:
        mover_mouse(data.x, data.y, data.duracion)
        return {"result": f"Mouse movido a: ({data.x}, {data.y})"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/click_mouse")
def api_click_mouse(data: MouseClickInput):
    try:
        click_mouse(data.boton)
        return {"result": f"Click mouse: {data.boton}"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/scroll_mouse")
def api_scroll_mouse(data: MouseScrollInput):
    try:
        scroll_mouse(data.cantidad)
        return {"result": f"Scroll mouse: {data.cantidad}"}
    except Exception as e:
        return {"error": str(e)}

# --- ENDPOINTS CONTROL APPS GENERALES ---
class AppInput(BaseModel):
    nombre: str

class ProcInput(BaseModel):
    nombre: str

@app.post("/open_app")
def api_abrir_aplicacion(data: AppInput):
    try:
        abrir_aplicacion(data.nombre)
        return {"result": f"Aplicación abierta: {data.nombre}"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/close_app")
def api_cerrar_aplicacion(data: ProcInput):
    try:
        cerrar_aplicacion(data.nombre)
        return {"result": f"Aplicación cerrada: {data.nombre}"}
    except Exception as e:
        return {"error": str(e)}
try:
    from security import JarvisVision
except ImportError:
    JarvisVision = None
from scripts.test_vision import iniciar_sesion_biometrica

app = FastAPI(
    title="JARVIS Launcher API",
    version="3.0"
)
# Endpoint para escaneo biométrico clásico (loop de cámara)
@app.post("/biometric_scan")
def biometric_scan():
    try:
        result = iniciar_sesion_biometrica()
        return {"result": "ACCESO CONCEDIDO" if result else "ACCESO DENEGADO"}
    except Exception as e:
        return {"error": str(e)}
# Endpoint para recibir un frame y procesar reconocimiento facial
@app.post("/process_frame")
async def process_frame(file: UploadFile = File(...)):
    if JarvisVision is None:
        return {"error": "JarvisVision no disponible"}
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        vision = JarvisVision()
        user = vision.identify_user(frame)
        return {"user": user}
    except Exception as e:
        return {"error": str(e)}

# Listar archivos y carpetas de un directorio
@app.get("/list_dir")
def list_dir(path: str = Query("", description="Ruta absoluta o relativa")):
    import os
    if not path:
        path = os.path.expanduser("~")
    if not os.path.exists(path):
        return {"error": "Ruta no encontrada"}
    items = []
    for name in os.listdir(path):
        full = os.path.join(path, name)
        items.append({
            "name": name,
            "is_dir": os.path.isdir(full),
            "path": full
        })
    return {"items": items}

# Abrir archivo o carpeta (explorador o app asociada)
@app.post("/open_file")
def open_file(path: str = Body(...)):
    import os
    import subprocess
    if not os.path.exists(path):
        return {"error": "Archivo o carpeta no encontrada"}
    try:
        os.startfile(path)
        return {"result": f"Abierto: {path}"}
    except Exception as e:
        try:
            subprocess.Popen(["explorer.exe", path])
            return {"result": f"Abierto con explorer: {path}"}
        except Exception as e2:
            return {"error": f"No se pudo abrir: {path}", "details": str(e2)}

# Cerrar archivo por nombre de proceso (ejemplo: WINWORD.EXE)
@app.post("/close_file")
def close_file(exe: str = Body(...)):
    import subprocess
    try:
        subprocess.run(["taskkill", "/f", "/im", exe], capture_output=True)
        return {"result": f"Cerrado: {exe}"}
    except Exception as e:
        return {"error": f"No se pudo cerrar: {exe}", "details": str(e)}

# =========================
# CERRAR APLICACIONES
# =========================
@app.post("/close_apps")
def close_apps(data: dict = Body(...)):
    """
    Cierra una aplicación por nombre, alias o ejecutable.
    data = {"name": "word"}  # puede ser alias, nombre o exe
    """
    app_map = load_app_map()
    aliases = app_map.get("aliases", {})
    exe_apps = app_map.get("exe_apps", {})
    name = data.get("name", "").lower()
    debug = []
    exe = None
    # Resolver alias
    if name in aliases:
        name = aliases[name]
        debug.append(f"Alias resuelto: {name}")
    # Buscar exe
    if name in exe_apps:
        exe = exe_apps[name]
        debug.append(f"EXE resuelto: {exe}")
    else:
        exe = name
        debug.append(f"Usando nombre directo: {exe}")
    # Extraer solo el nombre del ejecutable si es ruta
    exe_name = os.path.basename(exe).lower()
    try:
        result = subprocess.run(["taskkill", "/f", "/im", exe_name], capture_output=True, text=True)
        if result.returncode == 0:
            return {"result": f"Cerrado: {exe_name}", "debug": debug}
        else:
            return {"error": f"No se pudo cerrar: {exe_name}", "details": result.stderr, "debug": debug}
    except Exception as e:
        return {"error": f"Error al cerrar: {exe_name}", "details": str(e), "debug": debug}


# =========================
# UTILIDADES
# =========================

def load_app_map():
    if not os.path.exists(APP_MAP_FILE):
        return {"aliases": {}, "exe_apps": {}}
    with open(APP_MAP_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_store_cache(force_refresh=False):
    if os.path.exists(STORE_CACHE_FILE) and not force_refresh:
        with open(STORE_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    # Obtener apps Microsoft Store
    result = subprocess.run(
        ["powershell", "-Command", "Get-StartApps | ConvertTo-Json"],
        capture_output=True,
        text=True
    )

    apps = json.loads(result.stdout)
    store_map = {app["Name"].lower(): app["AppID"] for app in apps}

    with open(STORE_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(store_map, f, indent=2, ensure_ascii=False)

    return store_map

# =========================
# ENDPOINTS
# =========================

@app.get("/")
def root():
    return {"status": "JARVIS online 🤖"}

@app.get("/metrics")
def metrics():
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    }

@app.post("/refresh_store_apps")
def refresh_store_apps():
    store = load_store_cache(force_refresh=True)
    return {
        "result": "Apps de Microsoft Store actualizadas",
        "total_apps": len(store)
    }


@app.post("/command")
async def execute_command(data: dict):
    action = data.get("action")
    payload = data.get("payload", "").lower()

    if action == "poner_musica_spotify":
        from scripts.app_control import AppOrchestrator
        orchestrator = AppOrchestrator()
        result = orchestrator.control_spotify(payload)
        return {"result": result}
    elif action == "escribir_en_whatsapp":
        from scripts.app_control import AppOrchestrator
        orchestrator = AppOrchestrator()
        partes = payload.split('|', 1)
        contacto = partes[0].strip()
        mensaje = partes[1] if len(partes) > 1 else ""
        result = orchestrator.escribir_en_whatsapp(contacto, mensaje)
        return {"result": result}
    elif action == "programar_en_vscode":
        from scripts.app_control import AppOrchestrator
        orchestrator = AppOrchestrator()
        partes = payload.split('|', 1)
        ruta = partes[0].strip()
        contenido = partes[1] if len(partes) > 1 else ""
        result = orchestrator.programar_en_vscode(ruta, contenido)
        return {"result": result}
    elif action == "buscar_archivo":
        from scripts.app_control import AppOrchestrator
        orchestrator = AppOrchestrator()
        partes = payload.split('|')
        nombre = partes[0].strip()
        carpeta = partes[1].strip() if len(partes) > 1 else None
        result = orchestrator.buscar_archivo(nombre, carpeta)
        return {"result": result}
    elif action == "crear_archivo":
        from scripts.app_control import AppOrchestrator
        orchestrator = AppOrchestrator()
        partes = payload.split('|', 1)
        ruta = partes[0].strip()
        contenido = partes[1] if len(partes) > 1 else ""
        result = orchestrator.crear_archivo(ruta, contenido)
        return {"result": result}
    elif action == "buscar_en_opera":
        from scripts.app_control import AppOrchestrator
        orchestrator = AppOrchestrator()
        result = orchestrator.buscar_en_opera(payload)
        return {"result": result}
    elif action == "buscar_contacto_whatsapp":
        from scripts.app_control import AppOrchestrator
        orchestrator = AppOrchestrator()
        result = orchestrator.buscar_contacto_whatsapp(payload)
        return {"result": result}
    elif action == "escribir_en_app":
        from scripts.app_control import AppOrchestrator
        orchestrator = AppOrchestrator()
        result = orchestrator.write_in_active_app(payload)
        return {"result": result}

    # ...existing code for other actions...

    app_map = load_app_map()
    store_apps = load_store_cache()
    aliases = app_map.get("aliases", {})
    exe_apps = app_map.get("exe_apps", {})
    debug = []

    if action == "open_app":
        app_name = aliases.get(payload, payload)
        debug.append(f"Nombre final: {app_name}")
        # 1️⃣ Microsoft Store (solo si el AppID no es ruta ni .exe)
        if app_name in exe_apps:
            appid = exe_apps[app_name]
            # Si el AppID parece una ruta o termina en .exe, NO abrir como Store
            if not ("\\" in appid or "/" in appid or appid.lower().endswith(".exe")):
                try:
                    subprocess.Popen([
                        "powershell",
                        "-Command",
                        f"start shell:AppsFolder\\{appid}"
                    ])
                    return {"result": f"Abriendo {app_name} (Microsoft Store)", "debug": debug}
                except Exception as e:
                    debug.append(f"Error con shell:AppsFolder: {str(e)}")
            # Si es ruta absoluta o .exe, abrir como clásico
            if (appid.startswith("C:\\") or appid.startswith("D:\\") or ":\\" in appid or "/" in appid) and appid.lower().endswith(".exe"):
                try:
                    os.startfile(appid)
                    debug.append("os.startfile OK")
                    return {"result": f"Abriendo {app_name} (ruta absoluta)", "debug": debug}
                except Exception as e:
                    debug.append(f"Error con os.startfile: {str(e)}. Intentando con subprocess...")
                    try:
                        subprocess.Popen([appid])
                        debug.append("subprocess.Popen OK")
                        return {"result": f"Abriendo {app_name} con subprocess", "debug": debug}
                    except Exception as e2:
                        debug.append(f"Error con subprocess: {str(e2)}. Intentando con cmd /c start...")
                        try:
                            subprocess.Popen(["cmd", "/c", f"start \"{appid}\""], shell=True)
                            debug.append("cmd /c start ruta OK")
                            return {"result": f"Abriendo {app_name} con cmd /c start ruta", "debug": debug}
                        except Exception as e3:
                            debug.append(f"Error con cmd /c start: {str(e3)}")
                            return {"error": f"No se pudo abrir {app_name}", "details": str(e3), "debug": debug}
            # Si es solo el nombre, usar PowerShell
            try:
                subprocess.Popen([
                    "powershell",
                    "-Command",
                    f"Start-Process {appid}"
                ])
                return {"result": f"Abriendo {app_name}", "debug": debug}
            except Exception as e:
                debug.append(f"Error con subprocess: {str(e)}. Intentando con os.startfile...")
                try:
                    os.startfile(appid)
                    return {"result": f"Abriendo {app_name} con startfile", "debug": debug}
                except Exception as e2:
                    debug.append(f"Error con startfile: {str(e2)}")
                    return {"error": f"No se pudo abrir {app_name}", "details": str(e2), "debug": debug}
        # 2️⃣ Último intento (PATH / sistema)
        try:
            subprocess.Popen([
                "powershell",
                "-Command",
                f"Start-Process {app_name}"
            ])
            return {"result": f"Intentando abrir {app_name}", "debug": debug}
        except Exception as e:
            return {
                "error": "No se pudo abrir la aplicación",
                "details": str(e),
                "debug": debug
            }
    elif action == "close_app":
        # Usar AppOrchestrator para cerrar aplicaciones
        from scripts.app_control import AppOrchestrator
        orchestrator = AppOrchestrator()
        app_name = payload
        # Resolver alias
        if app_name in aliases:
            app_name = aliases[app_name]
            debug.append(f"Alias resuelto: {app_name}")
        # Buscar exe
        if app_name in exe_apps:
            app_name = exe_apps[app_name]
            debug.append(f"EXE resuelto: {app_name}")
        else:
            debug.append(f"Usando nombre directo: {app_name}")
        result = orchestrator.close_app(os.path.basename(app_name))
        return {"result": result, "debug": debug}
    else:
        return {"error": "Acción no soportada"}

# Alias para compatibilidad con bridge.py
get_system_metrics = metrics
