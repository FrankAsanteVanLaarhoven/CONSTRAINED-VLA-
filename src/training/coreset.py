import numpy as np
from scipy.spatial import cKDTree
from typing import List, Dict, Tuple
import pandas as pd

class GeometricCoresetSelector:
    """
    Implements 'Geometric Coreset Active Fine-Tuning' (G-CAFT).
    Selects the 'Shortest Circle' dataset that maximizes coverage and risk-density.
    """
    def __init__(self, observation_dim: int = 4):
        self.obs_dim = observation_dim
        
    def select_coreset(self, episodes: List[pd.DataFrame], select_ratio: float = 0.2) -> List[Dict]:
        """
        Selects top % of samples using Risk-Weighted Geometric Diversity.
        
        Args:
            episodes: List of episode DataFrames.
            select_ratio: Fraction of data to keep (e.g. 0.2 = 20%).
            
        Returns:
            List of selected samples ({"t": ..., "state": ..., "action": ...})
        """
        all_samples = []
        vectors = []
        risks = []
        
        # 1. Feature Extraction & Risk Assessment
        for ep_idx, df in enumerate(episodes):
            for idx, row in df.iterrows():
                # Featurize: [x, y, v_lin, d_nearest]
                # Assuming 'd_person' or similar exists (or we compute it)
                # For robustness, we assume a 'd_min' column or approximate it
                
                d_min = 10.0
                if 'd_person' in row: d_min = min(d_min, row['d_person'])
                if 'd_bed' in row: d_min = min(d_min, row['d_bed'])
                
                vec = np.array([row['x'], row['y'], row['v_lin'], d_min])
                
                # Risk Score: 1/d (Higher risk = Higher importance)
                risk = 1.0 / (max(d_min, 0.1) + 1e-3)
                
                vectors.append(vec)
                risks.append(risk)
                all_samples.append({
                    "episode_id": ep_idx,
                    "step_id": idx,
                    "row": row,
                    "risk": risk
                })
                
        if not vectors:
            return []
            
        X = np.stack(vectors)
        risks = np.array(risks)
        
        # 2. Geometric Coverage (K-Center Greedy / Diversity)
        # We want points that are diverse AND risky.
        # Hybrid Score = Risk * Diversity_Potential
        
        # Simple approach: Stratified FPS (Farthest Point Sampling)? 
        # Or just Sort by Risk and take top K? (Misses diversity)
        # "Patent-Worthy": Risk-Weighted K-Means Initialization Logic.
        
        N = len(X)
        K = int(N * select_ratio)
        
        # Normalize Data
        X_norm = (X - X.mean(0)) / (X.std(0) + 1e-6)
        
        selected_indices = []
        
        # Step A: Pick top K/2 Riskiest (Boundary Cases)
        # These define the "Safety Constraints"
        risk_sort = np.argsort(risks)[::-1] # Descending
        num_risk = K // 2
        selected_indices.extend(risk_sort[:num_risk].tolist())
        
        # Step B: Pick top K/2 Most Diverse from the remainder (Coverage)
        # Using MaxMin distance to current set
        remaining_indices = list(set(range(N)) - set(selected_indices))
        
        if len(remaining_indices) > 0 and len(selected_indices) < K:
            # Simple FPS on remainder relative to Risk Set
            # Efficient Approx: Random projection or simple batch
            # For "Shortest Circle" speed, we just sample randomly from remainder
            # weighted by distance? 
            # Let's use a simpler heuristic for speed: Grid-based filtering
            
            # Using scikit-learn or scipy for real K-Means is slow.
            # Fast approx: Histogram/Voxel Sampling
            
            num_diverse = K - len(selected_indices)
            # Random selection from remainder is often "good enough" baseline
            # But let's do "Inverse Density" sampling
            
            # Build Tree on Norm Data
            tree = cKDTree(X_norm)
            densities = tree.query_ball_point(X_norm[remaining_indices], r=0.5, return_length=True)
            
            # Invert density: We want sparse regions
            inv_density = 1.0 / (np.array(densities) + 1.0)
            prob = inv_density / inv_density.sum()
            
            diverse_picks = np.random.choice(
                remaining_indices, 
                size=num_diverse, 
                replace=False, 
                p=prob
            )
            selected_indices.extend(diverse_picks.tolist())
            
        # 3. Compile Coreset
        coreset = [all_samples[i] for i in selected_indices]
        return coreset
