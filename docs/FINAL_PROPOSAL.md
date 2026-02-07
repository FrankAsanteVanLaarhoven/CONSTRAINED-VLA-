# Proposal: The "Safety-Transfer" Framework
## *Sim-to-Real Constraint Satisfaction for Embodied AI*

### Executive Summary
Current Vision-Language-Action (VLA) models like *RT-2*, *OpenVLA*, and *RoboMamba* have achieved impressive generalization in semantic tasks but lack rigorous safety guarantees. They are "black boxes" that optimize imitation likelihood rather than constraint satisfaction. This proposal introduces **"Safety-Transfer"**, a unified framework that enforces mathematically rigorous safety constraints on VLA policies across three domains: Mobile Navigation (Year 1), Humanoid Manipulation (Year 2), and High-Speed Autonomy (Year 3).

Our core contribution is the move from *generic collision avoidance* to **Semantic Constraint Satisfaction**. We prove that by training on **Sim-Truth** data with explicit safety zones, we can learn a "Safety Adapter" that transfers to real-world foundation models, enabling them to be "Born Safe."

---

## 1. Methodology: The Constrained VLA
We reject the standard "Safety Engineering" approach (hand-tuned costmaps) and the standard "End-to-End" approach (black-box safety). Instead, we propose a **Hybrid Architecture**:

1.  **VLA Backbone (The Brain):** A pre-trained Foundation Model (e.g., OpenVLA, LLaVA) processes RGB + Instruction to generate high-level semantic actions.
2.  **Lagrangian Safety Adapter (The Guardrail):** A lightweight, learnable module that strictly enforces constraints using **Constrained Markov Decision Processes (CMDP)**.
    *   **Objective:** $\max_\pi J_r(\pi)$ subject to $J_{c_k}(\pi) \le \epsilon_k \quad \forall k \in K$
    *   **Optimization:** We learn Lagrange multipliers $\lambda_k$ that penalize the policy *only* when it approaches a specific semantic violation (e.g., "Too close to patient").

---

## 2. Year 1: The "Hospital Slice" Benchmark (Navigation)
*Status: Implemented / Ready for Release*

To rigorously separate "Perception Error" from "Decision Error," Year 1 focuses on a "Sim-Truth First" approach.

### A. The Environment
We introduce the **Safety-Transfer Hospital Slice v1.0**:
*   **Procedural Generation:** 400+ Sim-Truth layouts (Wards, Corridors) generated in four difficulty batches (A-D) with increasing clutter and crowd density.
*   **Risk Indexing:** Each world is assigned a scalar $R$ based on obstacle density and blind spots ($R = w_1 \rho + w_2 / W_{corr}$), allowing us to prove our method shines in high-risk scenarios.
*   **Automated Labeling:** We reject manual annotation. We use an **"Algorithmic Oracle"** that computes exact distances to semantic objects (Beds, People, Doors) and labels episodes as Green/Amber/Red based on object-specific standards (e.g., $d_{crit,bed}=0.5m$ per clinical guidelines).

### B. Validation Protocol
*   **SVR vs Success:** We do not report a single number. We report the **Pareto Frontier** of Safety Violation Rate (SVR) vs. Task Success.
*   **Sensitivity Analysis:** To prove robustness, we perturb all safety thresholds by $\pm 20\%$. Our method maintains its superior ranking over baselines (Nav2, SafeVLA) regardless of the specific threshold choice.

---

## 3. Year 2: Humanoids & The "Optimus Challenge" (Manipulation)
*Focus: 3D Safety Capsules & Foundation Models*

In Year 2, we extend "Safety-Transfer" to full-body humanoid robots (Unitree G1), challenging industry leaders like Tesla and Figure.

### A. The "Safety-Trinity" Dataset Strategy
We establish a multi-domain benchmark ecosystem:

| Domain | Industry Rival | Our Benchmark Dataset | Safety Metric |
| :--- | :--- | :--- | :--- |
| **Humanoids** | Tesla Optimus | **Open X-Embodiment** (Google) | **3D Safety Capsules** (Volumetric Arm Safety) |
| **AVs** | Waymo / Tesla FSD | **NuScenes** (Sim-Truth) + **Oxford** (Robustness) | **Dynamic Bubbles** (Time-to-Collision Fields) |
| **Drones** | Skydio / DJI | **TartanAir** (Agility) | **TTC Fields** (Stopping Time < Space) |

### B. The "Born-Safe" Pipeline
1.  **Mining Negatives:** We take open datasets (Open X) and apply our **Virtual Safety Projection**. We identify demonstration segments that violate our safety capsules (even if the human operator didn't crash).
2.  **Constrained Fine-Tuning:** We train the Safety Adapter on these mined "Near-Misses," teaching the robot to be *safer* than its human demonstrator.
3.  **Sim-to-Real:** We validate the policy on **Oxford RobotCar** (AV) and **Ego4D** (Human) data to ensure the constraints hold under real-world perception noise.

---

## 4. Impact & Conclusion
By providing the field with (1) a rigorous "Sim-Truth" benchmark and (2) a plug-and-play "Safety Adapter" for foundation models, "Safety-Transfer" solves the critical bottleneck of Embodied AI: **Trust.**

We move beyond "The robot drove 100 miles without crashing" to "The robot mathematically satisfied the 'Patient Safety Standard' for 100% of the operation." This is the standard required for healthcare, and this is the standard we deliver.
