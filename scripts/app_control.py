import pyautogui
import os

class AppOrchestrator:
    def buscar_en_opera(self, nombre_url):
        """Abre una URL registrada en browser_routes.json usando Opera GX."""
        import json
        import subprocess
        opera_path = r"C:\Users\LENOVO\AppData\Local\Programs\Opera GX\opera.exe"
        rutas = {}
        try:
            with open("browser_routes.json", "r", encoding="utf-8") as f:
                rutas = json.load(f).get("browser_routes", {})
        except Exception as e:
            return f"No se pudo leer browser_routes.json: {str(e)}"
        url = rutas.get(nombre_url)
        if not url:
            return f"No se encontró la ruta para: {nombre_url}"
        if not os.path.exists(opera_path):
            return "Opera GX no está instalado en la ruta estándar."
        try:
            subprocess.Popen([opera_path, url])
            return f"Abriendo en Opera GX: {url}"
        except Exception as e:
            return f"Error al abrir en Opera GX: {str(e)}"

    def buscar_contacto_whatsapp(self, nombre_contacto):
        """Busca un contacto en WhatsApp Desktop usando pyautogui y lo selecciona."""
        import time
        import pyperclip
        # Asume que WhatsApp Desktop está abierto y en primer plano
        try:
            pyautogui.hotkey('ctrl', 'f')  # Abre la barra de búsqueda
            time.sleep(0.3)
            pyperclip.copy(nombre_contacto)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            pyautogui.press('enter')
            return f"Contacto '{nombre_contacto}' buscado y seleccionado en WhatsApp."
        except Exception as e:
            return f"Error al buscar contacto en WhatsApp: {str(e)}"
    def write_in_active_app(self, text):
        """Escribe el texto dado en la aplicación activa usando pyautogui."""
        import time
        time.sleep(0.5)  # Pequeña pausa para asegurar el foco
        try:
            pyautogui.typewrite(text, interval=0.03)
            return f"Texto escrito: {text}"
        except Exception as e:
            return f"Error al escribir: {str(e)}"

    def control_spotify(self, command):
        if "reproduce" in command:
            pyautogui.press('playpause')
            return "Retomando su lista de reproducción, Señor."

    def close_app(self, app_name):
        """Cierra una aplicación por su nombre de ejecutable o alias."""
        import subprocess
        exe_name = app_name if app_name.lower().endswith('.exe') else app_name + '.exe'
        try:
            result = subprocess.run(["taskkill", "/f", "/im", exe_name], capture_output=True, text=True)
            if result.returncode == 0:
                return f"Cerrado: {exe_name}"
            else:
                # Intentar con psutil si taskkill falla
                import psutil
                killed = 0
                for p in psutil.process_iter(['name']):
                    if p.info['name'] and p.info['name'].lower() == exe_name.lower():
                        try:
                            p.kill()
                            killed += 1
                        except Exception:
                            pass
                if killed > 0:
                    return f"Cerrado con psutil: {exe_name}"
                return f"No se pudo cerrar: {exe_name}"
        except Exception as e:
            return f"Error al cerrar: {exe_name} ({str(e)})"

    def open_custom_app(self, app_name):
        # Mapeo de rutas de sus aplicaciones favoritas
        apps = {
            "discord": "C:\\Users\\User\\AppData\\Local\\Discord\\Update.exe --processStart Discord.exe",
            "obs": "C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe"
        }
        if app_name in apps:
            os.startfile(apps[app_name])
            return f"Desplegando {app_name}."
        return "Aplicación no encontrada en el registro."