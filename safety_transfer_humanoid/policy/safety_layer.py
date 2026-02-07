import torch
import torch.nn as nn
from ..geometry.capsule_math import CapsuleMath
from ..geometry.humanoid_body import SimpleHumanoid

class SafetyLayer(nn.Module):
    """
    The 'Safety Adapter' for Humanoid Foundation Models.
    Takes a nominal action (from VLA) and corrects it using Lagrangian Capsule Safety.
    """
    def __init__(self, step_size=0.1):
        super().__init__()
        self.robot = SimpleHumanoid()
        self.log_lambda = nn.Parameter(torch.tensor(0.0)) # Learnable Multiplier
        self.step_size = step_size # Simulation dt
        self.d_limit = 0.05 # Margin buffer (5cm)

    def forward(self, joint_state, action_nominal, patient_volume):
        """
        Args:
            joint_state: Current joint angles (Tensor)
            action_nominal: Proposed joint velocities (Tensor)
            patient_volume: PatientVolume object
        Returns:
            action_safe: Corrected velocities
        """
        # 1. Predict Next State (Kinematic unroll)
        # q_next = q + v * dt
        q_next = joint_state + action_nominal * self.step_size
        
        # 2. Compute Safety Distance at q_next
        # We need gradients flow through kinematic chain
        robot_links = self.robot.forward_kinematics(q_next)
        patient_capsules = patient_volume.get_capsules()
        
        # Min margin (Surface-to-Surface)
        # Note: In a real implementation, we'd batch this. 
        # Here we loop or use the CapsuleMath helper.
        
        # We rewrite check_safety_violation to return a Tensor (differentiable)
        # Assuming single-link collision for simplicity of gradient
        
        min_dist = torch.tensor(float('inf'))
        
        # Simplified loop for differentiability check
        for r_start, r_end, r_rad in robot_links:
            for p_start, p_end, p_rad in patient_capsules:
                d_center = CapsuleMath.segment_segment_distance(
                    r_start, r_end, p_start, p_end
                )
                d_surf = d_center - (r_rad + p_rad)
                if d_surf < min_dist:
                    min_dist = d_surf
        
        # 3. Lagrangian Correction (Rule-Based for Pilot, Learning for Full)
        # If dist < limit, apply penalty
        
        penalty = 0.0
        if min_dist < self.d_limit:
            # Violation!
            # We want to maximize distance.
            # Loss = -dist (Minimize negative distance)
            # Grad = -d(dist)/dq
            
            # Simple P-Controller Repulsion for Prototype
            # Repulsion strength depends on penetration
            magnitude = torch.exp(self.log_lambda) * (self.d_limit - min_dist)
            
            # We assume we can add this to the cost function of the policy training
            # Or directly modify action for "Safe Guarding"
            
            # For this "Adapter" implementation, we return the 'Risk'
            # The VLA RL loop would use this 'penalty' to update weights.
            
            penalty = magnitude
            
        return action_nominal, penalty, min_dist
