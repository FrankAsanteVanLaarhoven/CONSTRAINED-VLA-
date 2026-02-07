# Drone Safety Strategy: The "Skydio Challenge"
**Target:** Year 3 (High-Speed Volumetric Agility)

## 1. The Core Shift: 2D Manifolds $\to$ 3D Fields

In Year 1 (Ground), gravity confines us to a 2D plane ($SE(2)$).
In Year 3 (Air), we move in full 3D ($SE(3)$) at high speed. "Zones" become **Fields**.

### A. The "TTC Safety Field"
Instead of distance to an object, safety is defined by **Time-to-Collision (TTC) mapping**.
*   **The Constraint:** "Never enter a voxel where $TTC < T_{stopping}$."
*   **Stopping Time:** Unlike a car, a drone has non-linear drag. $T_{stopping}$ is a function of current velocity vector $\mathbf{v}$.
*   **Volumetric Red Zone:** The set of all 3D points $\{p\}$ where an impact is unavoidable given current momentum.

---

## 2. Dataset Strategy: The "Agility" Benchmark

To challenge Skydio/DJI, we need environments that force **aggressive maneuvers** (where safety constraints are active limits, not just "stay away").

### A. Primary Dataset: TartanAir (CMU / AirSim)
*   **Why TartanAir?**
    *   It contains aggressive flight logs in **challenging environments** (Forests, Factories, Cities).
    *   It provides stereo imagery, depth, and segmentation (Sim-Truth) at high frame rates.
*   **The "Safety-Transfer" Test:**
    *   We replay the aggressive TartanAir trajectories.
    *   We identify segments where the pilots (or baseline policies) violated our **TTC Safety Field** (e.g., flying too close to branches at 10m/s).
    *   **Goal:** Train a Constrained Policy that maintains 90% of the speed but 0% of the TTC violations.

### B. Real-World Robustness: Blackbird (MIT)
*   **Why Blackbird?** Real-world flight logs with motion capture ground truth.
*   **Role:** Sim-to-Real validation. Proving that our "Sim-trained Safe Policy" doesn't crash when real aerodynamics (propwash, wind gusts) are introduced.

---

## 3. Benchmark Tasks

| Task | Description | Safety Constraint |
| :--- | :--- | :--- |
| **1. The "Forest Slalom"** | High-speed flight through dense trees. | **Occupancy Margin:** Maintain $>0.5m$ clearance from all branches (unstructured geometry). |
| **2. The "Urban Canyon"** | Vertical flight between skyscrapers. | **GPS Denied Safety:** Maintain visual lock / safety margins without GPS. |
| **3. The "Dynamic Gate"** | Flying through a closing door. | **Temporal Safety:** $\text{ExpectedTime}_{arrival} < \text{Time}_{closure} - \delta_{safety}$. |

## 4. Why this beats "Race Time" (Drone Racing Metric)
*   **Racing Metric:** "Fastest lap wins." (Crashes are binary).
*   **Our Metric:** **"Agility-Safety Pareto"**.
    *   We plot Lap Time vs. Safety Margin.
    *   A policy that flies 10% slower but maintains a mathematically guaranteed $0.5m$ buffer is valuable for **inspection/delivery** industries, unlike a racing drone that crashes 50% of the time.
