import face_recognition
import cv2
import numpy as np
import sys

class JarvisVision:
    def __init__(self):
        self.authorized_encoding = None
        self.load_reference_image()

    def load_reference_image(self):
        try:
            image = face_recognition.load_image_file("creator.jpg")
            encodings = face_recognition.face_encodings(image)
            
            if len(encodings) > 0:
                self.authorized_encoding = encodings[0]
                print("[SISTEMA] Perfil biométrico del Creador cargado con éxito.")
            else:
                print("[CRÍTICO] No se detectó ningún rostro en 'creator.jpg'. Use otra foto.")
                sys.exit() # Detenemos el sistema para evitar el crash posterior
        except Exception as e:
            print(f"[ERROR] Error al cargar la imagen: {e}")
            sys.exit()

    def identify_user(self, frame):
        if self.authorized_encoding is None:
            return "Error de Base de Datos"

        # Reducción para velocidad
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for face_encoding in face_encodings:
            # Comparación con tolerancia ajustada
            matches = face_recognition.compare_faces([self.authorized_encoding], face_encoding, tolerance=0.5)
            if True in matches:
                return "Creador"
        return "Desconocido"
    