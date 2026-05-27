
import pygame

class JarvisPhysicsUI:
    def __init__(self):
        self.theme_color = (0, 255, 255) # Cyan original

    def set_theme(self, mode):
        if mode == "CRIMSON_ALERT":
            self.theme_color = (255, 0, 0) # Rojo Alerta
        else:
            self.theme_color = (0, 255, 255)

    def draw_hud(self, hand_pos=None):
        # Usar self.theme_color para todos los dibujos del HUD
        if hand_pos is not None:
            x, y = hand_pos
        else:
            x, y = 100, 100  # Coordenadas por defecto
        pygame.draw.circle(self.screen, self.theme_color, (x, y), 60, 1)