import pygame
import sys
from objects import Creature

pygame.init()

size = width, height = 640, 480
speed = [1, 1]
black = 0, 0, 0

screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

creatures = []
color = pygame.Color(50, 50, 50)
creatures.append(Creature(100.0, 100.0, 10.0, color, 1.0))
color = pygame.Color(50, 100, 50)
creatures.append(Creature(100.0, 100.0, 10.0, color, 2.0))

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill(black)
    dt = clock.tick(60)

    for creature in creatures:
        creature.tick(screen, [], dt)
        creature.draw(screen)

    pygame.display.flip()
