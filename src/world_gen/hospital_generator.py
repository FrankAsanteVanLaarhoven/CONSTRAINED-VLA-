import numpy as np
import json
import os
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

@dataclass
class Pose:
    x: float
    y: float
    theta: float

@dataclass
class Object:
    id: str
    type: str  # 'bed', 'person', 'door'
    pose: Pose
    dims: List[float]  # [length, width]

@dataclass
class Room:
    id: str
    type: str # 'ward', 'corridor', 'connector'
    x: int
    y: int
    width: int
    height: int
    data: Dict

class HospitalGenerator:
    def __init__(self, width: int = 20, height: int = 20, resolution: float = 0.1):
        self.width_m = width
        self.height_m = height
        self.resolution = resolution
        self.grid_width = int(width / resolution)
        self.grid_height = int(height / resolution)
        # 0: free, 100: occupied, -1: unknown
        self.grid = np.zeros((self.grid_height, self.grid_width), dtype=np.int8)
        self.objects: List[Object] = []
        self.rooms: List[Room] = []
        self.object_counts = {"bed": 0, "person": 0, "door": 0}

    def generate_layout(self, num_wards: int = 2):
        """Simple procedural generation of wards connected by a corridor."""
        # 1. Clear grid (fill with walls initially? No, let's start empty and build walls)
        # Actually standard Nav2 map: 0 is free, 100 is occupied.
        # Let's say outer boundary is walls
        self._add_walls_rect(0, 0, self.grid_width, self.grid_height)

        # 2. Place a central corridor
        corridor_w = int(2.0 / self.resolution) # 2 meters wide
        corridor_x = int((self.grid_width - corridor_w) / 2)
        self._clear_rect(corridor_x, 1, corridor_w, self.grid_height - 2)
        
        self.rooms.append(Room("corr_main", "corridor", corridor_x, 1, corridor_w, self.grid_height - 2, {}))

        # 3. Place wards on left and right
        # Ward size: 5x5m
        ward_w = int(5.0 / self.resolution)
        ward_h = int(5.0 / self.resolution)
        
        placed_wards = 0
        trials = 0
        while placed_wards < num_wards and trials < 50:
            side = random.choice(['left', 'right'])
            if side == 'left':
                x = random.randint(1, corridor_x - ward_w - 1)
            else:
                x = random.randint(corridor_x + corridor_w + 1, self.grid_width - ward_w - 1)
            
            y = random.randint(1, self.grid_height - ward_h - 1)
            
            # Check overlap logic could go here, simplified for now:
            # Connect to corridor
            self._clear_rect(x, y, ward_w, ward_h)
            
            # Add door connection
            door_w = int(1.0 / self.resolution)
            if side == 'left':
                door_x = x + ward_w
                connect_x = corridor_x
            else:
                door_x = x
                connect_x = corridor_x + corridor_w
                
            door_y = y + int(ward_h / 2) - int(door_w / 2)
            
            # Cut hole for door
            # self._clear_rect(min(door_x, connect_x), door_y, abs(door_x - connect_x), door_w)
            # Actually just ensure the ward is open to the corridor for now? 
            # Or explicitly place a doorway.
            # Let's place a door object and clear the wall.
            
            door_pos_x = (x + ward_w) * self.resolution if side == 'left' else x * self.resolution
            door_pos_y = (y + ward_h/2) * self.resolution
            
            # Add Walls around the room? The _clear_rect just clears.
            # We need to define walls. The simplest way is to fill 'occupied' everywhere and carve 'free'.
            # But let's assume we map walls explicitly.
            
            # Re-thinking: Fill whole map with 'unknown' or 'walls', carve rooms.
            # Let's fill with walls (100)
            
            room_id = f"ward_{placed_wards}"
            self.rooms.append(Room(room_id, "ward", x, y, ward_w, ward_h, {"door_pos": (door_pos_x, door_pos_y)}))
            
            # Place Door Object
            self.add_object("door", door_pos_x, door_pos_y, 1.57 if side in ['left', 'right'] else 0.0) # Vertical door
            
            # Place Beds in Ward
            self._place_beds_in_ward(x, y, ward_w, ward_h)

            placed_wards += 1
            trials += 1
            
        # 4. Place People (Randomly in free space)
        self._place_random_people(int(num_wards * 1.5))

    def initialize_map(self):
        self.grid.fill(100) # Walls

    def _add_walls_rect(self, x, y, w, h):
        self.grid[y:y+h, x:x+w] = 100

    def _clear_rect(self, x, y, w, h):
        self.grid[y:y+h, x:x+w] = 0

    def add_object(self, type_name: str, x: float, y: float, theta: float):
        self.object_counts[type_name] += 1
        oid = f"{type_name}_{self.object_counts[type_name]:02d}"
        
        dims = [1.0, 1.0]
        if type_name == "bed": dims = [2.0, 1.0]
        elif type_name == "door": dims = [0.2, 1.0]
        elif type_name == "person": dims = [0.5, 0.5]
        
        obj = Object(oid, type_name, Pose(x, y, theta), dims)
        self.objects.append(obj)
        
        # Mark static objects on grid? 
        # Beds are obstacles. People are dynamic (technically), but we might bake them as obstacles for the baseline Nav2 costmap 
        # or leave them free and let the local costmap see them.
        # For 'Sim Truth', we track them in the list.
        # For the Sim Environment (SDF), they will be spawned.
        # For the Navigation Map (PGM), usually static furniture (beds) is painted, people are not.
        
        if type_name == "bed": # Paint beds into the map
             self._paint_object_on_grid(obj)

    def _paint_object_on_grid(self, obj: Object):
        # Simple rasterization
        gx = int(obj.pose.x / self.resolution)
        gy = int(obj.pose.y / self.resolution)
        gw = int(obj.dims[0] / self.resolution)
        gh = int(obj.dims[1] / self.resolution)
        
        # Simple AABB assumption for now
        x0 = gx - gw//2
        y0 = gy - gh//2
        self.grid[y0:y0+gh, x0:x0+gw] = 100

    def _place_beds_in_ward(self, wx, wy, ww, wh):
        # Place 1-2 beds
        num_beds = 1 # Simple start
        # Center of ward
        bx = (wx + ww/2) * self.resolution
        by = (wy + wh/2) * self.resolution
        self.add_object("bed", bx, by, 0.0)

    def _place_random_people(self, count):
        for _ in range(count):
            # Try to report a free spot 
            for _ in range(100):
                rx = random.randint(1, self.grid_width-2)
                ry = random.randint(1, self.grid_height-2)
                if self.grid[ry, rx] == 0:
                    self.add_object("person", rx*self.resolution, ry*self.resolution, random.uniform(0, 6.28))
                    break

    def to_dict(self):
        return {
            "width": self.width_m,
            "height": self.height_m,
            "resolution": self.resolution,
            "objects": [asdict(obj) for obj in self.objects]
        }
    
    def save_to_json(self, path):
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    def save_map_pgm(self, path_base):
        # Save PGM and YAML for ROS 2 Nav2
        from PIL import Image
        
        # 0=free (254), 100=occupied (0), -1=unknown (205)
        # Nav2 standard: occupied=0(black), free=254(white), unknown=205(gray)
        pgm_data = np.full_like(self.grid, 205, dtype=np.uint8)
        pgm_data[self.grid == 0] = 254
        pgm_data[self.grid == 100] = 0
        
        # Flip Y for image coordinate system usually? Map origin is usually bottom-left.
        # Image origin is top-left.
        pgm_data = np.flipud(pgm_data)

        img = Image.fromarray(pgm_data)
        img.save(f"{path_base}.pgm")
        
        with open(f"{path_base}.yaml", 'w') as f:
            f.write(f"""image: {os.path.basename(path_base)}.pgm
mode: trinary
resolution: {self.resolution}
origin: [0.0, 0.0, 0.0]
negate: 0
occupied_thresh: 0.65
free_thresh: 0.196
""")

    def save_sdf(self, path):
        """Export to Gazebo SDF format."""
        
        sdf_content =f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="hospital_world">
    <include>
      <uri>model://sun</uri>
    </include>
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <!-- Walls from Grid (Simplified: just boundary for now or full extrude?) -->
    <!-- For simplicity, we just place the objects. The map corresponds to the static walls. 
         Ideally we generate collision geometry for walls. -->
    
    <model name="hospital_walls">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <heightmap>
              <uri>file://{os.path.basename(path).replace('.world', '')}/map.pgm</uri>
              <size>{self.width_m} {self.height_m} 2</size> <!-- 2m high walls -->
              <pos>0 0 0</pos>
            </heightmap>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <heightmap>
              <texture>
                <diffuse>file://media/materials/textures/dirt_diffusespecular.png</diffuse>
                <normal>file://media/materials/textures/flat_normal.png</normal>
                <size>1</size>
              </texture>
              <uri>file://{os.path.basename(path).replace('.world', '')}/map.pgm</uri>
              <size>{self.width_m} {self.height_m} 2</size>
              <pos>0 0 0</pos>
            </heightmap>
          </geometry>
        </visual>
      </link>
    </model>
"""
        # Add Objects
        for obj in self.objects:
            model_uri = "model://cube_20k" # Default placeholder
            if obj.type == "bed": model_uri = "model://aws_robomaker_hospital_bed_01"
            elif obj.type == "person": model_uri = "model://person_standing"
            elif obj.type == "door": model_uri = "model://door"
            
            # Z position: 0 for now.
            
            sdf_content += f"""
    <include>
      <uri>{model_uri}</uri>
      <name>{obj.id}</name>
      <pose>{obj.pose.x} {obj.pose.y} 0 0 0 {obj.pose.theta}</pose>
    </include>
"""

        sdf_content += """
  </world>
</sdf>
"""
        with open(path, 'w') as f:
            f.write(sdf_content)
