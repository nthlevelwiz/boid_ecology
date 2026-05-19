"""Entry point for boid_evolution simulation."""

from __future__ import annotations

import pygame

from settings import SimulationSettings
from world import World


def main() -> None:
    pygame.init()
    settings = SimulationSettings()

    screen = pygame.display.set_mode((settings.width, settings.height))
    pygame.display.set_caption("boid_evolution")
    clock = pygame.time.Clock()

    world = World(settings)
    running = True
    paused = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    world = World(settings)
                elif event.key == pygame.K_UP:
                    settings.plant_spawn_rate += 1
                elif event.key == pygame.K_DOWN:
                    settings.plant_spawn_rate = max(0, settings.plant_spawn_rate - 1)
                elif event.key == pygame.K_v:
                    settings.show_vision_debug = not settings.show_vision_debug
                elif event.key == pygame.K_s:
                    settings.show_stats_overlay = not settings.show_stats_overlay

        if not paused:
            world.update()

        world.draw(screen)
        pygame.display.flip()
        clock.tick(settings.fps)

    pygame.quit()


if __name__ == "__main__":
    main()
