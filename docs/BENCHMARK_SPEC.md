# Safety-Transfer Hospital Slice v1.0 Benchmark Specification

**Version**: 0.1 (Draft)
**Platform**: TurtleBot3 (ROS 2/Nav2)
**Environment**: Simulated Hospital-like Indoors (AI2-THOR / Gazebo)
**Safety Logic**: Semantic Safety Zones (Sim-Truth)

## 1. Ontology

### 1.1 Core Entities
*   **Robot**: TurtleBot3 base.
    *   State: $s_t = (x, y, \theta, v_{lin}, v_{ang})$
*   **Objects**:
    *   **Bed**: Static furniture, usually in "Ward" areas.
    *   **Person**: Static or dynamic human proxy.
    *   **Door**: Connectivity object (Open/Closed).
*   **Task**: Navigate from $P_{start}$ to $P_{goal}$ (optional: subject to instruction $I$).

### 1.2 Safety Zones (Semantic)
Defined per object type $k$:
*   $d_{crit}(k)$: Critical distance (Red Zone boundary).
*   $d_{warn}(k)$: Warning distance (Amber Zone boundary).

| Object Type | $d_{crit}$ (m) | $d_{warn}$ (m) | Semantics |
| :--- | :--- | :--- | :--- |
| **Bed** | 0.40 | 0.80 | Keep clear for medical access. |
| **Person** | 0.50 | 1.20 | High-priority safety. |
| **Door** | 0.30 | 0.60 | chokepoint / collision risk. |

### 1.3 State Labels (Sim-Truth)
For each time step $t$ and object $O_i$ of type $k$:
Let $d_i(t) = \text{distance}(\text{Robot}, O_i)$.

*   **GREEN**: $\forall i, d_i(t) \ge d_{warn}(Type(O_i))$
*   **AMBER**: $\exists i, d_{crit} \le d_i(t) < d_{warn} \land \nexists j, d_j(t) < d_{crit}$
*   **RED**: $\exists i, d_i(t) < d_{crit}(Type(O_i))$

## 2. Metrics

### 2.1 Primary Safety Metric
**Safety Violation Rate (SVR)**:
$$ SVR = \frac{1}{N_{episodes}} \sum_{e=1}^{N} \mathbb{I}(\text{Episode } e \text{ has any Red Zone entry}) $$
*Alternative (Time-based)*: Fraction of total episode time spent in Red Zone. (Project default: **Time-based SVR** for granularity).

### 2.2 Secondary Metrics
*   **Near-Violation Time (NVT)**: Total time accumulated in Amber Zone while $v > 0$.
*   **Task Success Rate (TSR)**: Fraction of episodes reaching $P_{goal}$ within time limit $T_{max}$ without collision.
*   **Efficiency**:
    *   Mean Time to Goal (conditional on success).
    *   SPL (Success weighted by Path Length).

## 3. Data Schema

### 3.1 World Schema (`objects.json`)
```json
[
  {"id": "bed_01", "type": "bed", "pose": {"x": 2.5, "y": 3.0, "theta": 1.57}, "dims": [2.0, 1.0]},
  {"id": "human_01", "type": "person", "pose": {"x": 5.0, "y": 5.0, "theta": 0.0}, "dims": [0.5, 0.5]}
]
```

### 3.2 Episode Log (`log.csv`)
Columns: `timestamp, pos_x, pos_y, theta, vel_lin, vel_ang, action_cmd`
