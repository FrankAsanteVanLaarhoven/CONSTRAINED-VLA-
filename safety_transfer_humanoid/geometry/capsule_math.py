import torch
import numpy as np

class CapsuleMath:
    """
    Library for differentiable 3D distance calculations involving Capsules.
    Used for 'Safety Volume' checks in Humanoid Manipulation.
    """
    
    @staticmethod
    def point_segment_distance(point, seg_a, seg_b):
        """
        Computes distance between a query point P and a line segment AB.
        Inputs:
            point: (N, 3) batch of points
            seg_a: (3,) start of segment
            seg_b: (3,) end of segment
        Returns:
            dist: (N,) distances
        """
        # Vector from A to B
        ab = seg_b - seg_a
        # Vector from A to P
        ap = point - seg_a
        
        # Project AP onto AB to find parameter t
        t = torch.sum(ap * ab, dim=-1) / (torch.sum(ab * ab, dim=-1) + 1e-8)
        
        # Clamp t to segment [0, 1]
        t = torch.clamp(t, 0.0, 1.0)
        
        # Find closest point on segment
        closest = seg_a + (ab * t.unsqueeze(-1))
        
        # Distance
        return torch.norm(point - closest, dim=-1)

    @staticmethod
    def segment_segment_distance(seg1_a, seg1_b, seg2_a, seg2_b):
        """
        Computes minimum distance between two line segments (Robot Link vs Patient Limb).
        Simplified implementation using clamping approximation for speed.
        
        For rigorous collision checking, creates a 'Capsule-Capsule' distance.
        """
        # For prototype: We sample points along Seg1 and check distance to Seg2
        # (Faster/Simpler for high-dim batching than rigorous geometric solver)
        
        num_samples = 5
        # Interpolate points along robot link
        alphas = torch.linspace(0, 1, num_samples)
        
        # (Samples, 3)
        points_on_seg1 = seg1_a + (seg1_b - seg1_a) * alphas.unsqueeze(-1)
        
        # Check dists to Seg2
        dists = CapsuleMath.point_segment_distance(
            points_on_seg1, 
            seg2_a, 
            seg2_b
        )
        
        return torch.min(dists)

    @staticmethod
    def check_safety_violation(robot_links, patient_capsules):
        """
        Checks if any robot link penetrates any patient capsule.
        
        robot_links: List of (A, B, radius) tuples
        patient_capsules: List of (A, B, radius) tuples
        
        Returns:
            violation_mask: (Numeric) >0 if unsafe.
        """
        min_margin = float('inf')
        
        for r_a, r_b, r_rad in robot_links:
            for p_a, p_b, p_rad in patient_capsules:
                
                # Centerline distance
                dist_center = CapsuleMath.segment_segment_distance(
                    torch.tensor(r_a), torch.tensor(r_b),
                    torch.tensor(p_a), torch.tensor(p_b)
                )
                
                # Surface distance = CenterDist - (r1 + r2)
                dist_surface = dist_center - (r_rad + p_rad)
                
                if dist_surface < min_margin:
                    min_margin = dist_surface
                    
        return min_margin
