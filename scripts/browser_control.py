import os
import json
import subprocess

def abrir_url_en_opera(nombre_url):
    """
    Abre una URL registrada en browser_routes.json usando Opera.
    """
    with open("browser_routes.json", "r", encoding="utf-8") as f:
        rutas = json.load(f).get("browser_routes", {})
    url = rutas.get(nombre_url)
    if not url:
        return f"No se encontró la ruta para: {nombre_url}"
    # Ruta típica de Opera en Windows
    opera_path = r"C:\Program Files\Opera\launcher.exe"
    if not os.path.exists(opera_path):
        return "Opera no está instalado en la ruta estándar."
    try:
        subprocess.Popen([opera_path, url])
        return f"Abriendo en Opera: {url}"
    except Exception as e:
        return f"Error al abrir en Opera: {str(e)}"

# Nueva función: abrir_url_en_navegador
import webbrowser
def abrir_url_en_navegador(nombre_url):
    """
    Abre una URL registrada en browser_routes.json usando el navegador predeterminado del sistema.
    """
    with open("browser_routes.json", "r", encoding="utf-8") as f:
        rutas = json.load(f).get("browser_routes", {})
    url = rutas.get(nombre_url)
    if not url:
        return f"No se encontró la ruta para: {nombre_url}"
    try:
        webbrowser.open(url)
        return f"Abriendo en el navegador predeterminado: {url}"
    except Exception as e:
        return f"Error al abrir en el navegador: {str(e)}"
