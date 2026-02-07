import sys
import os
import json
import shutil

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from safety_transfer_hospital.world_gen.generator import HospitalGenerator, ObjectType, SAFETY_STANDARDS

def test_generation():
    print("Testing HospitalGenerator...")
    output_dir = "tests/test_output/world_test"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    gen = HospitalGenerator(width=30, height=20, seed=123)
    gen.generate_layout()
    gen.place_objects(num_beds_per_room=2, prob_person=0.5)
    
    gen.export_map(output_dir)
    json_path = os.path.join(output_dir, "objects.json")
    gen.export_metadata(json_path)

    # Verification
    if not os.path.exists(json_path):
        print("FAIL: objects.json not created")
        sys.exit(1)
        
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    print(f"Generated {len(data)} objects.")
    
    # Check Schema
    for obj in data:
        if "safety_d_warn" not in obj or "safety_d_crit" not in obj:
            print(f"FAIL: Object {obj['id']} missing safety thresholds")
            sys.exit(1)
            
        # Verify thresholds match the standard
        obj_type = ObjectType(obj['type'])
        expected = SAFETY_STANDARDS[obj_type]
        if obj['safety_d_warn'] != expected.d_warn:
             print(f"FAIL: Object {obj['id']} has wrong d_warn. Got {obj['safety_d_warn']}, expected {expected.d_warn}")
             sys.exit(1)

    print("SUCCESS: World Generation and Schema Verification passed.")

if __name__ == "__main__":
    test_generation()
