"""Simulation settings and constants for boid_evolution."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SimulationSettings:
    # Window / world
    width: int = 1200
    height: int = 800
    fps: int = 60
    background_color: tuple[int, int, int] = (15, 18, 24)

    # Initial populations
    initial_plants: int = 220
    initial_herbivores: int = 40
    initial_predators: int = 16
    initial_apex: int = 6

    # Energy model
    starting_energy: float = 50.0
    plant_energy: float = 25.0
    prey_energy: float = 60.0
    base_metabolism: float = 0.05
    movement_cost_factor: float = 0.01
    reproduction_threshold: float = 100.0
    reproduction_cost: float = 40.0
    child_energy: float = 30.0

    # Interaction ranges
    eat_radius: float = 6.0
    attack_radius: float = 8.0

    # Plant spawning
    plant_spawn_rate: int = 3
    max_plants: int = 300

    # Lifecycle
    max_age: int = 20000
    reproduction_cooldown_ticks: int = 180

    # Drawing
    boid_base_radius: int = 4
    show_vision_debug: bool = False
    show_stats_overlay: bool = True

    # Trophic rendering colors
    level_colors: dict[int, tuple[int, int, int]] = field(
        default_factory=lambda: {
            1: (102, 204, 255),  # herbivore
            2: (255, 140, 80),   # predator
            3: (214, 86, 255),   # apex
        }
    )
    plant_color: tuple[int, int, int] = (66, 204, 84)


# Bounds used by Genome trait clamping.
GENOME_BOUNDS: dict[str, tuple[float, float]] = {
    "max_speed": (1.0, 6.0),
    "max_force": (0.02, 0.6),
    "vision_radius": (25.0, 220.0),
    "separation_weight": (0.0, 3.0),
    "alignment_weight": (0.0, 3.0),
    "cohesion_weight": (0.0, 3.0),
    "food_seek_weight": (0.0, 4.0),
    "predator_flee_weight": (0.0, 5.0),
    "prey_chase_weight": (0.0, 4.0),
    "metabolism": (0.01, 0.3),
    "reproduction_threshold": (70.0, 180.0),
    "mutation_rate": (0.005, 0.35),
}
