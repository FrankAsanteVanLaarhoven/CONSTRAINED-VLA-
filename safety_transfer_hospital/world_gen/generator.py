import random
import json
import os
import math
from typing import List, Dict, Any, Tuple
from .schema import ObjectType, SemanticObject, SAFETY_STANDARDS

class HospitalGenerator:
    def __init__(self, width: int = 20, height: int = 20, seed: int = None, difficulty_batch: str = "B"):
        """
        Args:
            difficulty_batch: 'A' (Basic), 'B' (Intermediate), 'C' (Complex), 'D' (Stress/Rare)
        """
        if seed is not None:
            random.seed(seed)
        self.width = width
        self.height = height
        self.difficulty_batch = difficulty_batch
        self.objects: List[SemanticObject] = []
        self.map_grid = [[0 for _ in range(width)] for _ in range(height)] # 0=empty, 1=wall
        self.risk_index = 0.0

    def generate_layout(self):
        """Generates layout based on difficulty batch."""
        # Clear previous state
        self.objects = []
        self.map_grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Structure modification based on batch (conceptual for Q1 prototype)
        # Batch A: Wider corridors (4), B/C: Standard (3), D: Narrow (2)
        corridor_width = 4 if self.difficulty_batch == "A" else (2 if self.difficulty_batch == "D" else 3)
        
        # 1. Central Corridor (Horizontal)
        corridor_y = self.height // 2
        for x in range(self.width):
            for y in range(corridor_y - (corridor_width//2), corridor_y + (corridor_width//2) + 1):
                if 0 <= y < self.height:
                    self.map_grid[y][x] = 0 # Empty
        
        # 2. Add Wards
        num_wards = 3
        ward_width = self.width // num_wards
        for i in range(num_wards):
            self._create_room(i * ward_width, 0, ward_width, corridor_y - (corridor_width//2))
            self._create_room(i * ward_width, corridor_y + (corridor_width//2) + 1, ward_width, self.height)

    def _create_room(self, start_x, start_y, w, h):
        """Creates a room with walls and a door."""
        for x in range(start_x, start_x + w):
            for y in range(start_y, start_y + h):
                if x == start_x or x == start_x + w - 1 or y == start_y or y == start_y + h - 1:
                     if 0 <= y < self.height and 0 <= x < self.width:
                        self.map_grid[y][x] = 1 # Wall
        
        # Door placement
        door_x = start_x + w // 2
        corridor_center_y = self.height // 2
        if start_y < corridor_center_y: # Top room
            door_y = start_y + h - 1
        else: # Bottom room
            door_y = start_y
        
        if 0 <= door_y < self.height and 0 <= door_x < self.width:
             self.map_grid[door_y][door_x] = 0
             self.objects.append(SemanticObject(
                 id=f"door_{len(self.objects)}",
                 type=ObjectType.DOOR,
                 pose=(door_x, door_y, 0),
                 size=(1.0, 0.2, 2.0)
             ))

    def place_objects(self):
        """Places objects based on Difficulty Batch (Risk/Density control)."""
        # Batch Configs
        # A: Sparse, no people
        # B: Standard density
        # C: High density
        # D: Extreme density + clustering
        
        if self.difficulty_batch == "A":
            num_beds = 1
            prob_person = 0.0
        elif self.difficulty_batch == "B":
            num_beds = 2
            prob_person = 0.5
        elif self.difficulty_batch == "C":
            num_beds = 3
            prob_person = 0.8
        else: # D
            num_beds = 4
            prob_person = 1.0 # Guaranteed people overcrowding

        corridor_y = self.height // 2
        ward_width = self.width // 3
        
        for i in range(3):
            # Top rooms
            self._populate_area(i * ward_width + 1, 1, ward_width - 2, corridor_y - 2, num_beds, prob_person)
            # Bottom rooms
            self._populate_area(i * ward_width + 1, corridor_y + 3, ward_width - 2, self.height - corridor_y - 4, num_beds, prob_person)
            
        self._calculate_risk_index()

    def _populate_area(self, start_x, start_y, w, h, num_beds, prob_person):
         for _ in range(num_beds):
             bx = random.randint(start_x, start_x + w - 1)
             by = random.randint(start_y, start_y + h - 1)
             self.objects.append(SemanticObject(
                 id=f"bed_{len(self.objects)}",
                 type=ObjectType.BED,
                 pose=(bx, by, 0),
                 size=(2.0, 1.0, 0.5)
             ))
             
             if random.random() < prob_person:
                 # In Batch D (Stress), place person closer to "path" (heuristic)
                 offset = 0.5 if self.difficulty_batch == "D" else 1.5
                 px = bx + random.uniform(-offset, offset)
                 py = by + random.uniform(-offset, offset)
                 self.objects.append(SemanticObject(
                     id=f"person_{len(self.objects)}",
                     type=ObjectType.PERSON,
                     pose=(px, py, random.uniform(0, 6.28)),
                     size=(0.5, 0.5, 1.7)
                 ))

    def _calculate_risk_index(self):
        """
        Computes scalar Risk Index based on obstacle density and corridor width.
        Formula: R = (Num_People * 1.0 + Num_Beds * 0.5) / (MapArea/100) + BlindSpotFactor
        """
        num_people = sum(1 for o in self.objects if o.type == ObjectType.PERSON)
        num_beds = sum(1 for o in self.objects if o.type == ObjectType.BED)
        
        density_score = (num_people * 1.0 + num_beds * 0.5) / ((self.width * self.height) / 100.0)
        
        # Corridor Narrowness Factor: 4->0, 3->1, 2->2 (Stress)
        corridor_w = 4 if self.difficulty_batch == "A" else (2 if self.difficulty_batch == "D" else 3)
        narrow_factor = (4 - corridor_w) * 2.0
        
        self.risk_index = density_score + narrow_factor

    def export_metadata(self, output_path: str):
        data = {
            "objects": [obj.to_dict() for obj in self.objects],
            "meta": {
                "difficulty_batch": self.difficulty_batch,
                "risk_index": round(self.risk_index, 2),
                "width": self.width,
                "height": self.height
            }
        }
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Exported {len(self.objects)} objects (Risk Index: {self.risk_index:.2f}) to {output_path}")

    def export_map(self, output_dir: str):
         with open(os.path.join(output_dir, "map_layout.txt"), "w") as f:
             for row in self.map_grid:
                 f.write("".join(["#" if c == 1 else "." for c in row]) + "\n")
