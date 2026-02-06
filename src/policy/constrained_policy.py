import numpy as np
import math
from dataclasses import dataclass
from typing import Tuple, Dict, List

@dataclass
class PolicyParams:
    # Standard P-Control gains
    kp_lin: float = 1.0
    kp_ang: float = 2.0
    max_v: float = 0.5
    
    # Safety Weights (Langrangian-like modulation)
    # We conceptually assume the policy learns to slow down.
    # Here we model a "learned" behavior as a safety gain 'k_safe'
    # v_cmd = v_nominal * (1 - exp(-k_safe * dist_to_hazard))
    # If k_safe is high, we don't slow down until very close (aggressive)
    # If k_safe is low, we slow down early (conservative)
    k_safe_bed: float = 5.0
    k_safe_person: float = 5.0
    
class LagrangianOptimizer:
    def __init__(self, target_cost: float = 0.05, lr: float = 0.1):
        """
        Adapts lambda to keep cost <= target_cost.
        target_cost: e.g. 0.05 (5% SVR allowed? Or 0?)
        """
        self.lambda_val = 0.0
        self.target_cost = target_cost
        self.lr = lr
        
    def update(self, current_cost: float):
        # Lambda update: lambda = max(0, lambda + lr * (cost - target))
        # Logic: If cost > target, lambda increases (punish unsafety more).
        # If cost < target, lambda decreases (care less about safety).
        self.lambda_val = max(0.0, self.lambda_val + self.lr * (current_cost - self.target_cost))
        return self.lambda_val

class ConstrainedPolicy:
    def __init__(self, params: PolicyParams = None):
        if params is None:
            self.params = PolicyParams()
        else:
            self.params = params
            
    def get_action(self, robot_state, goal_pose, nearest_dists: Dict[str, float]) -> Tuple[float, float]:
        """
        Returns (v_lin, v_ang).
        nearest_dists: {'bed': d, 'person': d, ...}
        """
        rx, ry, rt = robot_state.x, robot_state.y, robot_state.theta
        gx, gy, gt = goal_pose
        
        # 1. Nominal P-Control
        dx = gx - rx
        dy = gy - ry
        dist = math.sqrt(dx**2 + dy**2)
        target_ang = math.atan2(dy, dx)
        ang_diff = target_ang - rt
        while ang_diff > math.pi: ang_diff -= 2*math.pi
        while ang_diff < -math.pi: ang_diff += 2*math.pi
        
        v_lin = min(self.params.max_v, dist * self.params.kp_lin)
        v_ang = ang_diff * self.params.kp_ang
        v_ang = max(-1.0, min(1.0, v_ang))
        
        # 2. Safety Modulation (The component optimized by Lagrangian)
        # We look at the "Safety Cost Field"
        # safety_factor = product( 1 - exp(-k * d) ) ??
        # Let's use min() logic
        
        # Bed Factor
        d_bed = nearest_dists.get('bed', float('inf'))
        # Simple barrier-like function: 
        # If dist large, factor ~ 1. If dist -> 0, factor -> 0.
        # k_safe controls how steep the drop is.
        # factor = 1 - exp(-k * d) is good. 0 at d=0, 1 at inf.
        factor_bed = 1.0 - math.exp(-self.params.k_safe_bed * d_bed)
        
        # Person Factor
        d_person = nearest_dists.get('person', float('inf'))
        factor_person = 1.0 - math.exp(-self.params.k_safe_person * d_person)
        
        # Final Safety Factor (conservative: take min)
        safety_factor = min(factor_bed, factor_person)
        # Clamp to [0, 1] just in case
        safety_factor = max(0.0, min(1.0, safety_factor))
        
        # Modulate Linear Velocity
        v_lin = v_lin * safety_factor
        
        return v_lin, v_ang
        
    def update_params(self, lambda_val: float):
        """
        'Training' Step (Heuristic Gradient simulation for V0.1).
        
        In a real CMDP RL, the policy gradient would adjust weights.
        Here, we simulate the effect of the Lagrangian on the 'k_safe' parameters.
        
        Objective: Minimize ( -TaskReward + Lambda * SafetyCost )
        
        If Lambda is high (unsafe):
           We need to LOWER cost (get safer).
           This means INCREASING k_safe ?? 
           Wait, let's check the maths.
           factor = 1 - exp(-k * d).
           If k=100, exp(-100d) ~ 0 -> factor=1 -> Fast -> Unsafe.
           If k=0.1, exp(-0.1d) ~ 1 -> factor=0 -> Stop -> Safe.
           
           So to be safer, we need k_safe to DECREASE.
           
           Update Rule Heuristic:
           k_safe_new = k_safe_old - alpha * lambda_val * gradient_heuristic
           
        If Lambda is low (safe enough):
           We want to maximize R (go fast).
           We can INCREASE k_safe.
           
        """
        # Heuristic update
        # Descent step on k_safe
        # We want to increase k if lambda is low (safe enough, go faster)
        # We want to decrease k if lambda is high (unsafe, slow down)
        
        learning_rate = 0.1
        
        # "Gradient" of Task Reward w.r.t k is positive (higher k = faster = more reward)
        grad_R = 1.0 
        
        # "Gradient" of Safety Cost w.r.t k is positive (higher k = closer calls = higher cost)
        grad_C = 1.0
        
        # Net Gradient descent direction for Loss = -R + lambda*C
        # dL/dk = -1 + lambda * 1
        # update: k = k - lr * dL/dk = k - lr * (lambda - 1)
        # = k + lr * (1 - lambda)
        
        delta = learning_rate * (1.0 - lambda_val * 5.0) # Scaling factor for lambda impact
        
        self.params.k_safe_bed = max(0.1, self.params.k_safe_bed + delta)
        self.params.k_safe_person = max(0.1, self.params.k_safe_person + delta)
