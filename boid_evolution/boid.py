"""Boid entity with flocking, feeding, fleeing, and reproduction behavior."""

from __future__ import annotations

from dataclasses import dataclass
import random

import numpy as np

from genome import Genome
from settings import SimulationSettings
from utils import limit_vector, random_unit_vector, toroidal_offset, wrap_position


@dataclass
class Boid:
    position: np.ndarray
    velocity: np.ndarray
    acceleration: np.ndarray
    energy: float
    age: int
    level: int
    genome: Genome
    reproduction_cooldown: int
    alive: bool = True

    @classmethod
    def random_boid(cls, level: int, settings: SimulationSettings) -> "Boid":
        position = np.array(
            [random.uniform(0, settings.width), random.uniform(0, settings.height)], dtype=float
        )
        velocity = random_unit_vector() * random.uniform(0.1, 1.0)
        return cls(
            position=position,
            velocity=velocity,
            acceleration=np.zeros(2, dtype=float),
            energy=settings.starting_energy,
            age=0,
            level=level,
            genome=Genome.random_genome(settings),
            reproduction_cooldown=random.randint(0, settings.reproduction_cooldown_ticks),
        )

    def apply_force(self, force: np.ndarray) -> None:
        self.acceleration += force

    def steer_toward(self, target_direction: np.ndarray) -> np.ndarray:
        if np.linalg.norm(target_direction) == 0:
            return np.zeros(2, dtype=float)
        desired = target_direction / np.linalg.norm(target_direction) * self.genome.max_speed
        steer = desired - self.velocity
        return limit_vector(steer, self.genome.max_force)

    def update(self, world: "World") -> None:
        if not self.alive:
            return

        self.age += 1
        self.reproduction_cooldown = max(0, self.reproduction_cooldown - 1)

        flock_force = self.flock(world)
        food_force = self.seek_food(world)
        flee_force = self.flee_predators(world)
        chase_force = self.chase_prey(world)

        self.apply_force(flock_force)
        self.apply_force(food_force * self.genome.food_seek_weight)
        self.apply_force(flee_force * self.genome.predator_flee_weight)
        self.apply_force(chase_force * self.genome.prey_chase_weight)

        self.acceleration = limit_vector(self.acceleration, self.genome.max_force * 3.0)
        self.velocity += self.acceleration
        self.velocity = limit_vector(self.velocity, self.genome.max_speed)
        self.position += self.velocity
        self.position = wrap_position(self.position, world.settings.width, world.settings.height)
        self.acceleration *= 0

        speed = np.linalg.norm(self.velocity)
        energy_loss = self.genome.metabolism + world.settings.movement_cost_factor * speed**2
        self.energy -= energy_loss

        if self.energy <= 0:
            self.die("starvation", world)
        elif self.age >= world.settings.max_age:
            self.die("old_age", world)

    def flock(self, world: "World") -> np.ndarray:
        neighbors = []
        for other in world.boids:
            if other is self or not other.alive or other.level != self.level:
                continue
            offset = toroidal_offset(self.position, other.position, world.settings.width, world.settings.height)
            dist = np.linalg.norm(offset)
            if dist < self.genome.vision_radius:
                neighbors.append((other, offset, dist))

        if not neighbors:
            return np.zeros(2, dtype=float)

        separation = np.zeros(2, dtype=float)
        alignment = np.zeros(2, dtype=float)
        cohesion = np.zeros(2, dtype=float)

        for other, offset, dist in neighbors:
            if dist > 0:
                separation -= offset / (dist * dist)
            alignment += other.velocity
            cohesion += self.position + offset

        alignment /= len(neighbors)
        cohesion = (cohesion / len(neighbors)) - self.position

        sep_force = self.steer_toward(separation) * self.genome.separation_weight
        ali_force = self.steer_toward(alignment) * self.genome.alignment_weight
        coh_force = self.steer_toward(cohesion) * self.genome.cohesion_weight

        return sep_force + ali_force + coh_force

    def seek_food(self, world: "World") -> np.ndarray:
        if self.level != 1:
            return np.zeros(2, dtype=float)

        nearest_offset = None
        nearest_dist = float("inf")
        for plant in world.plants:
            offset = toroidal_offset(self.position, plant.position, world.settings.width, world.settings.height)
            dist = np.linalg.norm(offset)
            if dist < nearest_dist and dist < self.genome.vision_radius:
                nearest_dist = dist
                nearest_offset = offset

        if nearest_offset is None:
            return np.zeros(2, dtype=float)
        return self.steer_toward(nearest_offset)

    def chase_prey(self, world: "World") -> np.ndarray:
        if self.level not in (2, 3):
            return np.zeros(2, dtype=float)

        target_level = self.level - 1
        return self._seek_nearest_level(world, target_level)

    def flee_predators(self, world: "World") -> np.ndarray:
        if self.level >= 3:
            return np.zeros(2, dtype=float)

        predator_level = self.level + 1
        nearest = self._seek_nearest_level(world, predator_level)
        if np.linalg.norm(nearest) == 0:
            return nearest
        return -nearest

    def _seek_nearest_level(self, world: "World", level: int) -> np.ndarray:
        nearest_offset = None
        nearest_dist = float("inf")
        for other in world.boids:
            if other is self or not other.alive or other.level != level:
                continue
            offset = toroidal_offset(self.position, other.position, world.settings.width, world.settings.height)
            dist = np.linalg.norm(offset)
            if dist < nearest_dist and dist < self.genome.vision_radius:
                nearest_dist = dist
                nearest_offset = offset

        if nearest_offset is None:
            return np.zeros(2, dtype=float)
        return self.steer_toward(nearest_offset)

    def die(self, cause: str, world: "World") -> None:
        if self.alive:
            self.alive = False
            world.stats.record_death(self.level, cause)
