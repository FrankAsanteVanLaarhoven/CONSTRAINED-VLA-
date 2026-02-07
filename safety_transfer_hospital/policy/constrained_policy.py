import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Tuple, Dict

class ConstrainedVLAPolicy(nn.Module):
    def __init__(self, state_dim: int = 3, semantic_dim: int = 3, hidden_dim: int = 64):
        """
        A simple Year 1 VLA Policy for Constrained CMDP.
        
        Args:
            state_dim: Robot state dimension (e.g., x, y, yaw relative to goal or distances).
                       Here we assume "relative goal vector" (dx, dy) + "current yaw" = 3.
            semantic_dim: Dimensions for semantic inputs (d_bed, d_person, d_door) = 3.
            hidden_dim: Size of hidden layers.
        """
        super().__init__()
        
        # 1. Feature Encoders
        self.state_encoder = nn.Linear(state_dim, hidden_dim)
        self.semantic_encoder = nn.Linear(semantic_dim, hidden_dim)
        
        # 2. Fusion Layer (Simulating VLA fusion, simplified for Year 1)
        self.fusion = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        
        # 3. Action Head (Actor) -> [v, omega]
        # v in [0, 0.22], omega in [-2.8, 2.8] (TurtleBot3 limits)
        self.action_head = nn.Linear(hidden_dim, 2)
        
        # 4. Safety Critic Head (for Lagrangian Learning)
        # Predicts probability/value of violating constraints for Bed, Person, Door
        self.safety_head = nn.Linear(hidden_dim, 3) 
        
        # 5. Lagrangian Multipliers (Learnable parameters)
        # One lambda per semantic type: Bed, Person, Door
        self.log_lambdas = nn.Parameter(torch.zeros(3)) # start at 1.0 (exp(0))

    def forward(self, state: torch.Tensor, semantic_dists: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass.
        
        Args:
            state: [batch, state_dim]
            semantic_dists: [batch, semantic_dim]
            
        Returns:
            actions: [batch, 2] (v, omega)
            safety_values: [batch, 3] (predicted safety cost/violation risk)
        """
        s_emb = F.relu(self.state_encoder(state))
        sem_emb = F.relu(self.semantic_encoder(semantic_dists))
        
        # Fuse
        fused = torch.cat([s_emb, sem_emb], dim=-1)
        features = self.fusion(fused)
        
        # Action
        raw_actions = self.action_head(features)
        # Sigmoid for v -> [0, 1] then scale to 0.22
        # Tanh for omega -> [-1, 1] then scale to 1.0 (keep it gentle)
        v = torch.sigmoid(raw_actions[:, 0]) * 0.22 
        omega = torch.tanh(raw_actions[:, 1]) * 1.0
        actions = torch.stack([v, omega], dim=-1)
        
        # Safety Critic
        safety_values = self.safety_head(features)
        
        return actions, safety_values

    def get_lambdas(self):
        return torch.exp(self.log_lambdas)
        
    def act_numpy(self, state: np.ndarray, semantic_dists: np.ndarray) -> np.ndarray:
        """Helper for inference/simulation loop."""
        with torch.no_grad():
            s_t = torch.FloatTensor(state).unsqueeze(0)
            sem_t = torch.FloatTensor(semantic_dists).unsqueeze(0)
            actions, _ = self(s_t, sem_t)
            return actions[0].numpy()
