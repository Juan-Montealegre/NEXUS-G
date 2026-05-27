import os
import subprocess
import sys
import ctypes
import pyautogui
import keyboard
import mouse
import time

def is_admin():
    """Verifica si el script se está ejecutando como administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Reinicia el script con privilegios de administrador si no los tiene."""
    if not is_admin():
        print("Reiniciando como administrador...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
        sys.exit()

def abrir_aplicacion(ruta):
    """Abre una aplicación por alias, ruta, AppID, comando especial, etc."""
    import json
    try:
        # Cargar app_map.json
        with open("app_map.json", "r", encoding="utf-8") as f:
            app_map = json.load(f)
        aliases = app_map.get("aliases", {})
        exe_apps = app_map.get("exe_apps", {})
        # Resolver alias
        nombre = ruta.lower()
        if nombre in aliases:
            nombre = aliases[nombre]
        valor = exe_apps.get(nombre, nombre)

        # Lanzar según tipo
        if valor.startswith("ms-settings:"):
            # Configuración de Windows
            os.system(f'start {valor}')
        elif valor.startswith("steam://"):
            # Lanzar juegos de Steam desde el menú inicio
            os.system(f'start shell:AppsFolder\\{valor}')
        elif valor.endswith(".exe") or os.path.isabs(valor):
            subprocess.Popen(valor)
        elif "!" in valor or "_8wekyb3d8bbwe" in valor or valor.startswith("{"):
            # AppID UWP/Store
            os.system(f'start shell:AppsFolder\\{valor}')
        else:
            # Otros comandos o rutas
            try:
                subprocess.Popen(valor)
            except Exception:
                os.system(f'start {valor}')
        print(f"Aplicación abierta: {valor}")
    except Exception as e:
        print(f"Error al abrir aplicación: {e}")

def cerrar_aplicacion(nombre_proceso):
    """Cierra una aplicación por nombre de proceso (ej: notepad.exe)."""
    import json
    try:
        # Cargar app_map.json
        with open("app_map.json", "r", encoding="utf-8") as f:
            app_map = json.load(f)
        aliases = app_map.get("aliases", {})
        exe_apps = app_map.get("exe_apps", {})
        # Resolver alias
        nombre = nombre_proceso.lower()
        if nombre in aliases:
            nombre = aliases[nombre]
        exe = exe_apps.get(nombre, nombre)
        exe_name = os.path.basename(exe)
        # Si es .exe, cerrar normalmente
        if exe_name.endswith('.exe'):
            os.system(f"taskkill /f /im {exe_name}")
            print(f"Aplicación cerrada: {exe_name}")
            return
        # Si es AppID UWP/Store, buscar proceso por AppUserModelId
        if '!' in exe or '_8wekyb3d8bbwe' in exe or exe.startswith('{'):
            # Usar PowerShell para buscar y cerrar el proceso
            import subprocess
            ps_script = f"Get-Process | Where {{$_.MainWindowTitle -ne '' -and $_.Path -ne $null}} | Where {{$_.AppUserModelId -eq '{exe}'}} | ForEach-Object {{$_.CloseMainWindow() | Out-Null; $_.Kill()}}"
            result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Intento de cierre para UWP/Store: {exe}")
            else:
                print(f"No se pudo cerrar UWP/Store: {exe}")
            return
        # Si es ms-settings o comando especial, no se puede cerrar
        if exe.startswith('ms-settings:') or exe.startswith('steam://'):
            print(f"No se puede cerrar este tipo de app: {exe}")
            return
        # Si no se reconoce, intentar taskkill por nombre
        os.system(f"taskkill /f /im {exe_name}")
        print(f"Intento de cierre genérico: {exe_name}")
    except Exception as e:
        print(f"Error al cerrar aplicación: {e}")

# --- Control de teclado ---
def escribir_texto(texto):
    """Escribe texto como si fuera el teclado."""
    pyautogui.write(texto)

def presionar_tecla(tecla):
    """Presiona una tecla específica."""
    keyboard.press_and_release(tecla)

# --- Control de ratón ---
def mover_mouse(x, y, duracion=0.5):
    """Mueve el mouse a la posición (x, y) en la pantalla."""
    pyautogui.moveTo(x, y, duration=duracion)

def click_mouse(boton='left'):
    """Hace clic con el mouse (izquierdo por defecto)."""
    pyautogui.click(button=boton)

def scroll_mouse(cantidad):
    """Hace scroll con el mouse (positivo o negativo)."""
    pyautogui.scroll(cantidad)

if __name__ == "__main__":
    run_as_admin()
    # Ejemplos de uso:
    # abrir_aplicacion('notepad.exe')
    # time.sleep(2)
    # escribir_texto('Hola mundo!')
    # mover_mouse(100, 100)
    # click_mouse()
    # cerrar_aplicacion('notepad.exe')