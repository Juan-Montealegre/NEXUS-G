import ollama
import pyttsx3
import re

class JarvisBrain:
    def __init__(self):
        self.model = "llama3"
        # Inicializar motor de voz
        try:
            self.engine = pyttsx3.init()
            self.configurar_voz()
        except Exception as e:
            print(f"[ERROR VOZ] No se pudo inicializar pyttsx3: {e}")

        self.system_prompt = (
            "Eres J.A.R.V.I.S., un asistente avanzado. "
            "Responde SIEMPRE en ESPAÑOL. Sé breve y elegante."
        )

    def configurar_voz(self):
        # Ajustar velocidad y voz en español
        self.engine.setProperty('rate', 185) 
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "spanish" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break

    def speak(self, text):
        """Hace que J.A.R.V.I.S hable y bloquea escucha si hay evento. Incluye logs de depuración."""
        print("[AUDIOPROCESADOR] Generando voz...")
        if hasattr(self, 'speak_event') and self.speak_event is not None:
            self.speak_event.set()
        try:
            print("[SISTEMA] Texto a reproducir:", text)
            self.engine.say(text)
            self.engine.runAndWait()
            print("[SISTEMA] Voz reproducida correctamente.")
        except Exception as e:
            print("[SISTEMA] Error al reproducir voz:", e)
        if hasattr(self, 'speak_event') and self.speak_event is not None:
            self.speak_event.clear()

    def think(self, user_input):
        try:
            # Consultar a Ollama
            response = ollama.chat(model=self.model, messages=[
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': user_input}
            ])
            
            respuesta_texto = response['message']['content']
            respuesta_limpia = re.sub(r'\*+', '', respuesta_texto).strip()
            
            # --- LA CLAVE ESTÁ AQUÍ ---
            # Primero llamamos a speak para que el audio salga 
            # mientras el texto se imprime
            self.speak(respuesta_limpia)
            return respuesta_limpia
            
        except Exception as e:
            error_msg = "Señor, mis protocolos de comunicación están offline."
            self.speak(error_msg)
            return f"{error_msg}: {e}"