import pygame
import random
import auxiliary
from brain import Brain
from dna import BrainDNA, DNA
from math import cos, pi, sin, atan2, fmod
import logging
import numpy as np
import sys

# logging.basicConfig(level=logging.DEBUG)
# logs to std err and overwrites (each execution) file out.log
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG,
                    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(filename='out.log', mode='w')])

logger = logging.getLogger(__name__)


class CreatureIdGenerator:
    def __init__(self):
        self.creature_id_inc_counter = 0

    def get_next_id(self):
        self.creature_id_inc_counter += 1
        return self.creature_id_inc_counter


# create singleton creature id generator
creature_id_generator = CreatureIdGenerator()


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
        self.creatures.append(creature)  # comment back
        self.creature_total += 1

    def add_edible(self, food):
        self.edibles.append(food)

    def generate_random_creature(self):
        return BrainCreature(x=random.uniform(0, self.width), y=random.uniform(0, self.height), dna=DNA(),
                             brain_dna=BrainDNA(), name='Creature ' + str(creature_id_generator.get_next_id()))

    def remove_creature(self, creature):
        creature.log("died")
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

            # random death:
            if random.random() <= creature.death_rate * dt / 1000:
                self.remove_creature(creature)

            elif creature.health > 0:
                creature.draw(self.screen)
            else:
                self.remove_creature(creature)

        font = pygame.font.Font('freesansbold.ttf', 14)
        text = font.render(f"# of creatures: {len(self.creatures)}", True, (255, 255, 255), (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (100, 50)
        self.screen.blit(text, text_rect)

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

    def log(self, info: str):
        # pass
        logger.debug(self.name + ": " + info)


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
    # base_health = 300
    base_health = 20000
    # multiply_delay = 10 ** 4
    multiply_delay = 2 * (10 ** 4)
    death_rate = 0.01  # possibility of random death
    direction_change_delay = 500

    def __init__(self, x: float, y: float, size: float, speed: float, color: pygame.Color,
                 direction: float = 0.0, vision_radius: int = 100, name: str = 'object_x',
                 multiply_chance=(0.25, 0.05)):
        super().__init__(x, y, size, color, direction, name=name)
        self.log("creature created")
        self.speed = speed
        self.health = self.base_health
        self.log(f"health init: {self.health}")
        self.multiply_chance = multiply_chance

        self.multiply_cd = self.multiply_delay
        self.direction_change_cd = self.direction_change_delay

        # self.vision_radius = 100
        self.vision_radius = vision_radius
        self.log(f"vision radius: {self.vision_radius}")
        # self.vision_radius = 300
        self.detection_chance = 1000
        self.vision_rect = pygame.Rect(self.x + self.vision_radius, self.y + self.vision_radius,
                                       self.vision_radius * 2, self.vision_radius * 2)

        # auxiliary attributes
        self.dx = 0.0
        self.dy = 0.0
        self.x_acc = 0.0
        self.y_acc = 0.0

    def can_change_direction(self):
        return self.direction_change_cd <= 0

    def can_multiply(self) -> bool:
        return self.multiply_cd <= 0

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        color = pygame.Color(255, 255, 255)

        pygame.draw.rect(surface, self.color, self.vision_rect, 1)

        a = pygame.math.Vector2(self.x, self.y)
        b = pygame.math.Vector2(self.x - self.size * cos(self.direction),
                                self.y - self.size * sin(self.direction))
        pygame.draw.line(surface, color, a, b)
        font = pygame.font.Font('freesansbold.ttf', 12)
        if self.can_multiply():
            text = font.render("fertile", True, (0, 255, 0), (0, 0, 0))
        else:
            text = font.render(str(self.multiply_cd // 1000), True, (255, 0, 0), (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (self.x, self.y)
        surface.blit(text, text_rect)

        # print health
        health_ratio = self.health / self.base_health
        if health_ratio > 1:
            health_ratio = 1
        r = int(255 - (255 * health_ratio))
        g = int(255 * health_ratio)
        b = 0
        health_text = font.render(f"h: {round(health_ratio * 100, 2)}%", True, (r, g, b), (0, 0, 0))
        health_text_rect = health_text.get_rect()
        health_text_rect.center = (self.x, self.y + 15)
        surface.blit(health_text, health_text_rect)

        dx_text = font.render(f"dx: {round(self.dx, 2)}", True, (255, 255, 255), (0, 0, 0))
        dx_text_rect = dx_text.get_rect()
        dx_text_rect.center = (self.x, self.y + 30)
        surface.blit(dx_text, dx_text_rect)

        dy_text = font.render(f"dy: {round(self.dy, 2)}", True, (255, 255, 255), (0, 0, 0))
        dy_text_rect = dx_text.get_rect()
        dy_text_rect.center = (self.x, self.y + 45)
        surface.blit(dy_text, dy_text_rect)

        # position output
        """
        x_text = font.render(f"x: {round(self.x, 2)}", True, (255, 255, 255), (0, 0, 0))
        x_text_rect = x_text.get_rect()
        x_text_rect.center = (self.x, self.y + 60)
        surface.blit(x_text, x_text_rect)

        y_text = font.render(f"y: {round(self.y, 2)}", True, (255, 255, 255), (0, 0, 0))
        y_text_rect = y_text.get_rect()
        y_text_rect.center = (self.x, self.y + 75)
        surface.blit(y_text, y_text_rect)
        """

    """
    def find_target(self, world: World, dt) -> SquareObject:
        min_food_dist = 100000 # just some number larger than the world
        closest_food = None
        for edible in world.edibles:
            if self.vision_rect.colliderect(edible.rect):
                dist = ((self.x - edible.x) ** 2 + (self.y - edible.y) ** 2) ** 0.5
                if dist < min_food_dist:
                    min_food_dist = dist
                    closest = edible
        #if closest_food:
        #    return closest_food

        closest_creature = None
        min_creature_dist = 100000 # just some number larger than the world
        for creature in world.creatures:
            # if creature != self and self.rect.colliderect(creature.rect):
            if creature != self and self.vision_rect.colliderect(creature.rect):
                dist = ((self.x - creature.x) ** 2 + (self.y - creature.y) ** 2) ** 0.5
                if dist < min_creature_dist:
                    closest_creature = creature
                    min_creature_dist = dist
                # if random.random() < self.detection_chance * dt / 1000:
        #            return creature

        if min_food_dist < min_creature_dist:
            return closest_food
        elif creature:
            return creature
        else:
            return None
    """

    def find_target(self, world: World, dt) -> SquareObject:
        for edible in world.edibles:
            if self.vision_rect.colliderect(edible.rect):
                return edible

        for creature in world.creatures:
            # if creature != self and self.rect.colliderect(creature.rect):
            if creature != self and self.vision_rect.colliderect(creature.rect):
                # if random.random() < self.detection_chance * dt / 1000:
                return creature

        return None

    def multiply(self) -> 'Creature':
        self.multiply_cd = self.multiply_delay
        size = random.uniform(self.size * 0.9, self.size * 1.1)
        return Creature(self.x, self.y, size, speed=random.uniform(self.speed * 0.9, self.speed * 1.1),
                        color=self.color, direction=fmod(self.direction + pi, 2 * pi), name=self.name,
                        multiply_chance=self.multiply_chance)

    def sexual_multiply(self, partner):
        return self.multiply()

    def asexual_multiply(self):
        return self.multiply()

    def update_health(self, dt):
        # self.health -= (self.speed ** 1.1) * (self.size ** 1.1) * dt * 0.0005
        # self.health -= (self.speed ** 1.1) * (self.size ** 1.1) * dt * 0.000005
        self.health -= ((self.size ** 3) * (self.speed ** 2) + self.vision_radius) * dt * 0.0000005  # primer-like
        # print(f"delta health: {(self.size ** 3) * (self.speed ** 2) * dt }")

    def update_direction_change_cd(self, dt):
        self.direction_change_cd = max(0, self.direction_change_cd - dt)

    def update_multiply_cd(self, dt):
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

                    # bigger creatures can it smaller creatures if their size is at least 20% the size of the smaller one
                    # ? add successful hunt probability?
                    # if (self.size ** 2) >= 1.4 * (creature.size ** 2):
                    #     self.health += 0.0001 * creature.health
                    #     world.remove_creature(creature)

            """   
            # asexual reproduction
            if random.random() < self.multiply_chance[1] * dt / 1000:
                world.add_creature(self.asexual_multiply())
            """

    def get_velocity(self, dt):

        self.dx = self.speed / 50 * cos(self.direction) * dt
        self.dy = self.speed / 50 * sin(self.direction) * dt
        vel_x = self.dx + self.x_acc
        vel_y = self.dy + self.y_acc
        # self.log(f"velocity: x: {vel_x}, y: {vel_y}")

        self.x_acc = vel_x - int(vel_x)
        vel_x = int(vel_x)

        self.y_acc = vel_y - int(vel_y)
        vel_y = int(vel_y)

        return vel_x, vel_y

    def do_movement(self, world: World, dt: float):
        direction_changed = False
        if self.can_change_direction():
            target = self.find_target(world, dt)
            if target:
                self.log("found target %s" % target.name)
                if isinstance(target, Food) or (self.can_multiply() and target.can_multiply()):
                    self.direction = atan2(target.y - self.y, target.x - self.x)
                else:
                    self.direction = atan2(target.x - self.x, target.y - self.y)
                direction_changed = True

        vel_x, vel_y = self.get_velocity(dt)
        new_rect = self.rect.move(vel_x, vel_y)

        bounds = world.screen.get_rect()
        if not bounds.contains(new_rect):
            if self.can_change_direction():
                self.direction = fmod(self.direction + random.uniform(0, pi), (2 * pi))
                vel_x, vel_y = self.get_velocity(dt)
                new_rect = self.rect.move(vel_x, vel_y)
                direction_changed = True
            new_rect = new_rect.clamp(bounds)

        if direction_changed:
            self.direction_change_cd = self.direction_change_delay

        return new_rect

    def tick(self, world: World, dt: float):
        new_rect = self.do_movement(world, dt)

        for edible in world.edibles:
            if self.rect.colliderect(edible.rect):
                self.log(f"found food with value: {edible.value}")
                self.health += edible.value
                world.remove_edible(edible)

        self.creature_interaction(world, dt)

        self.update_direction_change_cd(dt)
        self.update_multiply_cd(dt)
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

    min_vision_radius = 50.0
    max_vision_radius = 150.0

    def __init__(self, x: float, y: float, dna=DNA(), direction: float = 0.0, name: str = 'object'):
        color = pygame.Color(int(dna.genes[0] * 255), int(dna.genes[1] * 255), int(dna.genes[2] * 255))
        speed = auxiliary.map(dna.genes[3], 0, 1, self.min_speed, self.max_speed)
        size = auxiliary.map(dna.genes[4], 0, 1, self.min_size, self.max_size)
        multiply_chance = (auxiliary.map(dna.genes[5], 0, 1, self.min_s_multiply, self.max_s_multiply),
                           auxiliary.map(dna.genes[5], 0, 1, self.max_a_multiply, self.min_a_multiply))
        vision_radius = auxiliary.map(dna.genes[6], 0, 1, size, self.max_vision_radius)
        super().__init__(x, y, size, speed, color, direction, vision_radius, name=name, multiply_chance=multiply_chance)
        self.dna = dna

        self.log("creature created")
        self.log(f"health dna creature: {self.health}")

        # neural network parameters

    # reproduction comes with a cost

    def get_repro_dna(self, partner: 'DnaCreature' = None) -> DNA:
        if partner:
            dna = self.dna.crossover(partner.dna)
        else:
            dna = self.dna.copy()

        dna.mutation()
        return dna

    def asexual_multiply(self):
        self.health -= 0.01 * self.health
        self.multiply_cd = self.multiply_delay

        dna = self.get_repro_dna()

        self.log("produced child via asexual reproduction")
        return DnaCreature(self.x, self.y, dna=dna, direction=fmod(self.direction + pi, (2 * pi)), name=self.name)

    def sexual_multiply(self, partner: 'DnaCreature') -> 'DnaCreature':
        self.health -= 0.15 * self.health
        partner.health -= 0.15 * partner.health
        self.multiply_cd = self.multiply_delay

        child_dna = self.get_repro_dna(partner)

        self.log("produced child with %s via sexual reproduction" % partner.name)

        return DnaCreature(self.x, self.y, dna=child_dna, direction=fmod((self.direction + pi), (2 * pi)), name=self.name)


class BrainCreature(DnaCreature):
    def __init__(self, x: float, y: float, dna: DNA = DNA(), brain_dna: DNA = BrainDNA(), direction: float = 0.0,
                 name: str = 'object'):
        super().__init__(x, y, dna, direction, name)
        self.brain = Brain(brain_dna)

    def get_brain_repro_dna(self, partner: 'BrainCreature' = None) -> BrainDNA:
        if partner:
            dna = self.brain.dna.crossover(partner.brain.dna)
        else:
            dna = self.brain.dna.copy()

        dna.mutation()
        return dna

    def asexual_multiply(self):
        # self.health -= 0.01 * self.health
        self.multiply_cd = self.multiply_delay

        dna = self.get_repro_dna()
        brain_dna = self.get_brain_repro_dna()

        return BrainCreature(self.x, self.y, dna=dna, brain_dna=brain_dna, direction=fmod(self.direction + pi, (2 * pi)),
                             name=self.name)

    def sexual_multiply(self, partner: 'DnaCreature') -> 'DnaCreature':
        # self.health -= 0.15 * self.health
        # partner.health -= 0.15 * partner.health
        self.multiply_cd = self.multiply_delay

        dna = self.get_repro_dna(partner)
        brain_dna = self.get_brain_repro_dna(partner)

        return BrainCreature(self.x, self.y, dna=dna, brain_dna=brain_dna, direction=fmod((self.direction + pi), (2 * pi)),
                             name=self.name)

    def do_movement(self, world: World, dt: float):
        direction_changed = False
        if self.can_change_direction():
            target = self.find_target(world, dt)
            neuron_input = np.zeros(Brain.input_neurons)
            neuron_input[3] = self.can_multiply()
            neuron_input[6] = self.health
            neuron_input[7] = self.multiply_cd / 1000
            if target:
                neuron_input[0] = target.x - self.x
                neuron_input[1] = target.y - self.y
                if isinstance(target, Food):
                    neuron_input[2] = 1
                    neuron_input[5] = 10
                else:
                    neuron_input[2] = -1
                    neuron_input[4] = target.can_multiply()
                    if self.size > target.size:
                        neuron_input[5] = self.size / target.size
                    else:
                        neuron_input[5] = -1 * target.size / self.size

            direction = self.brain.get_direction(neuron_input)
            direction_changed = self.direction == direction
            self.direction = direction

        vel_x, vel_y = self.get_velocity(dt)
        new_rect = self.rect.move(vel_x, vel_y)

        bounds = world.screen.get_rect()
        if not bounds.contains(new_rect):
            if self.can_change_direction():
                self.direction = fmod((self.direction + random.uniform(0, pi)), (2 * pi))
                vel_x, vel_y = self.get_velocity(dt)
                new_rect = self.rect.move(vel_x, vel_y)
                direction_changed = True
            new_rect = new_rect.clamp(bounds)

        if direction_changed:
            self.direction_change_cd = self.direction_change_delay

        return new_rect


class Food(SquareObject):
    def __init__(self, x: float, y: float, value: float = 2000, size: float = 3.0,
                 color: pygame.Color = pygame.Color(125, 125, 125)):
        super().__init__(x, y, size, color, 0, name='food')
        self.value = value
