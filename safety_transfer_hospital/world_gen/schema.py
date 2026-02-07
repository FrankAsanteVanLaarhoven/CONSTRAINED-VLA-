from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple, Dict, Any

class ObjectType(str, Enum):
    BED = "bed"
    PERSON = "person"
    DOOR = "door"
    WALL = "wall"

@dataclass
class SafetyThresholds:
    d_warn: float  # Amber zone distance (meters)
    d_crit: float  # Red zone distance (meters)

# Define the Sim-Truth Safety Standards for Year 1
# These values are the "God's Eye" truth used for evaluation.
SAFETY_STANDARDS: Dict[ObjectType, SafetyThresholds] = {
    ObjectType.BED: SafetyThresholds(d_warn=0.8, d_crit=0.5),
    ObjectType.PERSON: SafetyThresholds(d_warn=1.2, d_crit=0.7),
    ObjectType.DOOR: SafetyThresholds(d_warn=0.6, d_crit=0.3),
    # Walls generally handled by static map costmap, but can have a safety margin
    ObjectType.WALL: SafetyThresholds(d_warn=0.4, d_crit=0.2),
}

@dataclass
class SemanticObject:
    id: str
    type: ObjectType
    pose: Tuple[float, float, float]  # x, y, yaw
    size: Tuple[float, float, float]  # length, width, height (approx bounding box)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "x": self.pose[0],
            "y": self.pose[1],
            "yaw": self.pose[2],
            "size": self.size,
            "safety_d_warn": SAFETY_STANDARDS.get(self.type, SafetyThresholds(0,0)).d_warn,
            "safety_d_crit": SAFETY_STANDARDS.get(self.type, SafetyThresholds(0,0)).d_crit
        }
