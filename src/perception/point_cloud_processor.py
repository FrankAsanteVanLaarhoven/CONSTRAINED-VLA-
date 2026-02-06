import numpy as np
from scipy.spatial import cKDTree
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class OrientedBoundingBox:
    center: np.ndarray
    extent: np.ndarray # half-lengths
    rotation: np.ndarray # 3x3 matrix
    color: np.ndarray # RGB
    eigenvalues: np.ndarray # Explained variance (linearity/planarity)

class PointCloudProcessor:
    """
    SOTA Perception Module for 3D Safety Analysis.
    Implements efficient geometric processing using Vectorized NumPy and KD-Trees.
    """
    def __init__(self, points: np.ndarray):
        """
        Args:
            points: Nx3 float array of XYZ coordinates.
        """
        self.points = points.astype(np.float64)
        self.tree = None
        self._build_tree()

    def _build_tree(self):
        if len(self.points) > 0:
            self.tree = cKDTree(self.points)

    def voxel_downsample(self, voxel_size: float) -> 'PointCloudProcessor':
        """
        Efficient Voxel Grid Downsampling.
        Returns a new PointCloudProcessor with reduced density.
        """
        if len(self.points) == 0: return self
        
        # Quantize coords
        coords = np.floor(self.points / voxel_size).astype(np.int32)
        
        # Use unique to find representative points (first encounter or centroid?)
        # For speed: first encounter (or unique indices)
        _, indices = np.unique(coords, axis=0, return_index=True)
        
        return PointCloudProcessor(self.points[indices])

    def compute_obb(self) -> OrientedBoundingBox:
        """
        Compute Oriented Bounding Box using PCA (Eigen-decomposition).
        Math: Covariance Matrix -> Eigenvectors (Principal Axes).
        """
        if len(self.points) < 3:
            raise ValueError("Need at least 3 points for OBB")

        # 1. Centroid
        center = np.mean(self.points, axis=0)
        centered_points = self.points - center

        # 2. Covariance Matrix (3x3)
        cov = np.cov(centered_points.T)

        # 3. Eigen Decomposition
        eigvals, eigvecs = np.linalg.eigh(cov)
        
        # Sort eigenvectors by eigenvalue (Large to Small) -> [Main Axis, Secondary, Normal]
        # np.linalg.eigh returns them in ascending order, so flip
        sort_indices = np.argsort(eigvals)[::-1]
        eigvals = eigvals[sort_indices]
        eigvecs = eigvecs[:, sort_indices] # Columns are vectors
        rotation = eigvecs

        # 4. Project points onto Principal Axes to find Extents
        # Transformation: P_rot = P_world @ R
        projected = centered_points @ rotation
        
        min_pt = np.min(projected, axis=0)
        max_pt = np.max(projected, axis=0)
        
        extent = (max_pt - min_pt) / 2.0
        center_offset = (max_pt + min_pt) / 2.0
        
        # The center in world frame is original centroid + offset rotated back
        world_center = center + (center_offset @ rotation.T)

        return OrientedBoundingBox(
            center=world_center,
            extent=extent,
            rotation=rotation,
            color=np.array([1, 0, 0]),
            eigenvalues=eigvals
        )

    def cluster_dbscan(self, eps: float, min_points: int) -> List['PointCloudProcessor']:
        """
        Custom High-Performance Clustering.
        Uses KD-Tree for O(log N) region queries.
        Returns list of PointCloudProcessors for each cluster.
        """
        if self.tree is None: return []

        n = len(self.points)
        labels = -1 * np.ones(n, dtype=np.int32) # -1 = Noise
        cluster_id = 0
        
        # Visited mask
        visited = np.zeros(n, dtype=bool)

        # Iterate all points
        for i in range(n):
            if visited[i]: 
                continue
            visited[i] = True
            
            # Query Neighbors
            indices = self.tree.query_ball_point(self.points[i], eps)
            
            if len(indices) < min_points:
                labels[i] = -1 # Noise
            else:
                # Start new cluster
                labels[i] = cluster_id
                
                # Expand Cluster (BFS)
                seed_set = list(indices)
                ptr = 0
                while ptr < len(seed_set):
                    idx = seed_set[ptr]
                    ptr += 1
                    
                    if not visited[idx]:
                        visited[idx] = True
                        neighbors = self.tree.query_ball_point(self.points[idx], eps)
                        if len(neighbors) >= min_points:
                            seed_set.extend(neighbors)
                    
                    if labels[idx] == -1: # Was noise, now border point
                        labels[idx] = cluster_id
                    
                cluster_id += 1
                
        # Extract Clusters
        clusters = []
        unique_labels = set(labels)
        if -1 in unique_labels: unique_labels.remove(-1)
        
        for lbl in unique_labels:
            mask = (labels == lbl)
            clusters.append(PointCloudProcessor(self.points[mask]))
            
        return clusters

    def estimate_normals(self, k: int=10) -> np.ndarray:
        """
        Estimate normals using Local PCA (k-NN).
        """
        normals = np.zeros_like(self.points)
        curvature = np.zeros(len(self.points))
        
        for i, pt in enumerate(self.points):
            # Get kNN
            dists, idxs = self.tree.query(pt, k=k)
            neighbors = self.points[idxs]
            
            # PCA on neighbors
            cov = np.cov((neighbors - np.mean(neighbors, axis=0)).T)
            vals, vecs = np.linalg.eigh(cov)
            
            # Normal is eigenvector of smallest eigenvalue
            normals[i] = vecs[:, 0]
            curvature[i] = vals[0] / np.sum(vals)
            
        return normals, curvature
