from scripts import database
from datetime import datetime
@app.on_event("startup")
def startup_event():
    database.create_tables()

# Endpoint para insertar un comando ejecutado
@app.post("/memoria/comando")
async def guardar_comando(data: dict):
    fecha = data.get("fecha") or datetime.now().isoformat()
    usuario = data.get("usuario", "desconocido")
    comando = data.get("comando", "")
    resultado = data.get("resultado")
    database.insertar_comando(fecha, usuario, comando, resultado)
    return {"status": "ok"}

# Endpoint para obtener últimos comandos
@app.get("/memoria/comandos")
def obtener_comandos(limit: int = 20):
    rows = database.obtener_comandos(limit)
    return [{"id": r[0], "fecha": r[1], "usuario": r[2], "comando": r[3], "resultado": r[4]} for r in rows]

# Endpoint para actualizar resultado de un comando
@app.put("/memoria/comando/{comando_id}")
async def actualizar_resultado(comando_id: int, data: dict):
    resultado = data.get("resultado", "")
    database.actualizar_resultado_comando(comando_id, resultado)
    return {"status": "ok"}

# Endpoint para eliminar un comando
@app.delete("/memoria/comando/{comando_id}")
def eliminar_comando(comando_id: int):
    database.eliminar_comando(comando_id)
    return {"status": "ok"}
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import psutil
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/metrics")
def get_metrics():
    """Devuelve métricas del sistema en tiempo real."""
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "temp": 55  # Mejora: usar sensores reales si están disponibles
    }

@app.post("/command")
async def execute(request: Request):
    """Ejecuta comandos físicos en la máquina según la acción recibida."""
    cmd = await request.json()
    action = cmd.get('action', '')
    output = ""
    # Ejemplo de acciones reales
    if action == "check_metrics":
        return get_metrics()
    elif action == "shutdown":
        os.system("shutdown /s /t 1")
        output = "Apagando el sistema..."
    elif action == "open_notepad":
        os.system("start notepad.exe")
        output = "Bloc de notas abierto."
    elif action == "say_hello":
        output = "Hola, Señor. NEXUS-G está en línea."
    else:
        output = f"Acción '{action}' no reconocida."
    return {"status": "success", "output": output}
