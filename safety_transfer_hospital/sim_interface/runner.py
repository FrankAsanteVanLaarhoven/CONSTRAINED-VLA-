import csv
import time
import math
import os
from typing import Tuple, List, Dict, Any

class SimulationRunner:
    def __init__(self, mode: str = "mock"):
        """
        Initialize the simulation runner.
        :param mode: 'ros2' for real TurtleBot3 simulation, 'mock' for kinematic simulation.
        """
        self.mode = mode
        self.current_pose = (0.0, 0.0, 0.0) # x, y, yaw
        self.logs = [] # List of dicts

    def reset(self, start_pose: Tuple[float, float, float]):
        """Resets the robot to the start pose."""
        self.current_pose = start_pose
        self.logs = []
        if self.mode == "ros2":
            # TODO: Implement ROS2 /reset_world or set_model_state service call
            pass
        return self.current_pose

    def step(self, action: Tuple[float, float], dt: float = 0.1) -> Tuple[float, float, float]:
        """
        Executes a control command.
        :param action: (v, omega) linear and angular velocity
        :param dt: Time step duration
        :return: New pose (x, y, yaw)
        """
        v, omega = action
        x, y, yaw = self.current_pose

        if self.mode == "mock":
            # Simple Unicycle Kinematics
            x += v * math.cos(yaw) * dt
            y += v * math.sin(yaw) * dt
            yaw += omega * dt
            
            # Normalize yaw
            yaw = (yaw + math.pi) % (2 * math.pi) - math.pi
            
            self.current_pose = (x, y, yaw)
        elif self.mode == "ros2":
            # TODO: Publish /cmd_vel and wait for /odom update
            pass
            
        return self.current_pose

    def run_episode(self, policy_fn, goal_pose: Tuple[float, float], max_steps: int = 200, output_path: str = None):
        """
        Runs a full episode using the provided policy function.
        :param policy_fn: Function taking (pose, goal) -> (v, omega)
        :param goal_pose: (x, y) target
        """
        start_time = 0.0
        dt = 0.1
        
        for step in range(max_steps):
            t = start_time + step * dt
            
            # 1. Get Action from Policy
            v, omega = policy_fn(self.current_pose, goal_pose)
            
            # 2. Execute Step
            new_pose = self.step((v, omega), dt)
            
            # 3. Log Data (Sim-Truth)
            self.logs.append({
                "t": t,
                "x": new_pose[0],
                "y": new_pose[1],
                "yaw": new_pose[2],
                "v": v,
                "omega": omega
            })
            
            # Check Goal Reached (Simple Euclidean dist)
            dist_to_goal = math.hypot(new_pose[0] - goal_pose[0], new_pose[1] - goal_pose[1])
            if dist_to_goal < 0.2:
                print(f"Goal reached at step {step}!")
                break
        
        if output_path:
            self._save_logs(output_path)
            
    def _save_logs(self, output_path: str):
        if not self.logs:
            return
            
        keys = self.logs[0].keys()
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.logs)
        print(f"Saved episode logs to {output_path}")

# --- Baselines ---

def pure_pursuit_policy(pose, goal, v_max=0.2):
    """Simple baseline: turn towards goal and drive."""
    x, y, yaw = pose
    gx, gy = goal
    
    dx = gx - x
    dy = gy - y
    
    target_yaw = math.atan2(dy, dx)
    yaw_err = target_yaw - yaw
    
    # Normalize yaw error
    yaw_err = (yaw_err + math.pi) % (2 * math.pi) - math.pi
    
    # Simple P-Controller
    omega = 2.0 * yaw_err
    
    # Slow down if turning sharp
    v = v_max * max(0, 1.0 - abs(yaw_err))
    
    return v, omega
