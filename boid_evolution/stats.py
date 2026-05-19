"""Simulation statistics tracking and rendering helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pygame


@dataclass
class SimulationStats:
    births_per_level: dict[int, int] = field(default_factory=lambda: {1: 0, 2: 0, 3: 0})
    deaths_per_level: dict[int, int] = field(default_factory=lambda: {1: 0, 2: 0, 3: 0})
    death_causes: dict[str, int] = field(default_factory=lambda: {"starvation": 0, "predation": 0, "old_age": 0})
    extinction_events: dict[int, int] = field(default_factory=lambda: {1: 0, 2: 0, 3: 0})
    prev_populations: dict[int, int] = field(default_factory=lambda: {1: 0, 2: 0, 3: 0})

    def record_birth(self, level: int) -> None:
        self.births_per_level[level] += 1

    def record_death(self, level: int, cause: str) -> None:
        self.deaths_per_level[level] += 1
        self.death_causes[cause] = self.death_causes.get(cause, 0) + 1

    def compute_level_stats(self, boids: list[Any]) -> dict[int, dict[str, float]]:
        level_stats: dict[int, dict[str, float]] = {}
        trait_names = (
            "max_speed",
            "max_force",
            "vision_radius",
            "metabolism",
            "reproduction_threshold",
            "mutation_rate",
        )

        for level in (1, 2, 3):
            level_boids = [b for b in boids if b.alive and b.level == level]
            population = len(level_boids)
            avg_energy = sum(b.energy for b in level_boids) / population if population else 0.0

            trait_avgs = {}
            for t in trait_names:
                trait_avgs[t] = (
                    sum(getattr(b.genome, t) for b in level_boids) / population if population else 0.0
                )

            level_stats[level] = {
                "population": population,
                "avg_energy": avg_energy,
                **{f"trait_{k}": v for k, v in trait_avgs.items()},
            }

            if self.prev_populations[level] > 0 and population == 0:
                self.extinction_events[level] += 1
            self.prev_populations[level] = population

        return level_stats

    def draw_overlay(self, surface: pygame.Surface, level_stats: dict[int, dict[str, float]], plant_count: int) -> None:
        font = pygame.font.SysFont("consolas", 18)
        lines = [
            f"Plants: {plant_count}",
            f"L1 pop/birth/death: {int(level_stats[1]['population'])}/{self.births_per_level[1]}/{self.deaths_per_level[1]}",
            f"L2 pop/birth/death: {int(level_stats[2]['population'])}/{self.births_per_level[2]}/{self.deaths_per_level[2]}",
            f"L3 pop/birth/death: {int(level_stats[3]['population'])}/{self.births_per_level[3]}/{self.deaths_per_level[3]}",
            f"Avg energy L1/L2/L3: {level_stats[1]['avg_energy']:.1f} / {level_stats[2]['avg_energy']:.1f} / {level_stats[3]['avg_energy']:.1f}",
            f"Deaths by cause S/P/O: {self.death_causes.get('starvation',0)}/{self.death_causes.get('predation',0)}/{self.death_causes.get('old_age',0)}",
            f"Extinctions L1/L2/L3: {self.extinction_events[1]}/{self.extinction_events[2]}/{self.extinction_events[3]}",
        ]

        y = 10
        for line in lines:
            text = font.render(line, True, (230, 230, 230))
            surface.blit(text, (10, y))
            y += 22
