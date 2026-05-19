from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
from statistics import mean, pvariance
from typing import Any
import pygame

ROLLING_WINDOW=1000

@dataclass
class SimulationStats:
    births_per_level: dict[int,int]=field(default_factory=lambda:{1:0,2:0,3:0})
    deaths_per_level: dict[int,int]=field(default_factory=lambda:{1:0,2:0,3:0})
    death_causes: dict[str,int]=field(default_factory=lambda:{'starvation':0,'predation':0,'old_age':0})
    extinction_events: dict[int,int]=field(default_factory=lambda:{1:0,2:0,3:0})
    prev_populations: dict[int,int]=field(default_factory=lambda:{1:0,2:0,3:0})
    population_history: dict[str,deque]=field(default_factory=lambda:{'plants':deque(maxlen=ROLLING_WINDOW),1:deque(maxlen=ROLLING_WINDOW),2:deque(maxlen=ROLLING_WINDOW),3:deque(maxlen=ROLLING_WINDOW)})
    max_plant_hits:int=0
    zero_plant_hits:int=0

    def record_birth(self, level:int)->None: self.births_per_level[level]+=1
    def record_death(self, level:int, cause:str)->None:
        self.deaths_per_level[level]+=1; self.death_causes[cause]=self.death_causes.get(cause,0)+1

    def step(self, boids:list[Any], plant_count:int, max_plants:int)->None:
        lv=self.compute_level_stats(boids)
        self.population_history['plants'].append(plant_count)
        for l in (1,2,3): self.population_history[l].append(int(lv[l]['population']))
        self.max_plant_hits += int(plant_count>=max_plants)
        self.zero_plant_hits += int(plant_count==0)

    def compute_level_stats(self, boids:list[Any])->dict[int,dict[str,float]]:
        out={}
        for level in (1,2,3):
            level_boids=[b for b in boids if b.alive and b.level==level]; pop=len(level_boids)
            out[level]={'population':pop,'avg_energy':(sum(b.energy for b in level_boids)/pop if pop else 0.0),'avg_age':(sum(b.age for b in level_boids)/pop if pop else 0.0)}
            if self.prev_populations[level]>0 and pop==0: self.extinction_events[level]+=1
            self.prev_populations[level]=pop
        return out

    def rolling_metrics(self)->dict[str,float]:
        m={f'mean_{n}':(mean(v) if v else 0.0) for n,v in [('plants',self.population_history['plants']),('herbivores',self.population_history[1]),('predators',self.population_history[2]),('apex',self.population_history[3])]}
        m.update({f'var_{k}':(pvariance(self.population_history[k]) if len(self.population_history[k])>1 else 0.0) for k in (1,2,3)})
        return m

    def equilibrium_score(self)->float:
        rm=self.rolling_metrics(); persist=min(40.0, (len(self.population_history[1])/ROLLING_WINDOW)*40.0)
        ext_penalty=10.0*sum(self.extinction_events.values()); explosion=0.0
        if rm['mean_herbivores']>200: explosion += (rm['mean_herbivores']-200)/4
        collapse=0.0
        if rm['mean_plants']<20: collapse+=20
        if self.zero_plant_hits>10: collapse+=10
        if self.max_plant_hits>len(self.population_history['plants'])*0.6: collapse+=10
        if rm['mean_apex']>rm['mean_predators']*0.8 and rm['mean_predators']>0: explosion+=10
        score=max(0.0,min(100.0,persist+60-ext_penalty-explosion-collapse))
        return score

    def draw_overlay(self, surface:pygame.Surface, settings:Any, level_stats:dict[int,dict[str,float]], plant_count:int, fps:float)->None:
        font=pygame.font.SysFont('consolas',17); rm=self.rolling_metrics()
        lines=[f"Preset: {settings.CURRENT_PRESET}",f"Plants: {plant_count}/{settings.MAX_PLANTS} spawn:{settings.PLANT_SPAWN_RATE} energy:{settings.PLANT_ENERGY:.1f}",f"L1/L2/L3 pop: {int(level_stats[1]['population'])}/{int(level_stats[2]['population'])}/{int(level_stats[3]['population'])}",f"Births L1/L2/L3: {self.births_per_level[1]}/{self.births_per_level[2]}/{self.births_per_level[3]}",f"Deaths L1/L2/L3: {self.deaths_per_level[1]}/{self.deaths_per_level[2]}/{self.deaths_per_level[3]}",f"Deaths starvation/predation: {self.death_causes.get('starvation',0)}/{self.death_causes.get('predation',0)}",f"Avg energy L1/L2/L3: {level_stats[1]['avg_energy']:.1f}/{level_stats[2]['avg_energy']:.1f}/{level_stats[3]['avg_energy']:.1f}",f"Avg age L1/L2/L3: {level_stats[1]['avg_age']:.0f}/{level_stats[2]['avg_age']:.0f}/{level_stats[3]['avg_age']:.0f}",f"Mean pop P/L1/L2/L3: {rm['mean_plants']:.1f}/{rm['mean_herbivores']:.1f}/{rm['mean_predators']:.1f}/{rm['mean_apex']:.1f}",f"Extinctions L1/L2/L3: {self.extinction_events[1]}/{self.extinction_events[2]}/{self.extinction_events[3]} reseed:{settings.EXTINCTION_RESEED_ENABLED}",f"Equilibrium score: {self.equilibrium_score():.1f}",f"FPS: {fps:.1f}"]
        y=10
        for line in lines:
            surface.blit(font.render(line,True,(230,230,230)),(10,y)); y+=20
