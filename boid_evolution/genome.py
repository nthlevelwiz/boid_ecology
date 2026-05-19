"""Genome class: inherited traits, randomization, mutation, and clamping."""

from __future__ import annotations

from dataclasses import dataclass
import random

from settings import GENOME_BOUNDS, SimulationSettings


@dataclass
class Genome:
    max_speed: float
    max_force: float
    vision_radius: float
    separation_weight: float
    alignment_weight: float
    cohesion_weight: float
    food_seek_weight: float
    predator_flee_weight: float
    prey_chase_weight: float
    metabolism: float
    reproduction_threshold: float
    mutation_rate: float

    @classmethod
    def random_genome(cls, settings: SimulationSettings) -> "Genome":
        return cls(
            max_speed=random.uniform(1.8, 3.5),
            max_force=random.uniform(0.08, 0.22),
            vision_radius=random.uniform(60.0, 130.0),
            separation_weight=random.uniform(0.6, 1.8),
            alignment_weight=random.uniform(0.4, 1.6),
            cohesion_weight=random.uniform(0.3, 1.4),
            food_seek_weight=random.uniform(1.0, 2.6),
            predator_flee_weight=random.uniform(1.2, 2.8),
            prey_chase_weight=random.uniform(0.8, 2.4),
            metabolism=max(settings.BASE_METABOLISM, random.uniform(0.03, 0.12)),
            reproduction_threshold=max(
                settings.reproduction_threshold_for_level(1) * 0.75,
                random.uniform(80.0, 130.0),
            ),
            mutation_rate=random.uniform(0.03, 0.12),
        ).clamped()

    def mutated_copy(self) -> "Genome":
        values = self.__dict__.copy()
        for trait_name, value in values.items():
            if random.random() < self.mutation_rate:
                delta_ratio = random.uniform(-0.2, 0.2)
                values[trait_name] = value * (1.0 + delta_ratio)

        # mutation rate itself mutates more gently
        if random.random() < self.mutation_rate:
            values["mutation_rate"] = self.mutation_rate + random.uniform(-0.02, 0.02)

        return Genome(**values).clamped()

    def clamped(self) -> "Genome":
        values = self.__dict__.copy()
        for trait_name, (low, high) in GENOME_BOUNDS.items():
            values[trait_name] = max(low, min(high, values[trait_name]))
        return Genome(**values)
