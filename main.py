import pygame
import random
import sys
import objects as obj
from dna import BrainDNA, DNA
import logging
import atexit
import pickle

# logging.basicConfig(level=logging.DEBUG)
add_file_handler = False
add_stdout_handler = True
dump_filename = "world.dump"

handlers = []
if add_stdout_handler:
    handlers.append(logging.StreamHandler(sys.stdout))
if add_file_handler:
    # overwrites (each execution) file out.log
    handlers.append(logging.FileHandler(filename='out.log', mode='w'))

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG,
                    handlers=handlers)

logger = logging.getLogger(__name__)

if len(sys.argv) > 1:
    with open(file=sys.argv[1], mode='rb') as file_handle:
        world = pickle.loads(file_handle.read())
else:
    creatures = []
    pop_size = 70

    for i in range(pop_size):
        color = pygame.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        x = random.randint(0, 1024)
        y = random.randint(0, 768)
        # color red, color green, color blue, speed, size, reproduction preference
        gene = [color.r / 255, color.g / 255, color.b / 255, random.uniform(0, 1), random.uniform(0, 1),
                random.uniform(0, 1), random.uniform(0, 1)]
        print(f"gene: {gene} generated")
        creatures.append(obj.BrainCreature(x=x, y=y, dna=DNA(gene), brain_dna=BrainDNA(),
                                           name='BrainCreature_' + str(obj.creature_id_generator.get_next_id())))

    food = [obj.Food(random.uniform(0, 1000), random.uniform(0, 700)) for i in range(100)]
    world = obj.World(1024, 768, creatures=creatures, edibles=food, creature_spawn_interval=1000, food_spawn_interval=1000,
                  random_spawning=True,
                  max_creatures=100)


def dump_the_world_pickle(world_to_dump):
    logger.debug("dumping the world")
    with open(file=dump_filename, mode='wb') as file_handle:
        pickle.dump(world_to_dump, file_handle)


atexit.register(dump_the_world_pickle, world)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    world.tick()
