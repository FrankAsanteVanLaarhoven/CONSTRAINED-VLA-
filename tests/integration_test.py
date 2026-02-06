import sys
import os
import shutil
import zipfile
import json
import pandas as pd
import numpy as np

# Add src to path
sys.path.append(os.path.abspath('src'))

from world_gen.hospital_generator import HospitalGenerator
from simulation.episode_runner import EpisodeRunner, RobotState
from metrics.safety_evaluator import SafetyEvaluator
from policy.constrained_policy import ConstrainedPolicy
from data_loader.oxford_adapter import OxfordAdapter

def test_pipeline():
    print("1. Testing World Generation...")
    gen = HospitalGenerator(width=20, height=20)
    gen.initialize_map()
    gen.generate_layout(num_wards=1)
    world_config = gen.to_dict()
    assert len(world_config['objects']) > 0, "No objects generated"
    
    # Save dummy world for zip test
    os.makedirs('data/dataset_v0.1/world_test', exist_ok=True)
    with open('data/dataset_v0.1/world_test/objects.json', 'w') as f:
        json.dump(world_config, f)
    
    print("2. Testing Simulation & Policy...")
    policy = ConstrainedPolicy()
    runner = EpisodeRunner(world_config, mode="mock")
    
    # Manual policy step check
    r_s = RobotState(0, 5, 5, 0, 0, 0) # dataclass from policy module
    action = policy.get_action(r_s, (8, 8, 0), {})
    assert action is not None
    
    # Runner check
    traj = runner.run_episode((2,2,0), (8,8,0), duration=2.0)
    assert len(traj) > 0
    
    # Save dummy log
    df = pd.DataFrame([{'t': t.t, 'x': t.x, 'y': t.y, 'v_lin': t.v_lin, 'v_ang': t.v_ang} for t in traj])
    os.makedirs('data/dataset_v0.1/world_test/episodes', exist_ok=True)
    df.to_csv('data/dataset_v0.1/world_test/episodes/episode_00_log.csv', index=False)

    print("3. Testing Metrics...")
    evaluator = SafetyEvaluator(world_config['objects'])
    metrics, _ = evaluator.evaluate_episode(df)
    assert 'SVR' in metrics
    
    print("4. Testing Oxford Adapter...")
    adapter = OxfordAdapter()
    objs, log_df = adapter.load_scenario(duration_s=2.0)
    assert len(objs) > 0
    assert not log_df.empty
    
    print("5. Testing Evidence Pack (Zip)...")
    # Minimal zip check
    with zipfile.ZipFile('evidence_pack_test.zip', 'w') as zf:
        zf.write('src/world_gen/__init__.py', 'src/world_gen/__init__.py')

    print("6. Testing SOTA Perception...")
    from perception.point_cloud_processor import PointCloudProcessor
    rng = np.random.default_rng()
    pts = rng.random((50, 3))
    proc = PointCloudProcessor(pts)
    clusters = proc.cluster_dbscan(0.5, 3)
    if len(clusters) > 0:
        obb = clusters[0].compute_obb()
        assert obb.extent is not None

    print("7. Testing Advanced Metrics...")
    from metrics.advanced_safety import AdvancedSafetyMetrics
    adv_metrics = AdvancedSafetyMetrics()
    res = adv_metrics.compute_metrics(df) # using log df from step 2
    assert res.aj_score >= 0.0

    print("ALL TESTS PASSED.")

if __name__ == "__main__":
    test_pipeline()
