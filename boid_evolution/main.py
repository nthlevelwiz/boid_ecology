from __future__ import annotations
import json
from datetime import datetime
import pygame
from settings import EcosystemSettings, PRESETS
from world import World

PRESET_KEYS={pygame.K_1:'lush_world',pygame.K_2:'predator_pressure',pygame.K_3:'fragile_balance',pygame.K_4:'herbivore_bloom',pygame.K_5:'collapse_test'}

def main()->None:
    pygame.init(); settings=EcosystemSettings()
    screen=pygame.display.set_mode((settings.WORLD_WIDTH, settings.WORLD_HEIGHT)); clock=pygame.time.Clock(); world=World(settings)
    running=True; paused=False
    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_SPACE: paused=not paused
                elif event.key in PRESET_KEYS:
                    name=PRESET_KEYS[event.key]; settings.apply_preset(name, PRESETS[name]); world=World(settings)
                elif event.key==pygame.K_p: settings.PLANT_SPAWN_RATE += 1
                elif event.key==pygame.K_o: settings.PLANT_SPAWN_RATE=max(0,settings.PLANT_SPAWN_RATE-1)
                elif event.key==pygame.K_h: settings.RESEED_COUNTS[1]+=1
                elif event.key==pygame.K_j: settings.RESEED_COUNTS[1]=max(0,settings.RESEED_COUNTS[1]-1)
                elif event.key==pygame.K_k: settings.RESEED_COUNTS[2]+=1
                elif event.key==pygame.K_l: settings.RESEED_COUNTS[2]=max(0,settings.RESEED_COUNTS[2]-1)
                elif event.key==pygame.K_n: settings.RESEED_COUNTS[3]+=1
                elif event.key==pygame.K_m: settings.RESEED_COUNTS[3]=max(0,settings.RESEED_COUNTS[3]-1)
                elif event.key==pygame.K_z: settings.PLANT_ENERGY=max(1,settings.PLANT_ENERGY-1); settings.PREY_ENERGY_GAIN[1]=settings.PLANT_ENERGY
                elif event.key==pygame.K_x: settings.PLANT_ENERGY+=1; settings.PREY_ENERGY_GAIN[1]=settings.PLANT_ENERGY
                elif event.key==pygame.K_c: settings.PREY_ENERGY_GAIN[2]=max(1,settings.PREY_ENERGY_GAIN[2]-5); settings.PREY_ENERGY_GAIN[3]=max(1,settings.PREY_ENERGY_GAIN[3]-5)
                elif event.key==pygame.K_v: settings.PREY_ENERGY_GAIN[2]+=5; settings.PREY_ENERGY_GAIN[3]+=5
                elif event.key==pygame.K_b: settings.EXTINCTION_RESEED_ENABLED=not settings.EXTINCTION_RESEED_ENABLED
                elif event.key==pygame.K_r: world=World(settings)
                elif event.key==pygame.K_t: print(json.dumps(settings.to_dict(), indent=2))
                elif event.key==pygame.K_y: settings.save_json(f"settings_snapshot_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json")
        if not paused: world.update()
        world.draw(screen, fps=clock.get_fps()); pygame.display.flip(); clock.tick(settings.FPS)
    pygame.quit()

if __name__=='__main__': main()
