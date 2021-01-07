import pygame
import random
import sys
from objects import Creature, Food, World

creatures = []
color = pygame.Color(150, 50, 50)
creatures.append(Creature(x=100.0, y=100.0, size=10.0, color=color, speed=8, name='Small 1'))
color = pygame.Color(150, 100, 50)
creatures.append(Creature(x=200.0, y=100.0, size=20.0, color=color, speed=4, name='Big 1'))

food = []

world = World(1024, 768, creatures=creatures, edibles=food, creature_spawn_interval=5000)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    world.tick()
