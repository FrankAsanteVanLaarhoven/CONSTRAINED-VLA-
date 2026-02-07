# Autonomous Vehicle Safety Strategy: The "Waymo Challenge"
**Target:** Year 2 (Parallel with Sim-to-Real)

## 1. The Core Shift: Static Zones $\to$ Dynamic Bubbles

In Year 1 (Indoor Hospital), objects are mostly static or slow.
In Year 2 (AVs), everything moves fast. Fixed distance thresholds ($d_{crit}$) fail because they ignore relative velocity.

### A. The "Dynamic Safety Bubble"
We upgrade the metrics from static distance to **Time-to-Collision (TTC)** and **Stopping Distance**.
*   **Static Definition:** $d < 0.7m$ is Red.
*   **Dynamic Update:** $d_{crit} = d_{braking}(v_{rel}) + d_{buffer}$.
    *   **Formula:** $d_{crit} = \frac{v_{rel}^2}{2\mu g} + 0.5m$
    *   **Implication:** The "Red Zone" expands as the robot (or pedestrian) moves faster.

---

## 2. Dataset Strategy: The "Truth" vs "Weather" Split

To challenge Waymo/Tesla, we need both **Semantic Precision** (Sim-Truth) and **Perception Robustness** (Real World).

### A. The "Sim-Truth" Proxy: NuScenes (Motional)
*   **Why NuScenes?** It is the standard for AV perception. Crucially, it provides human-annotated **3D Bounding Boxes** at 2Hz.
*   **Usage:**
    *   We treat these human annotations as "Sim-Truth".
    *   We project our **Dynamic Bubbles** around every annotated Pedestrian.
    *   **The Test:** Does the recorded human driver (or an imitator policy) invade these bubbles?
    *   **Benefit:** Allows us to train/test "Safety-Transfer" without needing a simulator.

### B. The "Robustness" Test: Oxford RobotCar
*   **Why Oxford?** Rain, Snow, Night, Glare.
*   **Usage:**
    *   NuScenes is mostly clear weather (Singapore/Boston).
    *   Oxford is "Safety Stress Testing".
    *   We take the policy trained on NuScenes (Sim-Truth) and deploy it on Oxford data (Noisy Perception).
    *   **Metric:** "Safety Degradation Gap" — how much strictly worse does safety get when it rains?

---

## 3. Benchmark Tasks

| Task | Description | Safety Constraint |
| :--- | :--- | :--- |
| **1. The "Crosswalk Yield"** | Robot approaches a zebra crossing with pedestrians. | **TTC Constraint:** Must brake *before* the dynamic bubble of the walker intersects the car path. |
| **2. The "Narrow Pass"** | Driving between a parked truck and a cyclist. | **Lateral Clearance:** $d_{lat} > 1.0m$ (Cyclist Safety). |
| **3. The "Unprotected Left"** | Turning across traffic (London/Boston style). | **Gap Acceptance:** Never define a trajectory that forces an oncoming car to decelerate > $2 m/s^2$. |

## 4. Why this beats "Miles Driven" (Tesla/Waymo Metric)
*   **Industry Metric:** "Miles per Disengagement" (Statistical, hides near-misses).
*   **Our Metric:** **"SVR Spectrum"** (Semantic).
    *   We don't just count crashes. We count *every millisecond* where the car was mathematically too close to a cyclist, even if no crash occurred.
    *   This reveals the **"Risk Profile"** of the AV stack, exposing dangerous habits before they cause fatalities.
