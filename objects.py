import pygame
import random
import auxiliary
from dna import DNA
from math import cos, pi, sin


# ? monitor number of creatures in the world

class World:
    def __init__(self, width: int = 640, height: int = 480, background: tuple = (0, 0, 0),
                 creatures: list = [], edibles: list = [], food_spawn_interval: int = 1000,
                 creature_spawn_interval: int = 10000):
        pygame.init()
        self.size = self.width, self.height = width, height
        self.background = background
        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()

        self.food_spawn_counter = 0
        self.food_spawn_interval = food_spawn_interval
        self.edibles = edibles

        self.creature_spawn_counter = 0
        self.creature_spawn_interval = creature_spawn_interval
        self.creatures = creatures

        self.creature_total = len(creatures)

    def add_creature(self, creature):
        # sanity check so the computer doesn't crash with bad params
        if len(self.creatures) > 100:
            pass
        self.creatures.append(creature)
        self.creature_total += 1

    def add_edible(self, food):
        self.edibles.append(food)

    def generate_random_creature(self):
        color = pygame.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        gene = [random.uniform(0, 1), color.r/255, color.g/255, color.b/255]
        print("random creature added")
        return Creature(x=random.uniform(0, self.width), y=random.uniform(0, self.height),
                        color=color, dna=DNA(gene), name='Creature ' + str(self.creature_total + 1))


    def remove_creature(self, creature):
        self.creatures.remove(creature)
        self.add_edible(Food(creature.x, creature.y, value=creature.size * 2, color=creature.color))

    def remove_edible(self, edible):
        self.edibles.remove(edible)

    def tick(self):
        self.screen.fill(self.background)
        dt = self.clock.tick(60)

        self.update_creatures(dt)
        self.update_edibles(dt)

        pygame.display.flip()

    def update_creatures(self, dt):
        self.creature_spawn_counter += dt
        if self.creature_spawn_counter > self.creature_spawn_interval:
            self.add_creature(self.generate_random_creature())
            self.creature_spawn_counter = 0

        for creature in self.creatures:
            creature.tick(self, dt)
            if creature.health > 0:
                creature.draw(self.screen)
            else:
                self.remove_creature(creature)

    def update_edibles(self, dt):
        self.food_spawn_counter += dt
        if self.food_spawn_counter > self.food_spawn_interval:
            self.add_edible(Food(random.uniform(0, self.width), random.uniform(0, self.height)))
            self.food_spawn_counter = 0

        for food in self.edibles:
            food.draw(self.screen)


class Object:
    def __init__(self, x: float, y: float, direction: float = 0.0, name: str = 'object'):
        self.x = x
        self.y = y
        self.direction = direction
        self.name = name


class SquareObject(Object):
    def __init__(self, x: float, y: float, size: float, color: pygame.Color, direction: float = 0.0,
                 name: str = 'object'):
        super().__init__(x, y, direction, name=name)
        self.rect = pygame.Rect(x + size // 2, y + size // 2, size, size)
        self.color = color
        self.size = size

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.color, self.rect)


class Creature(SquareObject):
    base_health = 300
    min_size = 1
    max_size = 50
    min_speed = 1
    max_speed = 5

    def __init__(self, x: float, y: float, color: pygame.Color, dna=DNA(),
                 direction: float = 0.0,
                 name: str = 'object', multiply_chance=0.05):
        # since speed and size are inversely related (auxiliary.map function) we can code its value with one gene
        self.dna = dna
        self.size = auxiliary.map(self.dna.genes[0], 0, 1, 1, 50)
        self.speed = auxiliary.map(self.dna.genes[0], 1, 50, 5, 1)
        super().__init__(x, y, self.size, color, direction, name=name)
        self.health = self.base_health
        self.multiply_chance = multiply_chance

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        color = pygame.Color(255, 255, 255)
        a = pygame.math.Vector2(self.x, self.y)
        b = pygame.math.Vector2(self.x - self.size * sin(self.direction),
                                self.y - self.size * cos(self.direction))
        pygame.draw.line(surface, color, a, b)

    def find_target(self, objects):
        pass

    def multiply(self) -> 'Creature':
        child_dna = self.dna.copy()
        child_dna.mutation()
        color = pygame.Color(int(child_dna.genes[1] * 255), int(child_dna.genes[2] * 255), int(child_dna.genes[3] * 255))
        return Creature(self.x, self.y, color=color, dna=child_dna, direction=(self.direction + pi) % (2 * pi),
                        name=self.name)

    def update_health(self, dt):
        self.health -= self.speed * self.size * dt * 0.0005

    def update_rect(self, rect: pygame.Rect):
        self.rect = rect
        self.x = rect.centerx
        self.y = rect.centery

    def tick(self, world: World, dt: float):
        vel_x = self.speed / 10 * sin(self.direction) * dt
        vel_y = self.speed / 10 * cos(self.direction) * dt
        new_rect = self.rect.move(vel_x, vel_y)

        bounds = world.screen.get_rect()
        if not bounds.contains(new_rect):
            self.direction = (self.direction + random.uniform(0, pi)) % (2 * pi)
            new_rect = self.rect.clamp(bounds)

        for edible in world.edibles:
            if self.rect.colliderect(edible.rect):
                self.health += edible.value
                world.remove_edible(edible)

        # creature interaction
        for creature in world.creatures:
            if creature != self and self.rect.colliderect(creature.rect):
                # sexual reproduction
                if random.random() < self.multiply_chance * dt / 1000:
                    child_dna = self.dna.crossover(creature.dna)
                    child_dna.mutation()
                    print("a child is born via sexual reproduction")
                    color = pygame.Color(int(child_dna.genes[1]*255), int(child_dna.genes[2]*255), int(child_dna.genes[3]*255))
                    child = Creature(self.x, self.y, color=color, dna=child_dna,
                             direction=(self.direction + pi) % (2 * pi),
                             name=self.name)
                    world.add_creature(child)

        # asexual reproduction
        if random.random() < self.multiply_chance * dt / 1000:
            print("a child is born via asexual reproduction")
            world.add_creature(self.multiply())

        self.update_health(dt)
        self.update_rect(new_rect)


class Food(SquareObject):
    def __init__(self, x: float, y: float, value: float = 30.0, size: float = 3.0,
                 color: pygame.Color = pygame.Color(125, 125, 125)):
        super().__init__(x, y, size, color, 0, name='food')
        self.value = value
