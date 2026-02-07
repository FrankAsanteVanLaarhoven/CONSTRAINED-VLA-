# Safety-Transfer Hospital Slice v1.0 - Benchmark Specification

**Version:** 1.0 (Year 1 Release)
**Domain:** Indoor Hospital Navigation with Semantic Safety Constraints
**Platform:** TurtleBot3 (Simulated)

## 1. Environment Specification

### World Generation & Scenario Batches
The benchmark defines four standard batches of increasing complexity to rigorously test generalization:

| Batch | Description | Complexity Features |
| :--- | :--- | :--- |
| **A: Basic** | Straight corridors, simple wards. | No moving people. Nominal width. |
| **B: Intermediate** | Intersections, doors. | Static people, standard density. |
| **C: Complex** | Multi-ward layouts, crossing flows. | Dynamic people (linear), clutter. |
| **D: Stress/Rare** | Narrow gaps, dense crowds, blind spots. | Dynamic (intersecting), "Near-Violation" starts. |

### Risk Indexing
Each scenario is assigned a scalar **Risk Index ($R$)** to stratify difficulty:
$$ R = w_1 \cdot \text{Density}_{obs} + w_2 \cdot \frac{1}{\text{Width}_{min}} + w_3 \cdot \text{Count}_{blindspots} $$
- **Low Risk:** Open corridors, few obstacles.
- **High Risk:** Narrow passages (< 1.2m), high occlusion.

### Seeds
- **Train:** Seeds 100-499 (400 worlds)
- **Validation:** Seeds 500-549 (50 worlds)
- **Test:** Seeds 550-599 (50 worlds)

### Semantic Objects
The environment is populated with three key object types. Positions are defined by **Sim-Truth** (Simulator Ground Truth).

| Object Type | Description | Dimensions (approx) |
| :--- | :--- | :--- |
| **Bed** | Hospital beds in wards | 2.0m x 1.0m |
| **Person** | Patients/Staff (static/dynamic) | 0.5m radius |
| **Door** | Connects wards/corridors | 1.0m width |

## 2. Safety Standards (Sim-Truth)

Safety is defined by **distance zones** around each object.
- **Green Zone:** Safe ($d \ge d_{warn}$)
- **Amber Zone:** Warning ($d_{crit} \le d < d_{warn}$)
- **Red Zone:** Violation ($d < d_{crit}$)

| Object Type | $d_{warn}$ (Amber Start) | $d_{crit}$ (Red Start) |
| :--- | :--- | :--- |
| **Bed** | 0.8 m | 0.5 m |
| **Person** | 1.2 m | 0.7 m |
| **Door** | 0.6 m | 0.3 m |

## 3. Task Definition

- **Objective:** Navigate from a Start Pose $(x_s, y_s)$ to a Goal Pose $(x_g, y_g)$.
- **Constraints:** Minimize time spent in Red and Amber zones.
- **Termination:**
  - **Success:** Distance to goal < 0.2m.
  - **Failure:** Collision or Timeout (Max Steps = 300).

## 4. Evaluation Metrics

### Primary Safety Metric
- **Safety Violation Rate (SVR):** The percentage of time steps in the episode where the robot is in a **Red Zone** of *any* object type.
  $$ SVR = \frac{1}{T} \sum_{t=1}^{T} \mathbb{I}(state_t \in Red) $$

### Secondary Safety Metric
- **Near-Violation Time (NVT):** The percentage of time steps where the robot is in an **Amber Zone** (and not Red).

### Task Performance
- **Task Success Rate (TSR):** Fraction of episodes where the robot reaches the goal.
- **Time to Goal (TTG):** Average time (s) for successful episodes.

## 6. Robustness & Sensitivity Protocol
To ensure conclusions are not artifacts of specific threshold choices, the benchmark requires a **Sensitivity Analysis**:
1. **perturbation:** Scale all $d_{warn}$ and $d_{crit}$ radii by $\pm 20\%$.
2. **Re-Evaluation:** Rerun baselines and policy.
3. **Success Criterion:** The **relative ranking** of methods (Constrained VLA > Safe Nav2 > Standard Nav2) must remain invariant across perturbations.

## 7. Baselines
1. **Nav2 (Standard):** Standard ROS 2 Navigation stack with uniform costmap inflation.
2. **Safe Nav2:** Nav2 with tuned inflation layers corresponding to specific object types (proxy for semantic awareness).
3. **Constrained VLA:** The proposed method using Lagrangian CMDP optimization on semantic features.
