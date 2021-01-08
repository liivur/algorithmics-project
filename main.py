import pygame
import random
import sys
from objects import Creature, Food, World
from dna import DNA

creatures = []
pop_size = 50
for i in range(pop_size):
    color = pygame.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    x = random.randint(0, 1024)
    y = random.randint(0, 768)
    gene = [random.uniform(0, 1), color.r/255, color.g/255, color.b/255]
    print(f"gene: {gene} generated")
    creatures.append(Creature(x=x, y=y, color=color,dna=DNA(gene), name='Creature '+str(i)))



food = []

world = World(1024, 768, creatures=creatures, edibles=food, creature_spawn_interval=5000)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    world.tick()
