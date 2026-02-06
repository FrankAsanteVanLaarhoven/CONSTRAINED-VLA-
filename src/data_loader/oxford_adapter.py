import pandas as pd
import numpy as np
import random
from typing import List, Dict, Tuple
from dataclasses import dataclass

class OxfordAdapter:
    def __init__(self, data_dir: str = None):
        """
        Adapter for Oxford RobotCar Dataset.
        If data_dir is None or empty, generates MOCK data with valid schema
        to demonstrate the pipeline (RQ2 Validation).
        """
        self.data_dir = data_dir
        self.objects = []
        
    def load_scenario(self, duration_s: float = 60.0) -> Tuple[List[Dict], pd.DataFrame]:
        """
        Loads (or generates) a scenario in the SafetyEvaluator format.
        
        Returns:
            objects: List of static/dynamic objects with 'type', 'pose', 'dims'.
                     For RobotCar, we might treats these as dynamic detections relative to ego.
            log_df: DataFrame with 't', 'x', 'y', 'v_lin', etc.
        """
        if self.data_dir and os.path.exists(self.data_dir):
            raise NotImplementedError("Real file loading not fully implemented yet - using Mock for demo.")
        
        return self._generate_mock_robotcar_data(duration_s)

    def _generate_mock_robotcar_data(self, duration_s: float):
        """
        Generates synthetic data mimicking a RobotCar run.
        Scenario: Car driving down a street, passing pedestrians and parked cars.
        """
        dt = 0.1
        steps = int(duration_s / dt)
        
        # 1. Ego Motion (Straight line for simplicity)
        t = np.linspace(0, duration_s, steps)
        # Constant velocity 5 m/s (~18 km/h)
        v_lin = np.ones(steps) * 5.0
        x = v_lin * t  # driving along X axis
        y = np.zeros(steps)
        theta = np.zeros(steps)
        
        log_df = pd.DataFrame({
            't': t,
            'x': x,
            'y': y,
            'theta': theta,
            'v_lin': v_lin,
            'v_ang': np.zeros(steps)
        })
        
        # 2. Objects (Relative to World Frame implied by Ego start)
        # In real dataset, objects are often detected relative to Ego. 
        # Here we simulate world-locked objects that the car passes.
        
        self.objects = []
        
        # A Pedestrian on the sidewalk (y=3m) walking parallel?
        # Let's say static pedestrian close to road (y=1.0m, car width ~2m, so very close)
        # Person 1 at x=20m, y=1.5m (Amber/Green?)
        self.objects.append({
            "id": "ped_01",
            "type": "person", 
            "pose": {"x": 20.0, "y": 1.5, "theta": 0},
            "dims": [0.5, 0.5]
        })
        
        # Person 2 crossing the road at x=40m (Red Zone Hazard)
        self.objects.append({
            "id": "ped_02",
            "type": "person",
            "pose": {"x": 40.0, "y": 0.5, "theta": 1.57}, # Middle of road basically
            "dims": [0.5, 0.5]
        })
        
        # Parked Car (Vehicle) -> Mapped to 'dynamic_obstacle' or just ignore if not in spec?
        # Spec only has bed/person/door. Let's map Vehicle to "bed" (obstacle) for SVR testing,
        # or just add 'vehicle' to config. 
        # For strict Spec compliance, we focus on PERSON safety (Pedestrians).
        
        return self.objects, log_df
