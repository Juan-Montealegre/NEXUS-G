import psutil

class JarvisTelemetry:
    def get_stats(self):
        cpu_usage = psutil.cpu_percent(interval=None)
        ram_usage = psutil.virtual_memory().percent
        # Intentar obtener temperatura (depende del hardware/OS)
        temp = "N/A"
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                temp = f"{temps['coretemp'][0].current}°C"
        
        return {
            "cpu": f"CPU: {cpu_usage}%",
            "ram": f"RAM: {ram_usage}%",
            "temp": f"TEMP: {temp}"
        }