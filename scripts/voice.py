import pyttsx3
import requests
import os

class JarvisVoice:
    def __init__(self, api_key=None, voice_id="Josh"): # Josh tiene un tono muy sofisticado
        self.api_key = api_key
        self.voice_id = voice_id
        # Fallback local
        self.local_engine = pyttsx3.init()
        self.setup_local_voice()

    def setup_local_voice(self):
        voices = self.local_engine.getProperty('voices')
        self.local_engine.setProperty('rate', 175)
        # Seleccionamos una voz masculina si está disponible
        for voice in voices:
            if "Spanish" in voice.languages or "male" in voice.name.lower():
                self.local_engine.setProperty('voice', voice.id)
                break

    def speak(self, text):
        if self.api_key:
            try:
                # Intento con ElevenLabs para máxima calidad
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
                headers = {"xi-api-key": self.api_key}
                data = {"text": text, "model_id": "eleven_multilingual_v2"}
                response = requests.post(url, json=data, headers=headers)
                if response.status_code == 200:
                    with open("temp_voice.mp3", "wb") as f:
                        f.write(response.content)
                    os.system("start temp_voice.mp3") # O usar pygame para reproducir
                    return
            except Exception as e:
                print(f"Error ElevenLabs: {e}. Usando motor local.")
        
        # Uso del motor local por defecto
        self.local_engine.say(text)
        self.local_engine.runAndWait()