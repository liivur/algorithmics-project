import pygame
import random
import auxiliary
from dna import DNA
from math import cos, pi, sin, atan2


# ? monitor number of creatures in the world

class World:
    def __init__(self, width: int = 640, height: int = 480, background: tuple = (0, 0, 0),
                 creatures: list = [], edibles: list = [], food_spawn_interval: int = 1000,
                 creature_spawn_interval: int = 10000, random_spawning: bool = True, max_creatures: int = 100):
        pygame.init()
        self.size = self.width, self.height = width, height
        self.background = background
        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        self.random_spawning = random_spawning
        self.max_creatures = max_creatures

        self.food_spawn_counter = 0
        self.food_spawn_interval = food_spawn_interval
        self.edibles = edibles

        self.creature_spawn_counter = 0
        self.creature_spawn_interval = creature_spawn_interval
        self.creatures = creatures

        self.creature_total = len(creatures)

    def add_creature(self, creature):
        # sanity check so the computer doesn't crash with bad params
        if len(self.creatures) > self.max_creatures:
            pass
        # self.creatures.append(creature)
        self.creature_total += 1

    def add_edible(self, food):
        self.edibles.append(food)

    def generate_random_creature(self):
        color = pygame.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        gene = [random.uniform(0, 1), color.r / 255, color.g / 255, color.b / 255]
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
        if self.random_spawning:
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
    multiply_delay = 10**4

    def __init__(self, x: float, y: float, size: float, speed: float, color: pygame.Color,
                 direction: float = 0.0, name: str = 'object', multiply_chance=(0.25, 0.05)):
        super().__init__(x, y, size, color, direction, name=name)
        self.speed = speed
        self.health = self.base_health
        self.multiply_chance = multiply_chance

        self.multiply_cd = self.multiply_delay

        self.vision_radius = 100
        self.detection_chance = 0.25
        self.vision_rect = pygame.Rect(self.x + self.vision_radius, self.y + self.vision_radius,
                                       self.vision_radius * 2, self.vision_radius * 2)

    def can_multiply(self) -> bool:
        return self.multiply_cd <= 0

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        color = pygame.Color(255, 255, 255)
        a = pygame.math.Vector2(self.x, self.y)
        b = pygame.math.Vector2(self.x - self.size * sin(self.direction),
                                self.y - self.size * cos(self.direction))
        pygame.draw.line(surface, color, a, b)
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render(str(self.multiply_cd // 1000), True, (255, 0, 0), (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (self.x, self.y)
        surface.blit(text, text_rect)

    def find_target(self, world: World, dt) -> SquareObject:
        for edible in world.edibles:
            if self.vision_rect.colliderect(edible.rect):
                return edible

        for creature in world.creatures:
            if creature != self and self.rect.colliderect(creature.rect):
                if random.random() < self.detection_chance * dt / 1000:
                    return creature

        return None

    def multiply(self) -> 'Creature':
        self.multiply_cd = self.multiply_delay
        size = random.uniform(self.size * 0.9, self.size * 1.1)
        return Creature(self.x, self.y, size, speed=random.uniform(self.speed * 0.9, self.speed * 1.1),
                        color=self.color, direction=(self.direction + pi) % (2 * pi), name=self.name,
                        multiply_chance=self.multiply_chance)

    def sexual_multiply(self, partner):
        return self.multiply()

    def asexual_multiply(self):
        return self.multiply()

    def update_health(self, dt):
        # self.health -= (self.speed ** 1.1) * (self.size ** 1.1) * dt * 0.0005
        self.health -= (self.speed ** 1.1) * (self.size ** 1.1) * dt * 0.000005

    def update_multiply(self, dt):
        self.multiply_cd = max(0, self.multiply_cd - dt)

    def update_rect(self, rect: pygame.Rect):
        self.rect = rect
        self.x = rect.centerx
        self.y = rect.centery
        self.vision_rect.center = rect.center

    def creature_interaction(self, world: World, dt):
        if self.can_multiply():
            # creature interaction
            for creature in world.creatures:
                if creature != self and self.rect.colliderect(creature.rect):
                    # sexual reproduction
                    if random.random() < self.multiply_chance[0] * dt / 1000:
                        child = self.sexual_multiply(creature)
                        world.add_creature(child)

            # asexual reproduction
            if random.random() < self.multiply_chance[1] * dt / 1000:
                world.add_creature(self.asexual_multiply())

    def get_velocity(self, dt):
        vel_x = self.speed / 50 * sin(self.direction) * dt
        vel_y = self.speed / 50 * cos(self.direction) * dt

        return vel_x, vel_y

    def tick(self, world: World, dt: float):
        target = self.find_target(world, dt)
        if target:
            if isinstance(target, Food) or (self.can_multiply() and target.can_multiply()):
                self.direction = atan2(target.y - self.y, target.x - self.x)
            else:
                self.direction = atan2(target.x - self.x, target.y - self.y)

        vel_x, vel_y = self.get_velocity(dt)
        new_rect = self.rect.move(vel_x, vel_y)

        bounds = world.screen.get_rect()
        if not bounds.contains(new_rect):
            self.direction = (self.direction + random.uniform(0, pi)) % (2 * pi)
            vel_x, vel_y = self.get_velocity(dt)
            new_rect = self.rect.move(vel_x, vel_y).clamp(bounds)
            # new_rect = self.rect.clamp(bounds)

        for edible in world.edibles:
            if self.rect.colliderect(edible.rect):
                self.health += edible.value
                world.remove_edible(edible)

        self.creature_interaction(world, dt)

        self.update_multiply(dt)
        self.update_health(dt)
        self.update_rect(new_rect)


class DnaCreature(Creature):
    min_size = 1.0
    max_size = 50.0
    min_speed = 1.0
    max_speed = 5.0
    min_a_multiply = 0
    max_a_multiply = 0.05
    min_s_multiply = 0
    max_s_multiply = 0.25

    def __init__(self, x: float, y: float, dna=DNA(), direction: float = 0.0, name: str = 'object'):
        color = pygame.Color(int(dna.genes[0] * 255), int(dna.genes[1] * 255), int(dna.genes[2] * 255))
        speed = auxiliary.map(dna.genes[3], 0, 1, self.min_speed, self.max_speed)
        size = auxiliary.map(dna.genes[4], 0, 1, self.min_size, self.max_size)
        multiply_chance = (auxiliary.map(dna.genes[5], 0, 1, self.min_s_multiply, self.max_s_multiply),
                           auxiliary.map(dna.genes[5], 0, 1, self.max_a_multiply, self.min_a_multiply))
        super().__init__(x, y, size, speed, color, direction, name=name, multiply_chance=multiply_chance)
        self.dna = dna

    def asexual_multiply(self):
        self.multiply_cd = self.multiply_delay
        dna = self.dna.copy()
        dna.mutation()
        print("a child is born via asexual reproduction")
        return DnaCreature(self.x, self.y, dna=dna, direction=(self.direction + pi) % (2 * pi), name=self.name)

    def sexual_multiply(self, partner: 'DnaCreature') -> 'DnaCreature':
        self.multiply_cd = self.multiply_delay

        child_dna = self.dna.crossover(partner.dna)
        child_dna.mutation()
        print("a child is born via sexual reproduction")

        return DnaCreature(self.x, self.y, dna=child_dna, direction=(self.direction + pi) % (2 * pi), name=self.name)


class Food(SquareObject):
    def __init__(self, x: float, y: float, value: float = 30.0, size: float = 3.0,
                 color: pygame.Color = pygame.Color(125, 125, 125)):
        super().__init__(x, y, size, color, 0, name='food')
        self.value = value
