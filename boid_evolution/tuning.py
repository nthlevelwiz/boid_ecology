from __future__ import annotations
import csv
from itertools import product
from settings import EcosystemSettings
from world import World

def run_parameter_sweep(base_settings:EcosystemSettings, variations:dict[str,list], steps_per_run:int=5000, csv_path:str='parameter_sweep_results.csv'):
    keys=list(variations.keys()); results=[]
    for combo in product(*(variations[k] for k in keys)):
        s=EcosystemSettings(**base_settings.to_dict())
        for k,v in zip(keys,combo): setattr(s,k,v)
        s.PREY_ENERGY_GAIN[1]=s.PLANT_ENERGY
        w=World(s)
        for _ in range(steps_per_run): w.update()
        rm=w.stats.rolling_metrics(); score=w.stats.equilibrium_score()
        results.append({
            'preset_name': s.CURRENT_PRESET,
            'plant_spawn_rate': s.PLANT_SPAWN_RATE,
            'max_plants': s.MAX_PLANTS,
            'plant_energy': s.PLANT_ENERGY,
            'initial_herbivores': s.INITIAL_HERBIVORES,
            'initial_predators': s.INITIAL_PREDATORS,
            'initial_apex_predators': s.INITIAL_APEX_PREDATORS,
            'mean_plants': rm['mean_plants'], 'mean_herbivores': rm['mean_herbivores'], 'mean_predators': rm['mean_predators'], 'mean_apex': rm['mean_apex'],
            'extinction_count': sum(w.stats.extinction_events.values()), 'equilibrium_score': score,
        })
    results.sort(key=lambda r:r['equilibrium_score'], reverse=True)
    if results:
        with open(csv_path,'w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f, fieldnames=list(results[0].keys())); writer.writeheader(); writer.writerows(results)
    return results
