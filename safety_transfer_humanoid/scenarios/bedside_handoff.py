import torch
import numpy as np
import sys
import os

# Path hack for prototype
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from safety_transfer_humanoid.policy.safety_layer import SafetyLayer
from safety_transfer_humanoid.geometry.capsule_math import CapsuleMath
from safety_transfer_humanoid.geometry.humanoid_body import SimpleHumanoid, PatientVolume

def run_bedside_handoff():
    print("=== Scenario: Bedside Handoff (Unitree G1) ===")
    
    # Setup
    safety_adapter = SafetyLayer(step_size=0.1)
    patient = PatientVolume(position=[0.8, 0.0, 1.0]) # Patient further away (Matches Unit Test)
    
    # Robot State
    # Start with arm up (Safe)
    q = torch.tensor([1.57, 0.0]) 
    
    # Nominal Action (Unsafe): Move arm down and forward FAST
    # This simulates a VLA trying to reach a goal "through" the patient
    # Shoulder velocity = -1.0 rad/s (Down), Elbow = 0.0
    action_nominal = torch.tensor([-2.0, 0.0]) 
    
    print(f"Initial State: q={q.numpy()}")
    print(f"User Command (Nominal): {action_nominal.numpy()}")
    
    # Simulation Loop
    print("\n--- Running Trajectory ---")
    print(f"{'Step':<5} | {'Margin (m)':<12} | {'Correction':<12}")
    
    for t in range(10):
        # 1. Apply Safety Layer
        # It predicts if 'action_nominal' leads to collision
        # And returns a penalty/correction
        
        # Note: In a full RL implementation, this returns a gradient.
        # Here, for the mock, we simulate the "Clamping" effect.
        # If penalty > 0, we brake.
        
        _, penalty, _ = safety_adapter(q, action_nominal, patient)
        
        # Heuristic Correction (Simulating the Optimizer)
        # If penalty is high, we stop/reverse the unsafe joint
        action_safe = action_nominal.clone()
        if penalty > 0:
            # Simple "Stop" reflex for prototype
            # In real Lagr-RL, this would be -grad(Safety)
            action_safe[0] *= 0.1 # Slow down shoulder
            correction_str = "BRAKING"
        else:
            correction_str = "None"
            
        # 2. Step Dynamics
        q = q + action_safe * 0.1
        
        # 3. Check ACTUAL Safety margin of new pose
        links = safety_adapter.robot.forward_kinematics(q)
        actual_margin = CapsuleMath.check_safety_violation(links, patient.get_capsules())
        
        print(f"{t:<5} | {float(actual_margin):<12.3f} | {correction_str:<12}")
        
    print("\n--- Result ---")
    if float(actual_margin) > 0:
        print("SUCCESS: Adapter prevented collision (Actual Margin > 0).")
    else:
        print(f"FAILURE: Collision occurred (Margin={actual_margin:.3f}).")

if __name__ == "__main__":
    run_bedside_handoff()
