from __future__ import annotations
import random
import numpy as np
import pygame
from boid import Boid
from plant import Plant
from neighbor_search import NeighborSearch
from settings import EcosystemSettings
from stats import SimulationStats
from utils import toroidal_offset

class World:
    def __init__(self, settings: EcosystemSettings):
        self.settings = settings
        self.stats = SimulationStats()
        self.plants=[]
        self.boids=[]
        self.neighbor_search = NeighborSearch(settings.WORLD_WIDTH, settings.WORLD_HEIGHT, wrap_edges=True)
        self.frames_since_extinction={1:0,2:0,3:0}
        self.reset()

    def reset(self)->None:
        self.stats = SimulationStats()
        self.plants=[self._spawn_plant() for _ in range(self.settings.INITIAL_PLANTS)]
        self.boids=[]
        for lvl,count in ((1,self.settings.INITIAL_HERBIVORES),(2,self.settings.INITIAL_PREDATORS),(3,self.settings.INITIAL_APEX_PREDATORS)):
            for _ in range(count):
                self.boids.append(Boid.random_boid(level=lvl, settings=self.settings))
                self.stats.record_birth(lvl)

    def _spawn_plant(self)->Plant:
        pos=np.array([random.uniform(0,self.settings.WORLD_WIDTH),random.uniform(0,self.settings.WORLD_HEIGHT)],dtype=float)
        return Plant(position=pos, energy_value=self.settings.PLANT_ENERGY)

    def spawn_plants(self)->None:
        for _ in range(self.settings.PLANT_SPAWN_RATE):
            if len(self.plants)>=self.settings.MAX_PLANTS: break
            self.plants.append(self._spawn_plant())

    def _extinction_reseed(self)->None:
        if not self.settings.EXTINCTION_RESEED_ENABLED: return
        pops={lvl:sum(1 for b in self.boids if b.alive and b.level==lvl) for lvl in (1,2,3)}
        for lvl,pop in pops.items():
            self.frames_since_extinction[lvl]=self.frames_since_extinction[lvl]+1 if pop==0 else 0
            if self.frames_since_extinction[lvl]>=self.settings.EXTINCTION_RESEED_DELAY:
                for _ in range(self.settings.RESEED_COUNTS.get(lvl,0)):
                    self.boids.append(Boid.random_boid(level=lvl, settings=self.settings))
                    self.stats.record_birth(lvl)
                self.frames_since_extinction[lvl]=0

    def update(self)->None:
        self.spawn_plants(); self.neighbor_search.rebuild(self.boids)
        for boid in self.boids: boid.update(self)
        self.handle_plant_consumption(); self.handle_predation(); self.handle_reproduction(); self.remove_dead_boids(); self._extinction_reseed()
        self.stats.step(self.boids, len(self.plants), self.settings.MAX_PLANTS)

    def handle_plant_consumption(self)->None:
        remaining=[]
        for plant in self.plants:
            eaten=False
            for boid in self.boids:
                if not boid.alive or boid.level!=1: continue
                dist=np.linalg.norm(toroidal_offset(boid.position, plant.position, self.settings.WORLD_WIDTH, self.settings.WORLD_HEIGHT))
                if dist<self.settings.EAT_RADIUS:
                    boid.energy += plant.energy_value; eaten=True; break
            if not eaten: remaining.append(plant)
        self.plants=remaining

    def handle_predation(self)->None:
        for predator in self.boids:
            if not predator.alive or predator.level not in (2,3): continue
            target_level=predator.level-1
            for prey in self.boids:
                if not prey.alive or prey.level!=target_level: continue
                dist=np.linalg.norm(toroidal_offset(predator.position, prey.position, self.settings.WORLD_WIDTH, self.settings.WORLD_HEIGHT))
                if dist<self.settings.ATTACK_RADIUS:
                    prey.die('predation', self); predator.energy += self.settings.PREY_ENERGY_GAIN.get(predator.level,70); break

    def handle_reproduction(self)->None:
        children=[]
        for boid in self.boids:
            if not boid.alive: continue
            if boid.energy>=self.settings.reproduction_threshold_for_level(boid.level) and boid.reproduction_cooldown==0:
                child_pos=boid.position+np.random.uniform(-8.0,8.0,size=2)
                child=Boid(position=np.array([child_pos[0]%self.settings.WORLD_WIDTH, child_pos[1]%self.settings.WORLD_HEIGHT]), velocity=np.copy(boid.velocity)*0.5, acceleration=np.zeros(2,dtype=float), energy=self.settings.child_energy_for_level(boid.level), age=0, level=boid.level, genome=boid.genome.mutated_copy(), reproduction_cooldown=self.settings.REPRODUCTION_COOLDOWN_TICKS)
                boid.energy -= self.settings.reproduction_cost_for_level(boid.level)
                boid.reproduction_cooldown=self.settings.REPRODUCTION_COOLDOWN_TICKS
                children.append(child); self.stats.record_birth(boid.level)
        self.boids.extend(children)

    def remove_dead_boids(self)->None:
        self.boids=[b for b in self.boids if b.alive]

    def draw(self, surface: pygame.Surface, fps: float=0.0):
        surface.fill(self.settings.BACKGROUND_COLOR)
        for plant in self.plants: pygame.draw.circle(surface, self.settings.PLANT_COLOR, plant.position.astype(int), 2)
        for boid in self.boids:
            pygame.draw.circle(surface, self.settings.LEVEL_COLORS[boid.level], boid.position.astype(int), self.settings.BOID_BASE_RADIUS+(boid.level-1))
        level_stats=self.stats.compute_level_stats(self.boids)
        if self.settings.SHOW_STATS_OVERLAY:
            self.stats.draw_overlay(surface, self.settings, level_stats, len(self.plants), fps)
        return level_stats
