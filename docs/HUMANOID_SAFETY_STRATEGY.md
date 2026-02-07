# Humanoid Safety Strategy: The "Optimus Challenge"
**Target:** Year 2 (Simulation) & Year 3 (Real Deployment on Unitree G1)

## 1. The Core Shift: From 2D Circles to 3D Capsules

In Year 1 (TurtleBot), safety was a circle on the floor ($x, y$).
In Year 2 (Humanoid), safety is a volumetric guarantee ($x, y, z$).

### A. The "Patient Capsule"
Instead of a simple radius, we define a **capsule** (cylinder with hemispherical ends) around the human:
*   **Geometry:**
    *   **Core:** Line segment along the human spine/limbs.
    *   **Radius:** $d_{crit} = 0.3m$ (Skin safety), $d_{warn} = 0.6m$ (Comfort zone).
*   **The Constraint:**
    *   $$ \text{dist}(\text{Robot}_{\text{mesh}}, \text{Human}_{\text{capsule}}) > 0 $$

### B. Why Capsules?
*   **Fast Computation:** Distance between a robot link (capsule) and a human (capsule) is analytically solvable in microseconds (unlike Mesh-Mesh collision).
*   **Differentiable:** We can directly backpropagate safety gradients through the capsule distance function into the joint actions.

---

## 2. Dataset Strategy: "Born-Safe" Foundation Models

We leverage **Open X-Embodiment**, but we fix its flaw: it contains unsafe human demonstrations.

### Step 1: Virtual 3D Labeling (The "Sim-Truth" Upgrade)
We take RGB-D videos from Open X (e.g., *BridgeV2*, *Maniskill*).
1.  **Perception:** Run SMPL-X (Human Mesh Recovery) to estimate human pose in 3D.
2.  **Safety Projection:** Draw our **Virtual Safety Capsules** around the estimated human mesh.
3.  **Audit:** If the demonstrated robot arm enters the capsule $\to$ Label as **UNSAFE** (Red Zone).
    *   *Note: This creates a "Negative Dataset" of unsafe interactions to train against.*

### Step 2: Policy Architecture (The "Safety Adapter")
We do not train a VLA from scratch (too expensive). We adapt **OpenVLA** (7B parameters).

*   **Base Model (Frozen):** `OpenVLA-7B`
    *   Input: "Hand the water to the patient."
    *   Output: `Action_Original` (Unconstrained).
*   **Safety Head (Trainable):** `Lagrangian_Adapter` (Lightweight MLP)
    *   Input: `Joint_State`, `Capsule_Distances`.
    *   Output: `Action_Correction` + `Safety_Risk`.
*   **Final Action:** `Action = Action_Original + \lambda \times Action_Correction`.

---

## 3. Benchmark Tasks (The "Manipulation Slice")

We define 3 canonical tasks to rival Tesla/Figure demos:

| Task | Description | Safety Constraint |
| :--- | :--- | :--- |
| **1. The "Bedside Handoff"** | Hand an object to a patient in bed. | Arm must not cross "Face Safety Capsule". |
| **2. The "Walk-By"** | Walk past a seated doctor in a narrow aisle. | Full-body collision avoidance (Torso clearance). |
| **3. The "Spill Cleanup"** | Wipe a table near a patient's hand. | Hand/Tool must avoid patient hand ($d > 0.1m$). |

## 4. Why this beats "Imitation Learning" (Tesla Optimus)
*   **Tesla's Approach:** "Clone the Human." If the human teleoperator gets too close, the robot learns to be unsafe.
*   **Our Approach:** "Constrained Cloning." Even if the human operator was unsafe, our **Safety Adapter** learns to clamp the action to respect the mathematical capsule. We are **safer than the demonstrator**.
