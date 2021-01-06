import pygame
import random
from math import cos, pi, sin


class Object:
    def __init__(self, x: float, y: float, direction: float = 0.0):
        self.x = x
        self.y = y
        self.direction = direction


class SquareObject(Object):
    def __init__(self, x: float, y: float, size: float, color: pygame.Color, direction: float = 0.0):
        super().__init__(x, y, direction)
        self.rect = pygame.Rect(x + size // 2, y + size // 2, size, size)
        self.color = color
        self.size = size

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.color, self.rect)


class Creature(SquareObject):
    def __init__(self, x: float, y: float, size: float, color: pygame.Color, direction: float = 0.0, speed: float = 1.0):
        super().__init__(x, y, size, color, direction)
        self.speed = speed

    def tick(self, screen: pygame.Surface, objects: list, dt: float):
        vel_x = self.speed * sin(self.direction) * dt
        vel_y = self.speed * cos(self.direction) * dt
        new_rect = self.rect.move(vel_x, vel_y)

        bounds = screen.get_rect()
        while not bounds.contains(new_rect):
            self.direction = (self.direction + random.uniform(0, pi)) % (2 * pi)
            new_rect = self.rect.move(self.speed * sin(self.direction) * dt, self.speed * cos(self.direction) * dt)

        self.rect = new_rect


