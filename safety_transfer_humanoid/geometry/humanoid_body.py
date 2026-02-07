import torch
import numpy as np
from .capsule_math import CapsuleMath

class SimpleHumanoid:
    """
    A simplified kinematic model of a Humanoid Robot (e.g., Unitree G1 Upper Body).
    Represented as a set of connected capsules.
    """
    def __init__(self):
        # Base location (0,0,0)
        self.base_pos = torch.tensor([0.0, 0.0, 1.0]) # Metro height
        
        # Link lengths
        self.l_upper = 0.3
        self.l_lower = 0.3
        self.l_hand = 0.1
        
        # Link Radii (thickness)
        self.radius = 0.05

    def forward_kinematics(self, joint_angles):
        """
        Computes link capsules given joint angles [shoulder_pitch, shoulder_roll, elbow_flex].
        Returns list of (start, end, radius) tuples.
        """
        # Simplified FK for prototype testing (Planar-ish for clarity)
        # q[0]: Shoulder Pitch
        # q[1]: Elbow Flex
        
        q = joint_angles
        
        # Shoulder Joint Position
        p_shoulder = self.base_pos
        
        # Elbow Position
        p_elbow = p_shoulder + torch.tensor([
            self.l_upper * torch.cos(q[0]),
            0.0, 
            self.l_upper * torch.sin(q[0])
        ])
        
        # Wrist Position
        p_wrist = p_elbow + torch.tensor([
            self.l_lower * torch.cos(q[0] + q[1]),
            0.0,
            self.l_lower * torch.sin(q[0] + q[1])
        ])
        
        # Define Capsules
        links = [
            (p_shoulder, p_elbow, self.radius), # Upper Arm
            (p_elbow, p_wrist, self.radius)     # Forearm
        ]
        
        return links

class PatientVolume:
    """
    Represents the Human Patient as a set of Safety Capsules.
    """
    def __init__(self, position):
        self.pos = torch.tensor(position) # Center of patient
        
    def get_capsules(self):
        """
        Returns list of (start, end, radius) for patient body parts.
        """
        # Torso/Head Capsule (Vertical)
        # Lying in bed: Horizontal capsule
        
        head = self.pos + torch.tensor([-0.4, 0.0, 0.0])
        feet = self.pos + torch.tensor([0.4, 0.0, 0.0])
        
        # Critical Radius (0.3m skin distance)
        radius = 0.3 
        
        return [(head, feet, radius)]
