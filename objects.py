import pygame
import random
from math import cos, pi, sin


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
        self.creatures.append(creature)
        self.creature_total += 1

    def add_edible(self, food):
        self.edibles.append(food)

    def generate_random_creature(self):
        color = pygame.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        return Creature(x=random.uniform(0, self.width), y=random.uniform(0, self.height),
                        size=random.uniform(1, 50), color=color, speed=random.random() + 0.0001,
                        name='Creature ' + str(self.creature_total + 1))

    def remove_creature(self, creature):
        self.creatures.remove(creature)

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
        color = pygame.Color(255, 255, 255)
        a = pygame.math.Vector2(self.rect.center)
        b = pygame.math.Vector2(self.rect.centerx - self.size * sin(self.direction),
                                self.rect.centery - self.size * cos(self.direction))
        pygame.draw.line(surface, color, a, b)


class Creature(SquareObject):
    def __init__(self, x: float, y: float, size: float, color: pygame.Color, direction: float = 0.0, speed: float = 1.0,
                 name: str = 'object'):
        super().__init__(x, y, size, color, direction, name=name)
        self.speed = speed
        self.health = 300

    def find_target(self, objects):
        pass

    def update_health(self, dt):
        self.health -= self.speed * self.size * dt * 0.001

    def tick(self, world: World, dt: float):
        vel_x = self.speed * sin(self.direction) * dt
        vel_y = self.speed * cos(self.direction) * dt
        new_rect = self.rect.move(vel_x, vel_y)

        bounds = world.screen.get_rect()
        if not bounds.contains(new_rect):
            self.direction = (self.direction + random.uniform(0, pi)) % (2 * pi)
            new_rect = self.rect.clamp(bounds)

        for edible in world.edibles:
            if self.rect.colliderect(edible.rect):
                self.health += edible.value
                world.remove_edible(edible)

        self.rect = new_rect
        self.update_health(dt)


class Food(SquareObject):
    def __init__(self, x: float, y: float, value: float = 10, size: float = 3.0,
                 color: pygame.Color = pygame.Color(125, 125, 125)):
        super().__init__(x, y, size, color, 0, name='food')
        self.value = value
