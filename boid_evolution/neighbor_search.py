"""Sweep-and-prune neighbor search for boids."""

from __future__ import annotations

from bisect import bisect_left
from typing import Iterable


class NeighborSearch:
    def __init__(self, world_width: float, world_height: float, wrap_edges: bool = True):
        self.world_width = world_width
        self.world_height = world_height
        self.wrap_edges = wrap_edges
        self.sorted_boids: list[object] = []
        self.sorted_x: list[float] = []
        self.sorted_by_level: dict[int, tuple[list[object], list[float]]] = {}
        self.last_stats = {
            "boids": 0,
            "queries": 0,
            "candidate_checks": 0,
            "valid_neighbors": 0,
            "max_valid_before_cap": 0,
        }

    def rebuild(self, boids: Iterable[object]) -> None:
        alive = [b for b in boids if getattr(b, "alive", True)]
        alive.sort(key=self._x_of)
        self.sorted_boids = alive
        self.sorted_x = [self._x_of(b) for b in alive]

        by_level: dict[int, list[object]] = {}
        for boid in alive:
            level = getattr(boid, "level", None)
            if level is None:
                continue
            by_level.setdefault(level, []).append(boid)

        self.sorted_by_level = {}
        for level, items in by_level.items():
            items.sort(key=self._x_of)
            self.sorted_by_level[level] = (items, [self._x_of(b) for b in items])

        self.last_stats = {
            "boids": len(alive),
            "queries": 0,
            "candidate_checks": 0,
            "valid_neighbors": 0,
            "max_valid_before_cap": 0,
        }

    def nearby_boids(self, boid, radius=None, level=None, max_neighbors=10):
        radius = boid.genome.vision_radius if radius is None else radius
        if radius <= 0:
            return []

        if level is None:
            boids = self.sorted_boids
            x_values = self.sorted_x
        else:
            level_bucket = self.sorted_by_level.get(level)
            if level_bucket is None:
                return []
            boids, x_values = level_bucket

        if not boids:
            return []

        query_x = self._x_of(boid)
        insert_idx = bisect_left(x_values, query_x)
        radius_sq = radius * radius

        seen: set[int] = set()
        valid: list[tuple[float, object]] = []
        candidate_checks = 0

        left = insert_idx - 1
        while left >= 0:
            x_diff = query_x - x_values[left]
            if x_diff > radius:
                break
            candidate = boids[left]
            candidate_checks += 1
            self._try_add_candidate(boid, candidate, radius_sq, seen, valid)
            left -= 1

        right = insert_idx
        while right < len(boids):
            x_diff = x_values[right] - query_x
            if x_diff > radius:
                break
            candidate = boids[right]
            candidate_checks += 1
            self._try_add_candidate(boid, candidate, radius_sq, seen, valid)
            right += 1

        if self.wrap_edges:
            if query_x < radius:
                i = len(boids) - 1
                while i >= 0:
                    wrap_x_diff = query_x + (self.world_width - x_values[i])
                    if wrap_x_diff > radius:
                        break
                    candidate_checks += 1
                    self._try_add_candidate(boid, boids[i], radius_sq, seen, valid)
                    i -= 1
            if self.world_width - query_x < radius:
                i = 0
                while i < len(boids):
                    wrap_x_diff = (self.world_width - query_x) + x_values[i]
                    if wrap_x_diff > radius:
                        break
                    candidate_checks += 1
                    self._try_add_candidate(boid, boids[i], radius_sq, seen, valid)
                    i += 1

        self.last_stats["queries"] += 1
        self.last_stats["candidate_checks"] += candidate_checks
        self.last_stats["valid_neighbors"] += len(valid)
        if len(valid) > self.last_stats["max_valid_before_cap"]:
            self.last_stats["max_valid_before_cap"] = len(valid)

        valid.sort(key=lambda item: item[0])
        return [other for _, other in valid[:max_neighbors]]

    def _try_add_candidate(self, boid, candidate, radius_sq, seen, valid) -> None:
        if candidate is boid:
            return
        candidate_id = id(candidate)
        if candidate_id in seen:
            return
        seen.add(candidate_id)

        dist_sq = self._dist_sq(boid, candidate)
        if dist_sq <= radius_sq:
            valid.append((dist_sq, candidate))

    def _dist_sq(self, boid_a, boid_b) -> float:
        x1, y1 = self._xy_of(boid_a)
        x2, y2 = self._xy_of(boid_b)

        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        if self.wrap_edges:
            dx = min(dx, self.world_width - dx)
            dy = min(dy, self.world_height - dy)
        return dx * dx + dy * dy

    @staticmethod
    def _xy_of(boid) -> tuple[float, float]:
        if hasattr(boid, "position"):
            return float(boid.position[0]), float(boid.position[1])
        return float(boid.x), float(boid.y)

    @classmethod
    def _x_of(cls, boid) -> float:
        if hasattr(boid, "position"):
            return float(boid.position[0])
        return float(boid.x)
