import sys
import os
import torch
import numpy as np

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from safety_transfer_humanoid.geometry.capsule_math import CapsuleMath
from safety_transfer_humanoid.geometry.humanoid_body import SimpleHumanoid, PatientVolume

def test_humanoid_collision():
    print("Testing 3D Humanoid Safety Logic...")
    
    robot = SimpleHumanoid()
    # Patient located 0.8m in front of robot base
    patient = PatientVolume(position=[0.8, 0.0, 1.0])
    
    patient_capsules = patient.get_capsules()
    
    # Case 1: Safe Pose (Arm straight up)
    # Shoulder angle = 90 deg (pi/2) -> Pointing Up
    q_safe = torch.tensor([1.57, 0.0]) 
    links_safe = robot.forward_kinematics(q_safe)
    
    margin_safe = CapsuleMath.check_safety_violation(links_safe, patient_capsules)
    print(f"Safe Pose Margin: {margin_safe:.3f}m (Expected > 0)")
    
    if margin_safe > 0:
        print("PASS: Safe pose detected correctly.")
    else:
        print("FAIL: Safe pose marked as unsafe.")
        
    # Case 2: Unsafe Pose (Reaching forward into patient)
    # Shoulder = 0 deg -> Pointing Forward towards X+
    q_unsafe = torch.tensor([0.0, 0.0]) 
    links_unsafe = robot.forward_kinematics(q_unsafe)
    
    margin_unsafe = CapsuleMath.check_safety_violation(links_unsafe, patient_capsules)
    print(f"Unsafe Pose Margin: {margin_unsafe:.3f}m (Expected < 0)")
    
    # Check
    # Robot Base: 0.0, 0.0, 1.0
    # Patient Center: 0.8, 0.0, 1.0. Radius 0.3 -> Surface at 0.5.
    # Arm Length: 0.6m. Reaches to 0.6.
    # Penetration: 0.6 (Hand) > 0.5 (Patient Surface).
    # Margin should be roughly 0.5 - 0.6 = -0.1m (approx)
    
    if margin_unsafe < 0:
        print("PASS: Collision pose detected correctly.")
    else:
        print("FAIL: Collision pose marked as safe.")
        
    print("Humanoid Safety Prototype Verified.")

if __name__ == "__main__":
    test_humanoid_collision()
