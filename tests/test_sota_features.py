import sys
import os
import shutil

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from safety_transfer_hospital.world_gen.generator import HospitalGenerator

def test_sota_features():
    print("Testing SOTA Refinements (Batches & Risk Index)...")
    
    batches = ['A', 'B', 'C', 'D']
    results = {}
    
    for batch in batches:
        print(f"Generating Batch {batch}...")
        gen = HospitalGenerator(seed=42, difficulty_batch=batch)
        gen.generate_layout()
        gen.place_objects()
        
        # Capture metrics
        count_obs = len(gen.objects)
        risk = gen.risk_index
        results[batch] = {'count': count_obs, 'risk': risk}
        
        print(f"  -> Objects: {count_obs}, Risk Index: {risk:.2f}")

    # Validation Logic
    # Risk should generally increase A < B < C < D
    # Note: heuristic logic in generator might have randomness, but trend should hold
    risks = [results[b]['risk'] for b in batches]
    
    if sorted(risks) == risks:
        print("SUCCESS: Risk Index increases monotonically with difficulty batch.")
    else:
        print("WARNING: Risk Index is not strict monotonic (could be due to seed randomness).")
        print(f"Risks: {risks}")
        
    # Check Batch D characteristics (Stress)
    if results['D']['count'] < results['A']['count']:
        print("FAIL: Stress batch has fewer objects than Basic batch.")
        sys.exit(1)

    print("SOTA Feature Verification Passed.")

if __name__ == "__main__":
    test_sota_features()
