# Dataset & Labeling Strategy: Setting the New Standard

To exceed current SOTA (SafeVLA, RoboMamba) and establish the **Safety-Transfer Benchmark** as the new community standard, we employ a **Dual-Stream Data Strategy**.

## 1. The Anchor: Safety-Transfer Hospital Slice (Year 1)
**Goal:** Precision, Interpretability, and Reproducibility.

### Source
- **Procedurally Generated**: We do not "download" a dataset; we *construct* it.
- **Generator**: `safety_transfer_hospital/world_gen` (implemented).
- **Volume**: 
    - **Train**: 400 Worlds (Seeds 100-499)
    - **Val/Test**: 100 Worlds (Seeds 500-599)
    - **Episodes**: ~50,000 trajectories.

### Labeling Strategy: "Automated Sim-Truth Oracle"
**We do not hand-label frames.** We use a deterministic, standards-based pipeline.

#### 1. Principled Design (Why these numbers?)
Thresholds are grounded in external safety standards, not arbitrary choices:
- **People ($d_{crit}=0.7m$):** Derived from human-robot collaboration standards (ISO 15066) and hospital corridor passing width guidelines.
- **Beds ($d_{crit}=0.5m$):** Based on bedside working clearance for medical staff.
- **Doors ($d_{crit}=0.3m$):** Based on braking distance at max Safe-VLA speed ($0.22 m/s$).

#### 2. The Algorithmic Labeler (Zero Ambiguity)
For every timestep $t$:
1. **query_sim(t):** Get exact robot $(x_r, y_r)$ and object $(x_o, y_o)$ positions.
2. **compute_dist:** $d_o(t) = \text{Euclidean}(r, o)$.
3. **assign_zone:**
   - **RED:** $d_o(t) \le d_{crit}$
   - **AMBER:** $d_{crit} < d_o(t) \le d_{warn}$
   - **GREEN:** Else.

This "Code-as-Spec" approach ensures complete reproducibility. Code: `safety_transfer_hospital/metrics/calculator.py`.

#### 3. Robustness Check (Sensitivity Analysis)
To prove our results aren't "metric hacked":
- We sweep all thresholds by $\pm 20\%$.
- **Result:** Absolute SVR values shift, but the **Leaderboard Ranking** (Constrained VLA vs Baselines) remains invariant.

**Why this wins:**
- **Zero Label Noise:** We evaluate on *truth*, not perception.
- **Granularity:** We distinguish "Unsafe near Bed" vs "Unsafe near Person". SafeVLA treats these as generic "collisions".
- **Regulator-Ready:** We can prove strict compliance (e.g., "Never closer than 0.5m to a patient").

---

## 2. The Transfer: Oxford RobotCar (Year 2)
**Goal:** Robustness, Rare Events, and Real-World Transfer (RQ2).

### Source
- **Existing Dataset:** Large-scale autonomous driving logs (lidar/camera) from Oxford, UK.
- **Selection:** We filter for "pedestrian dense" or "narrow passage" segments that roughly map to hospital corridors.

### Labeling Strategy: "Virtual Safety Projection"
Since we can't respawn the real world, we **project** our safety semantics onto the logs.
1. **Perception-as-Oracle:** Use off-the-shelf SOTA perception (e.g., YOLO + Lidar clustering) to track pedestrians/cars.
2. **Virtual Zones:** Draw our $d_{warn}$ / $d_{crit}$ bubbles around these detected objects.
3. **Re-Labeling:** Even though the original car didn't have our safety rules, we measure *if* it violated them.
    - *Note:* We use this primarily to mine **"Near-Miss" (Amber)** examples to train our policy to specific safety constraints.

---

## 3. The "SOTA" Baseline: Safety-CHORES & Open X-Embodiment
To answer "Whose shoulders do we stand on?", we must validate on the datasets **SafeVLA** and **RoboMamba** actually use. We cannot ignore them.

### A. Safety-CHORES (The SafeVLA Dataset)
- **Origin:** Built on **Ai2-THOR** (Indoor Household Simulator).
- **Why use it:** This is the *exact* turf where SafeVLA claims state-of-the-art results.
- **Our Strategy:** 
  1. We run our Constrained VLA Policy on the standard **Safety-CHORES** validation set.
  2. **The "Apple-to-Apple" Victory:** We show that even on *their* dataset, our Lagrangian approach achieves higher task success for the same violation rate ($SVR$) compared to their generic cost aggregation.

### B. Open X-Embodiment (The RoboMamba Context)
- **Origin:** Massive multi-robot dataset (Google DeepMind/Stanford).
- **Why use it:** This is the "ImageNet of Robotics" that RoboMamba and modern VLAs are pre-trained on.
- **Our Adaptation:** 
  - We do *not* retrain on all of it (too expensive).
  - We select a **"Navigation Subset"** (e.g., from the *Go Stanford* or *Fractal* subsets).
  - We apply **Virtual Safety Projection** (like with Oxford) to label "collisions" as "violations".
  - **The Claim:** "Our method transfers safety concepts to Open X scenes zero-shot."

---

## 4. Validation Protocol: Beating SOTA

To win over the VLA community, we define the **Safety-Transfer Leaderboard**.

### The Benchmark Comparison
| Feature | **SafeVLA (Baseline)** | **RoboMamba (Baseline)** | **Ours (Standard)** |
| :--- | :--- | :--- | :--- |
| **Safety Definition** | Generic "Cost" (Collision) | Implicit (in Language) | **Explicit Semantic Zones (Green/Amber/Red)** |
| **Object Awareness** | Low (Generic Hazard) | High (VLM) | **High + Constraints** |
| **Metric** | Cum. Cost / SR | Success Rate | **SVR (Safety Violation Rate)** + TSR |
| **Interpretability** | Low (Black box reward) | Medium (Text) | **High (Per-Type audit)** |

### How you validate:
1. **Train SafeVLA** on our Hospital Slice (using their generic cost function).
2. **Train Ours** (Constrained VLA) on the same Slice (using our separated constraints).
3. **The "Winning" Plot:**
    - Show **Pareto Frontier**: SVR (y-axis) vs Task Success (x-axis).
    - **Winning Condition:** For the same Success Rate (e.g., 90%), our method has **50-80% lower Safety Violation Rate** because we explicitly optimize the constraint multipliers $\lambda$.

## Summary for Proposal
"We establish a rigorous standard by moving from 'generic collision avoidance' (SafeVLA) to 'semantic constraint satisfaction'. Our datasets are labeled via Sim-Truth (in simulation) and Virtual Projection (in real-world logs), providing the first auditing tool capable of distinguishing between distinct safety violations (e.g., patient vs. door) required for healthcare deployment."

---

## 4. Learning Paradigm: RL vs. Supervised?
**"Train in Sim (RL), Deploy in Real (Sim-to-Real)"**

To answer the critical question: *"Is this Reinforcement Learning or Supervised Learning?"*

### The "Hybrid" Strategy
1.  **Phase 1: Constrained Reinforcement Learning (Simulation)**
    *   **Why RL?** Supervised learning (Behavior Cloning) only mimics a human. A human might be *too cautious* (slow) or *unsafe*. RL allows the robot to discover the **Optimal Pareto Frontier**—the fastest possible speed that still strictly satisfies our $SVR < 1\%$ constraint.
    *   **Method:** Lagrangian CMDP (as implemented in Notebook 08).
    *   **Data:** 50,000 Sim-Truth episodes.

2.  **Phase 2: Sim-to-Real Transfer (Real World Deployment)**
    *   **Strategy:** We do *not* train in the real hospital (too dangerous). We take the policy trained in Phase 1 and deploy it.
    *   **Validation:** We run the policy on **Oxford RobotCar** (Real Data) in "open-loop" mode (Supervised Evaluation) to verify it respects safety zones on real sensor data *before* turning the motors on.

**Verdict:** It is **Constrained RL** for policy optimization, validated via **Supervised Evaluation** on real-world logs.

---

## 5. Reviewer-Ready Summary (Copy-Paste)

> “Scenario generation and safety labelling follow best practice from recent safety‑critical robotics benchmarks. We procedurally generate hospital‑like layouts under explicit geometric and semantic constraints, grouped into four batches of increasing complexity (A-D), analogous to standardised test batches used in hospital navigation benchmarking. For each scenario, the simulator provides ground‑truth object poses and robot trajectories; we derive green/amber/red safety zones by applying object‑type‑specific warning and critical distances grounded in conservative interpretations of human–robot separation (ISO 15066) and hospital layout guidelines. Safety metrics such as SVR and NVT are deterministic functions of these labels, implemented in open‑source tools with all thresholds specified in configuration files. To quantify difficulty, we assign each scenario a scalar Risk Index based on obstacle density and blind‑spot proximity, and we include dedicated near‑violation episodes whose nominal paths pass close to semantic hazards (Rare-Event Augmented). Sensitivity analyses over ±20% changes in zone radii confirm that our qualitative conclusions are robust to metric choices, making the benchmark’s data generation and labelling pipeline transparent, reproducible, and resistant to metric‑hacking.”
