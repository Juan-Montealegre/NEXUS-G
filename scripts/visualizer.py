import cv2
import numpy as np

class JarvisVisualizer:
    def __init__(self):
        self.width, self.height = 400, 200
        self.color = (255, 191, 0) # Azul Stark (BGR)

    def draw_wave(self, volume):
        # Creamos un lienzo negro
        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        center_y = self.height // 2
        
        # Dibujamos una onda basada en el volumen recibido
        points = []
        for x in range(0, self.width, 2):
            # Oscilación matemática para simular frecuencia
            y = int(center_y + (np.sin(x * 0.05) * volume * 50))
            points.append([x, y])
            
        points = np.array(points, np.int32)
        cv2.polylines(img, [points], False, self.color, 2)
        
        # Añadimos un efecto de brillo
        cv2.GaussianBlur(img, (5, 5), 0)
        return img