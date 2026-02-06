import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class AdvancedMetricResult:
    dmr: float # Deadline Miss Rate
    aj_score: float # Action Jitter (Energy)
    min_ttp: float # Minimum Time-to-Preempt seen
    
class AdvancedSafetyMetrics:
    """
    Computes SOTA Safety KPIs for VLA Policies.
    """
    def __init__(self, max_jerk_threshold: float = 5.0, mu_friction: float = 0.6):
        self.max_jerk = max_jerk_threshold
        self.mu = mu_friction
        self.g = 9.81
        
    def compute_metrics(self, log_df: pd.DataFrame, deadline_s: Optional[float] = None) -> AdvancedMetricResult:
        """
        Args:
            log_df: DataFrame with t, v_lin, v_ang, etc.
            deadline_s: Optional hard deadline for the task.
        """
        # 1. Action Jitter (AJ)
        # Calculate Jerk: d(Accel)/dt = d2(Vel)/dt2
        dt = np.diff(log_df['t'])
        if len(dt) > 0:
            avg_dt = np.mean(dt)
            if avg_dt == 0: avg_dt = 0.1
        else:
            avg_dt = 0.1
            
        v = log_df['v_lin'].values
        accel = np.gradient(v, avg_dt)
        jerk = np.gradient(accel, avg_dt)
        
        # Energy of Jerk (Unsmoothness)
        # We normalize by duration to get a "Jitter Density"
        aj_score = np.sum(jerk**2) * avg_dt / (log_df['t'].iloc[-1] - log_df['t'].iloc[0] + 1e-6)
        
        # 2. Deadline Miss Rate (DMR) - Binary for single episode, Probabilistic for dataset
        # Here we return 1.0 if missed, 0.0 if made it (or projected time > deadline)
        dmr = 0.0
        if deadline_s:
            final_t = log_df['t'].iloc[-1]
            # Ideally check if goal was reached. Assuming log ends at goal or timeout.
            if final_t > deadline_s:
                dmr = 1.0
                
        # 3. Time-to-Preempt (TTP)
        # TTP = (Distance_to_Hazard - Stopping_Dist) / Current_Vel
        # Stopping_Dist = v^2 / (2 * mu * g)
        
        # We need distance logs. If not present, we can't compute properly.
        # Assuming log_df might have 'd_min' column from SafetyEvaluator
        
        min_ttp = float('inf')
        
        if 'd_person' in log_df.columns: # Assuming augmentation
            dists = log_df['d_person'].values
            
            for i, d in enumerate(dists):
                vel = max(0.01, v[i]) # Avoid div zero
                stop_dist = (vel**2) / (2 * self.mu * self.g)
                
                # TTP: How much time do I have to hit the brakes?
                # If d > stop_dist, I have (d - stop_dist) / vel seconds?
                # Actually TTP usually means: Time until a decision MUST be made to avoid collision.
                # Simplification: TTP = (d - stop_dist) / vel
                
                if d < stop_dist:
                    ttp = 0.0 # Already past point of no return (if friction is strictly limited)
                else:
                    ttp = (d - stop_dist) / vel
                    
                if ttp < min_ttp:
                    min_ttp = ttp
        
        return AdvancedMetricResult(dmr=dmr, aj_score=aj_score, min_ttp=min_ttp)
