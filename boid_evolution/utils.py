"""Utility functions for boid_evolution."""

from __future__ import annotations

import random

import numpy as np


def limit_vector(vec: np.ndarray, max_magnitude: float) -> np.ndarray:
    mag = np.linalg.norm(vec)
    if mag > max_magnitude and mag > 0:
        return vec / mag * max_magnitude
    return vec


def random_unit_vector() -> np.ndarray:
    angle = random.uniform(0, 2 * np.pi)
    return np.array([np.cos(angle), np.sin(angle)], dtype=float)


def wrap_position(position: np.ndarray, width: float, height: float) -> np.ndarray:
    return np.array([position[0] % width, position[1] % height], dtype=float)


def toroidal_offset(a: np.ndarray, b: np.ndarray, width: float, height: float) -> np.ndarray:
    """Return shortest wrapped vector from a to b in toroidal space."""
    dx = b[0] - a[0]
    dy = b[1] - a[1]

    if dx > width / 2:
        dx -= width
    elif dx < -width / 2:
        dx += width

    if dy > height / 2:
        dy -= height
    elif dy < -height / 2:
        dy += height

    return np.array([dx, dy], dtype=float)
