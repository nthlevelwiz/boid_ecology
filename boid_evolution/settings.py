"""Simulation settings and constants for boid_evolution."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
import json
from pathlib import Path
from typing import Any


@dataclass
class EcosystemSettings:
    # Window / world
    WORLD_WIDTH: int = 1200
    WORLD_HEIGHT: int = 800
    FPS: int = 60
    BACKGROUND_COLOR: tuple[int, int, int] = (15, 18, 24)

    # Initial populations
    INITIAL_PLANTS: int = 250
    INITIAL_HERBIVORES: int = 80
    INITIAL_PREDATORS: int = 25
    INITIAL_APEX_PREDATORS: int = 8

    # Energy / ecology
    PLANT_ENERGY: float = 25.0
    MAX_PLANTS: int = 500
    PLANT_SPAWN_RATE: int = 3
    HERBIVORE_START_ENERGY: float = 50.0
    PREDATOR_START_ENERGY: float = 70.0
    APEX_START_ENERGY: float = 90.0

    HERBIVORE_METABOLISM_MULTIPLIER: float = 1.0
    PREDATOR_METABOLISM_MULTIPLIER: float = 1.4
    APEX_METABOLISM_MULTIPLIER: float = 1.8

    HERBIVORE_REPRODUCTION_THRESHOLD: float = 100.0
    PREDATOR_REPRODUCTION_THRESHOLD: float = 140.0
    APEX_REPRODUCTION_THRESHOLD: float = 180.0

    HERBIVORE_REPRODUCTION_COST: float = 40.0
    PREDATOR_REPRODUCTION_COST: float = 65.0
    APEX_REPRODUCTION_COST: float = 90.0

    HERBIVORE_CHILD_ENERGY: float = 30.0
    PREDATOR_CHILD_ENERGY: float = 45.0
    APEX_CHILD_ENERGY: float = 60.0

    PREY_ENERGY_GAIN: dict[int, float] = field(default_factory=lambda: {1: 25.0, 2: 70.0, 3: 110.0})
    MAX_AGE_BY_LEVEL: dict[int, int] = field(default_factory=lambda: {1: 3000, 2: 4000, 3: 5000})
    MUTATION_RATE_BY_LEVEL: dict[int, float] = field(default_factory=lambda: {1: 0.05, 2: 0.04, 3: 0.03})

    EXTINCTION_RESEED_ENABLED: bool = True
    EXTINCTION_RESEED_DELAY: int = 600
    RESEED_COUNTS: dict[int, int] = field(default_factory=lambda: {1: 30, 2: 8, 3: 3})

    # Mechanics
    BASE_METABOLISM: float = 0.05
    MOVEMENT_COST_FACTOR: float = 0.01
    REPRODUCTION_COOLDOWN_TICKS: int = 180
    EAT_RADIUS: float = 6.0
    ATTACK_RADIUS: float = 8.0

    # Drawing
    BOID_BASE_RADIUS: int = 4
    SHOW_VISION_DEBUG: bool = False
    SHOW_STATS_OVERLAY: bool = True
    LEVEL_COLORS: dict[int, tuple[int, int, int]] = field(default_factory=lambda: {1: (102, 204, 255), 2: (255, 140, 80), 3: (214, 86, 255)})
    PLANT_COLOR: tuple[int, int, int] = (66, 204, 84)
    CURRENT_PRESET: str = "default"

    def with_updates(self, **kwargs: Any) -> "EcosystemSettings":
        return replace(self, **kwargs)

    def apply_preset(self, name: str, preset: dict[str, Any]) -> None:
        for key, value in preset.items():
            setattr(self, key, value)
        self.CURRENT_PRESET = name
        self.PREY_ENERGY_GAIN[1] = float(self.PLANT_ENERGY)

    def save_json(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    # Level helpers
    def start_energy_for_level(self, level: int) -> float:
        return {1: self.HERBIVORE_START_ENERGY, 2: self.PREDATOR_START_ENERGY, 3: self.APEX_START_ENERGY}[level]

    def reproduction_threshold_for_level(self, level: int) -> float:
        return {1: self.HERBIVORE_REPRODUCTION_THRESHOLD, 2: self.PREDATOR_REPRODUCTION_THRESHOLD, 3: self.APEX_REPRODUCTION_THRESHOLD}[level]

    def reproduction_cost_for_level(self, level: int) -> float:
        return {1: self.HERBIVORE_REPRODUCTION_COST, 2: self.PREDATOR_REPRODUCTION_COST, 3: self.APEX_REPRODUCTION_COST}[level]

    def child_energy_for_level(self, level: int) -> float:
        return {1: self.HERBIVORE_CHILD_ENERGY, 2: self.PREDATOR_CHILD_ENERGY, 3: self.APEX_CHILD_ENERGY}[level]

    def metabolism_multiplier_for_level(self, level: int) -> float:
        return {1: self.HERBIVORE_METABOLISM_MULTIPLIER, 2: self.PREDATOR_METABOLISM_MULTIPLIER, 3: self.APEX_METABOLISM_MULTIPLIER}[level]


PRESETS: dict[str, dict[str, Any]] = {
    "lush_world": {"INITIAL_PLANTS": 500, "MAX_PLANTS": 900, "PLANT_SPAWN_RATE": 6, "INITIAL_HERBIVORES": 120, "INITIAL_PREDATORS": 20, "INITIAL_APEX_PREDATORS": 4},
    "predator_pressure": {"INITIAL_PLANTS": 350, "MAX_PLANTS": 600, "PLANT_SPAWN_RATE": 4, "INITIAL_HERBIVORES": 120, "INITIAL_PREDATORS": 45, "INITIAL_APEX_PREDATORS": 10},
    "fragile_balance": {"INITIAL_PLANTS": 250, "MAX_PLANTS": 450, "PLANT_SPAWN_RATE": 2, "INITIAL_HERBIVORES": 70, "INITIAL_PREDATORS": 18, "INITIAL_APEX_PREDATORS": 5},
    "herbivore_bloom": {"INITIAL_PLANTS": 700, "MAX_PLANTS": 1000, "PLANT_SPAWN_RATE": 7, "INITIAL_HERBIVORES": 180, "INITIAL_PREDATORS": 12, "INITIAL_APEX_PREDATORS": 2},
    "collapse_test": {"INITIAL_PLANTS": 180, "MAX_PLANTS": 300, "PLANT_SPAWN_RATE": 1, "INITIAL_HERBIVORES": 100, "INITIAL_PREDATORS": 40, "INITIAL_APEX_PREDATORS": 15},
}

SimulationSettings = EcosystemSettings

GENOME_BOUNDS: dict[str, tuple[float, float]] = {
    "max_speed": (1.0, 6.0), "max_force": (0.02, 0.6), "vision_radius": (25.0, 220.0),
    "separation_weight": (0.0, 3.0), "alignment_weight": (0.0, 3.0), "cohesion_weight": (0.0, 3.0),
    "food_seek_weight": (0.0, 4.0), "predator_flee_weight": (0.0, 5.0), "prey_chase_weight": (0.0, 4.0),
    "metabolism": (0.01, 0.3), "reproduction_threshold": (70.0, 260.0), "mutation_rate": (0.005, 0.35),
}
