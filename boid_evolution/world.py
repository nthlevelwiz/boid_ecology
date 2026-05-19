"""World orchestration: entities, updates, interactions, drawing."""

from __future__ import annotations

import random

import numpy as np
import pygame

from boid import Boid
from plant import Plant
from settings import SimulationSettings
from stats import SimulationStats
from utils import toroidal_offset


class World:
    def __init__(self, settings: SimulationSettings):
        self.settings = settings
        self.stats = SimulationStats()
        self.plants: list[Plant] = []
        self.boids: list[Boid] = []
        self.reset()

    def reset(self) -> None:
        self.plants = [self._spawn_plant() for _ in range(self.settings.initial_plants)]
        self.boids = []

        for _ in range(self.settings.initial_herbivores):
            b = Boid.random_boid(level=1, settings=self.settings)
            self.boids.append(b)
            self.stats.record_birth(1)

        for _ in range(self.settings.initial_predators):
            b = Boid.random_boid(level=2, settings=self.settings)
            self.boids.append(b)
            self.stats.record_birth(2)

        for _ in range(self.settings.initial_apex):
            b = Boid.random_boid(level=3, settings=self.settings)
            self.boids.append(b)
            self.stats.record_birth(3)

    def _spawn_plant(self) -> Plant:
        pos = np.array(
            [random.uniform(0, self.settings.width), random.uniform(0, self.settings.height)], dtype=float
        )
        return Plant(position=pos, energy_value=self.settings.plant_energy)

    def spawn_plants(self) -> None:
        for _ in range(self.settings.plant_spawn_rate):
            if len(self.plants) >= self.settings.max_plants:
                break
            self.plants.append(self._spawn_plant())

    def update(self) -> None:
        self.spawn_plants()

        for boid in self.boids:
            boid.update(self)

        self.handle_plant_consumption()
        self.handle_predation()
        self.handle_reproduction()
        self.remove_dead_boids()

    def handle_plant_consumption(self) -> None:
        remaining_plants: list[Plant] = []
        for plant in self.plants:
            eaten = False
            for boid in self.boids:
                if not boid.alive or boid.level != 1:
                    continue
                dist = np.linalg.norm(
                    toroidal_offset(boid.position, plant.position, self.settings.width, self.settings.height)
                )
                if dist < self.settings.eat_radius:
                    boid.energy += plant.energy_value
                    eaten = True
                    break
            if not eaten:
                remaining_plants.append(plant)
        self.plants = remaining_plants

    def handle_predation(self) -> None:
        for predator in self.boids:
            if not predator.alive or predator.level not in (2, 3):
                continue
            target_level = predator.level - 1

            for prey in self.boids:
                if not prey.alive or prey.level != target_level:
                    continue
                dist = np.linalg.norm(
                    toroidal_offset(predator.position, prey.position, self.settings.width, self.settings.height)
                )
                if dist < self.settings.attack_radius:
                    prey.die("predation", self)
                    predator.energy += self.settings.prey_energy
                    break

    def handle_reproduction(self) -> None:
        children: list[Boid] = []
        for boid in self.boids:
            if not boid.alive:
                continue
            if (
                boid.energy >= boid.genome.reproduction_threshold
                and boid.reproduction_cooldown == 0
            ):
                child_pos = boid.position + np.random.uniform(-8.0, 8.0, size=2)
                child = Boid(
                    position=np.array([child_pos[0] % self.settings.width, child_pos[1] % self.settings.height]),
                    velocity=np.copy(boid.velocity) * 0.5,
                    acceleration=np.zeros(2, dtype=float),
                    energy=self.settings.child_energy,
                    age=0,
                    level=boid.level,
                    genome=boid.genome.mutated_copy(),
                    reproduction_cooldown=self.settings.reproduction_cooldown_ticks,
                )
                boid.energy -= self.settings.reproduction_cost
                boid.reproduction_cooldown = self.settings.reproduction_cooldown_ticks
                children.append(child)
                self.stats.record_birth(boid.level)
        self.boids.extend(children)

    def remove_dead_boids(self) -> None:
        self.boids = [b for b in self.boids if b.alive]

    def draw(self, surface: pygame.Surface) -> dict[int, dict[str, float]]:
        surface.fill(self.settings.background_color)

        for plant in self.plants:
            pygame.draw.circle(surface, self.settings.plant_color, plant.position.astype(int), 2)

        for boid in self.boids:
            radius = self.settings.boid_base_radius + (boid.level - 1)
            color = self.settings.level_colors[boid.level]
            pygame.draw.circle(surface, color, boid.position.astype(int), radius)

            if self.settings.show_vision_debug:
                pygame.draw.circle(
                    surface,
                    color,
                    boid.position.astype(int),
                    int(boid.genome.vision_radius),
                    1,
                )

        level_stats = self.stats.compute_level_stats(self.boids)
        if self.settings.show_stats_overlay:
            self.stats.draw_overlay(surface, level_stats, plant_count=len(self.plants))

        return level_stats
