import speech_recognition as sr


class JarvisEars:
    def __init__(self, speak_event=None):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.speak_event = speak_event
        # Ajustes de sensibilidad
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8  # Tiempo de silencio para terminar frase
        self.recognizer.energy_threshold = 300 # Sensibilidad mínima

    def listen(self):
        # Espera a que termine la voz antes de escuchar
        if self.speak_event is not None and self.speak_event.is_set():
            print("[SISTEMA] Esperando a que termine la voz...")
            self.speak_event.wait()
            # Cool-down breve para evitar eco
            import time
            time.sleep(0.3)
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("\n[OÍDOS] Escuchando órdenes...")
            try:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
                query = self.recognizer.recognize_google(audio, language='es-ES')
                return query.lower()
            except sr.WaitTimeoutError:
                return ""
            except Exception:
                print("[SISTEMA] Interferencia detectada o audio no claro.")
                return ""