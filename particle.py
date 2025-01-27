# particle.py
"""
Defines the Particle class and basic physics constants/logic.
"""

import math

# Physics constants
GRAVITY = 9.80665
MAX_SPEED = 1e4
MAX_SPEED_SQ = MAX_SPEED**2

class Particle:
    def __init__(self, x, y, mass, symbol, color, radius):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0

        self.mass = mass
        self.symbol = symbol
        self.color = color
        self.radius = radius

    def apply_forces(self, dt):
        # simple gravity
        self.vy += GRAVITY * dt

        # clamp velocity
        sp_sq = self.vx*self.vx + self.vy*self.vy
        if sp_sq > MAX_SPEED_SQ:
            sp = math.sqrt(sp_sq)
            scale = MAX_SPEED / sp
            self.vx *= scale
            self.vy *= scale

    def update_position(self, dt, main_width, main_height):
        # Move
        self.x += self.vx * dt
        self.y += self.vy * dt

        # floor collision
        if self.y + self.radius >= main_height:
            overlap = (self.y + self.radius) - main_height
            self.y -= overlap
            if self.vy > 0:
                self.vy = -0.5 * self.vy
                if abs(self.vy) < 1.0:
                    self.vy = 0

        # top collision
        if self.y - self.radius < 0:
            overlap = self.radius - self.y
            self.y += overlap
            if self.vy < 0:
                self.vy = -0.5 * self.vy

        # left
        if self.x - self.radius < 0:
            overlap = self.radius - self.x
            self.x += overlap
            if self.vx < 0:
                self.vx = -0.5 * self.vx

        # right
        if self.x + self.radius > main_width:
            overlap = (self.x + self.radius) - main_width
            self.x -= overlap
            if self.vx > 0:
                self.vx = -0.5 * self.vx

    def draw(self, surface, font=None):
        import pygame
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

        # skip text if symbol == "H₂O"
        if self.symbol and self.symbol != "H₂O":
            if font is None:
                font = pygame.font.SysFont(None, 20)
            txt_surf = font.render(self.symbol, True, (255,255,255))
            txt_rect = txt_surf.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(txt_surf, txt_rect)
