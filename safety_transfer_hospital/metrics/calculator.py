import pandas as pd
import numpy as np
import json
import math
from typing import Dict, List, Any
from ..world_gen.schema import ObjectType, SAFETY_STANDARDS

class MetricsCalculator:
    def __init__(self, world_objects_path: str):
        with open(world_objects_path, 'r') as f:
            self.objects_data = json.load(f)
            
        # Group objects by type for efficient distance checking
        self.objects_by_type = {
            ObjectType.BED: [],
            ObjectType.PERSON: [],
            ObjectType.DOOR: []
        }
        
        for obj in self.objects_data:
            o_type = ObjectType(obj['type'])
            if o_type in self.objects_by_type:
                self.objects_by_type[o_type].append(obj)

    def compute_distances(self, log_df: pd.DataFrame) -> pd.DataFrame:
        """
        Computes minimum distance to each object type for every timestep.
        Returns a DataFrame with columns: [t, d_bed, d_person, d_door]
        """
        results = []
        
        for _, row in log_df.iterrows():
            rx, ry = row['x'], row['y']
            
            step_res = {'t': row['t']}
            
            for o_type, obj_list in self.objects_by_type.items():
                min_dist = float('inf')
                
                if not obj_list:
                    step_res[f"d_{o_type.value}"] = float('inf')
                    continue
                    
                for obj in obj_list:
                    # Simple point-to-point distance (ignoring object size for Q1 prototype)
                    # Year 2 TODO: Update to polygon distance
                    ox, oy = obj['x'], obj['y']
                    dist = math.hypot(rx - ox, ry - oy)
                    if dist < min_dist:
                        min_dist = dist
                
                step_res[f"d_{o_type.value}"] = min_dist
                
            results.append(step_res)
            
        return pd.DataFrame(results)

    def label_safety_zones(self, dist_df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies d_warn/d_crit thresholds to label frames as Green/Amber/Red.
        Returns DataFrame with zone labels per type.
        """
        labels = dist_df.copy()
        
        for o_type in [ObjectType.BED, ObjectType.PERSON, ObjectType.DOOR]:
            col_name = f"d_{o_type.value}"
            zone_col = f"zone_{o_type.value}"
            
            thresholds = SAFETY_STANDARDS[o_type]
            
            def get_zone(d):
                if d < thresholds.d_crit:
                    return "RED"
                elif d < thresholds.d_warn:
                    return "AMBER"
                else:
                    return "GREEN"
            
            labels[zone_col] = labels[col_name].apply(get_zone)
            
        return labels

    def compute_episode_metrics(self, labeled_df: pd.DataFrame) -> Dict[str, float]:
        """
        Aggregates metrics for the episode.
        """
        total_steps = len(labeled_df)
        if total_steps == 0:
            return {}
            
        metrics = {}
        
        # SVR: Any Red Zone violation
        # A timestep is non-compliant if ANY object type is in RED
        is_red = (labeled_df['zone_bed'] == 'RED') | \
                 (labeled_df['zone_person'] == 'RED') | \
                 (labeled_df['zone_door'] == 'RED')
                 
        metrics['SVR'] = is_red.sum() / total_steps
        
        # NVT: Amber zone while moving (assume v > 0.05 from logs if available, else just time in amber)
        # Simplified: Fraction of time in AMBER (and not RED)
        is_amber = ((labeled_df['zone_bed'] == 'AMBER') | \
                   (labeled_df['zone_person'] == 'AMBER') | \
                   (labeled_df['zone_door'] == 'AMBER')) & (~is_red)
                   
        metrics['NVT'] = is_amber.sum() / total_steps
        
        # Min Distances
        metrics['min_dist_person'] = labeled_df['d_person'].min()
        metrics['min_dist_bed'] = labeled_df['d_bed'].min()
        
        return metrics
