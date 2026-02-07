# Roadmap: Extending Safety-Transfer to Humanoids (Years 2-3)

**Goal:** Evolve the "Sim-Truth" constrained safety framework from 2D mobile robots (Year 1) to full-body Humanoid interaction (Year 3).

---

## Year 2: The Perception Gap (Sim-to-Real)
*Focus: Replacing "God-Mode" Sim-Truth with real-world perception on mobile bases.*

### 1. From Oracle to Vision
*   **Current (Year 1):** `dist = math.hypot(robot, bed)` (Perfect geometric truth).
*   **Year 2 Upgrade:** `dist = perception_pipeline(camera_image)`.
    *   Integrate **Open-Set Object Detectors** (YOLO-World or OWL-ViT) to detect "beds" and "people" visually.
    *   **Validation:** Measure the "Safety Gap"—how much does safety drop when we switch from Sim-Truth to Noisy Visions?
    *   **Mitigation:** Learn *robust* constraint multipliers ($\lambda$) that account for uncertainty bubbles.

### 2. The Oxford Transfer
*   Verify the safety policy on the **Oxford RobotCar** dataset (as defined in `DATASET_STRATEGY.md`) to prove the math holds in unstructured real-world environments.

---

## Year 3: The Humanoid Leap (Unitree G1 / GR00T)
*Focus: 3D Safety Capsules and Manipulation Constraints.*

### 1. 2D Circles $\to$ 3D Capsules
The "Safety Zone" concept extends naturally but adds a dimension.
*   **Year 1:** Red Zone = Circle of radius $r$ on the floor.
*   **Year 3:** Red Zone = **Cylinder/Capsule** volume around the patient.
*   **Why:** A humanoid can be "safe" on the floor (feet far away) but "unsafe" with its arms (swinging near a patient's face).
*   **Metric Update:** $SVR_{3D}$ checks for penetration of the *entire robot skeletal mesh* into the safety volume.

### 2. Policy Backbone: MLP $\to$ VLA
*   **Current (Year 1):** Simple Neural Network (State + Instruction $\to$ Velocity).
*   **Year 3 Upgrade:** Fine-tune a Foundation Model (**OpenVLA**, **RT-2**, or **GR00T**).
    *   **Input:** RGB Video + Language ("Check the IV drip").
    *   **The "Constrained Adapter":** We inject our **Lagrangian Safety Head** (from Notebook 08) as a lightweight adapter on top of the frozen VLA backbone.
    *   **Benefit:** The robot understands semantic nuance ("This is a fragile patient") while our adapter enforces strict math safety.

### 3. The "Manipulation Slice"
*   Extend the benchmark from *Navigation* to *Mobile Manipulation*.
*   **Tasks:** "Approach Bed", "Open Door", "Hand Object to Nurse".
*   **Constraints:**
    *   **Impact limit:** Limit force/velocity near objects.
    *   **Reachability:** Ensure arms never cross into the "Patient Red Volume" dynamically.

---

## 4. The Unified Dataset Ecosystem (Challenging the Giants)

To challenge Tesla (Optimus), Nvidia (GR00T), and Skydio (Drones), we cannot rely on one dataset. We establish the **"Safety-Trinity" Benchmark**:

### A. Humanoids: "The Optimus Challenge"
*Goal: Generalized Manipulation Safety in Unstructured Homes/Hospitals.*
*   **Primary Dataset: Open X-Embodiment (Google DeepMind)**
    *   **Why:** It is the largest open robotic dataset (500+ robot types). It is the standard on which RT-2 and RoboMamba are trained.
    *   **Our Edge:** We apply our **Virtual 3D Safety Capsules** to this likely unsafe data, retraining models to be "Born Safe".
*   **Human-to-Robot Transfer: Ego4D (Episodic Memory)**
    *   **Why:** Tesla trains on human video. Ego4D enables us to learn "socially safe" behaviors (e.g., how humans avoid bumping into each other) from first-person video and transfer it to the robot.

### B. Autonomous Vehicles: "The Waymo Challenge"
*Goal: High-Speed Interaction Safety.*
*   **Dataset: NuScenes (Motional) + Oxford RobotCar**
    *   **Why:** NuScenes provides *annotated 3D bounding boxes* (Sim-Truth equivalent for real world). Oxford provides the raw, messy weather data for robustness.
    *   **Safety Mapping:** The 2D Safety Zones map directly to "Pedestrian Bubbles" and "Vehicle Headway" constraints.

### C. Aerial Drones: "The Skydio Challenge"
*Goal: 3D Volumetric Safety at Speed.*
*   **Dataset: TartanAir (AirSim) / Blackbird**
    *   **Why:** We need high-speed, clutter-rich environments to test reaction times.
    *   **Safety Mapping:**
        *   **Red Zone:** Defined by "Time-to-Collision" (TTC) fields > 0.5s.
        *   **Constraint:** "Never enter a region where stopping distance > available space."

## Summary for Proposal "Future Work"
"While Year 1 establishes the mathematical rigorousness of semantic constraints on mobile bases, Years 2 and 3 scale this to full embodiment. We will lift the 2D 'Safety Zones' into 3D 'Safety Volumes' for Humanoid manipulation (Unitree G1), ensuring that high-DoF arms respect patient safety corridors just as strictly as the mobile base respects navigation limits. The Lagrangian Constrained Policy is architecture-agnostic, allowing us to seamlessly attach it as a 'Safety Adapter' to state-of-the-art VLA backbones like GR00T."
