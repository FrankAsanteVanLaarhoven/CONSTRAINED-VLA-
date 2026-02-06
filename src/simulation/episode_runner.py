import time
import math
import csv
import os
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class RobotState:
    t: float
    x: float
    y: float
    theta: float
    v_lin: float
    v_ang: float

class EpisodeRunner:
    def __init__(self, world_config: Dict, mode: str = "mock"):
        """
        Args:
            world_config: Dict from HospitalGenerator.to_dict()
            mode: 'mock' for kinematic sim, 'ros2' for real Nav2
        """
        self.world_config = world_config
        self.mode = mode
        self.trajectory: List[RobotState] = []
        
    def run_episode(self, start_pose: Tuple[float, float, float], 
                    goal_pose: Tuple[float, float, float], 
                    duration: float = 30.0,
                    dt: float = 0.1):
        """
        Runs a single navigation episode.
        """
        self.trajectory = []
        
        if self.mode == "mock":
            self._run_mock_episode(start_pose, goal_pose, duration, dt)
        else:
            raise NotImplementedError("ROS 2 mode not yet implemented")
            
        return self.trajectory

    def _run_mock_episode(self, start, goal, duration, dt):
        """
        Simulates a robot driving to the goal with simple P-controller physics.
        Does NOT avoid obstacles (that's for the 'real' planner), but
        allows us to test the metric pipeline.
        """
        sx, sy, st = start
        gx, gy, gt = goal
        
        x, y, theta = sx, sy, st
        
        t = 0.0
        while t < duration:
            # Simple P-Control to goal
            dx = gx - x
            dy = gy - y
            dist = math.sqrt(dx**2 + dy**2)
            
            if dist < 0.2: # Reached goal
                break
                
            desired_theta = math.atan2(dy, dx)
            angle_diff = desired_theta - theta
            # Normalize angle
            while angle_diff > math.pi: angle_diff -= 2*math.pi
            while angle_diff < -math.pi: angle_diff += 2*math.pi
            
            # Kinematics
            v_lin = min(0.5, dist) # Max speed 0.5 m/s
            v_ang = 2.0 * angle_diff # P-gain for turn
            v_ang = max(-1.0, min(1.0, v_ang)) # Clamp angular vel
            
            # Update Pose
            x += v_lin * math.cos(theta) * dt
            y += v_lin * math.sin(theta) * dt
            theta += v_ang * dt
            
            self.trajectory.append(RobotState(t, x, y, theta, v_lin, v_ang))
            t += dt

    def save_log(self, filepath: str):
        """Saves trajectory to CSV."""
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['t', 'x', 'y', 'theta', 'v_lin', 'v_ang'])
            for s in self.trajectory:
                writer.writerow([f"{s.t:.3f}", f"{s.x:.3f}", f"{s.y:.3f}", 
                                 f"{s.theta:.3f}", f"{s.v_lin:.3f}", f"{s.v_ang:.3f}"])
