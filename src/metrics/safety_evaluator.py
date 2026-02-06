import numpy as np
import math
import pandas as pd
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class SafetyConfig:
    # {object_type: {'crit': float, 'warn': float}}
    thresholds: Dict[str, Dict[str, float]]

class SafetyEvaluator:
    def __init__(self, objects: List[Dict], config: SafetyConfig = None):
        """
        Args:
            objects: List of object dicts [{'type', 'pose': {'x', 'y' ...}, 'dims': ...}]
            config: Thresholds for safety zones
        """
        self.objects = objects
        if config is None:
            # Default from BENCHMARK_SPEC.md
            self.config = SafetyConfig(thresholds={
                "bed": {"crit": 0.4, "warn": 0.8},
                "person": {"crit": 0.5, "warn": 1.2},
                "door": {"crit": 0.3, "warn": 0.6}
            })
        else:
            self.config = config

    def evaluate_episode(self, log_df: pd.DataFrame) -> Dict:
        """
        Evaluates a full episode log.
        Returns a dictionary of aggregated metrics and a detailed DataFrame with per-step zones.
        """
        results = []
        
        total_steps = len(log_df)
        red_steps = 0
        amber_steps_moving = 0
        min_dists = {"bed": float('inf'), "person": float('inf'), "door": float('inf')}
        
        dt_est = 0.1 # Estimate if not available, or derive from t
        
        step_details = []

        for idx, row in log_df.iterrows():
            rx, ry = row['x'], row['y']
            
            # Distance to nearest of each type
            d_nearest = {"bed": float('inf'), "person": float('inf'), "door": float('inf')}
            
            # Check all objects
            # Optimization: could use KD-tree, but N is small (<50)
            for obj in self.objects:
                otype = obj['type']
                if otype not in d_nearest: continue
                
                ox, oy = obj['pose']['x'], obj['pose']['y']
                # Simple point distance for now (Project Spec Phase 1)
                # Ideally box distance, but point-to-point is acceptable for now if radii are large enough
                dist = math.sqrt((rx - ox)**2 + (ry - oy)**2)
                
                # Subtract approximate robot radius? 
                # Spec says "distance from robot center" implicitly unless specified.
                # Let's stick to center-to-center for simple ground truth, 
                # or center-to-object-center. 
                # BENCHMARK_SPEC says "d_i(t) = distance(Robot, O_i)".
                
                if dist < d_nearest[otype]:
                    d_nearest[otype] = dist
            
            # Determine Zone
            # Green (0), Amber (1), Red (2)
            # We track the worst zone across all types
            current_status = "green"
            
            in_red = False
            in_amber = False
            
            for otype, dist in d_nearest.items():
                min_dists[otype] = min(min_dists[otype], dist)
                
                thresholds = self.config.thresholds.get(otype)
                if not thresholds: continue
                
                if dist < thresholds['crit']:
                    in_red = True
                    current_status = "red"
                elif dist < thresholds['warn'] and not in_red:
                    in_amber = True
                    if current_status != "red":
                        current_status = "amber"
            
            # Aggregation
            if in_red:
                red_steps += 1
            
            if in_amber:
                # Check if moving
                v_lin = row['v_lin']
                if abs(v_lin) > 0.05: # moving
                    amber_steps_moving += 1
            
            step_details.append({
                "t": row['t'],
                "status": current_status,
                "d_bed": d_nearest['bed'],
                "d_person": d_nearest['person'],
                "d_door": d_nearest['door']
            })

        # Final Metrics
        svr = red_steps / total_steps if total_steps > 0 else 0.0
        # NVT: Duration in amber moving. Assuming ~constant dt or summing differences
        # Let's simple sum steps * dt (assuming 0.1 from logging)
        # Better: use actual time
        nvt_duration = 0.0
        # Implement precise time integration if needed, simple count for now suited for spec v0.1
        
        metrics = {
            "SVR": svr,
            "Red_Steps": red_steps,
            "Amber_Moving_Steps": amber_steps_moving,
            "Min_Dist_Person": min_dists['person'],
            "Min_Dist_Bed": min_dists['bed'],
            "Total_Steps": total_steps
        }
        
        return metrics, pd.DataFrame(step_details)
