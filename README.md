# Safety-Transfer: Sim-to-Real Constraint Satisfaction for Embodied AI

**A Unified Framework for Safe Foundation Models (Hospital -> Humanoid -> Zero-UI).**

This repository implements the "Safety-Transfer" methodology: a rigorous pipeline to enforce semantic safety constraints on VLA (Vision-Language-Action) models using Sim-Truth training and Lagrangian Safety Adapters.

---

## 🚀 Quick Start: The 3 Demos

We have implemented three key prototypes to validate the proposal.

### 1. The Hospital Benchmark (Year 1)
*   **Goal:** Prove "Sim-Truth" generation and Safety Metrics.
*   **Run:** Generates a randomized hospital ward and computes safety scores.
    ```bash
    python3 safety_transfer_hospital/analysis/compare_risk_levels.py
    ```
    *(Output: Stratifies performance by Risk Index Low/Med/High)*

### 2. The Humanoid Pilot (Year 2)
*   **Goal:** Prove "3D Safety Capsules" and the Safety Adapter.
*   **Run:** Simulates a robot arm attempting to crash into a patient. The Adapter intervenes.
    ```bash
    python3 safety_transfer_humanoid/scenarios/bedside_handoff.py
    ```
    *(Output: "SUCCESS: Adapter prevented collision (Actual Margin > 0)")*

### 3. The Holodeck Dashboard (Year 3+)
*   **Goal:** Prove "Minority Report" style interaction (Drag-and-Drop, Intent-Based).
*   **Run:** A full "Command Center" with Stage Manager and Voice Control.
    ```bash
    # Terminal 1: Start Server
    uvicorn src.ui.server:app --reload --port 8000 --host 0.0.0.0
    
    # Browser: Open http://localhost:8000/dashboard
    ```
    *(Interaction: Drag panels from the sidebar. Say "Reset Layout" to restore default.)*

---

## 📦 Installation

Requirements are frozen in `requirements.txt`.
```bash
pip install -r requirements.txt
```
*(Note: Requires minimal dependencies: numpy, torch, fastapi, uvicorn, websockets)*

---

---

## 🔧 Advanced Configuration (Phase 15 Features)

### Real-Time D-ID Avatar
To enable the **Real** D-ID video stream instead of the mock:
1.  Get an API key from [D-ID Studio](https://studio.d-id.com/).
2.  Edit `.env`:
    ```bash
    DID_API_KEY="your_key_here"
    ```
3.  Restart the server. The dashboard will now stream video.

### Gesture Control
*   Click the **Camera Icon (📷)** in the sidebar to enable.
*   **Wave your hand** vigorously to trigger a "Layout Reset."

### Isaac Sim Bridge (Sim2Val)
To export the current hospital world to NVIDIA Omniverse (USD):
```bash
python3 src/simulation/isaac_bridge.py
```
*(Creates `exports/usd/hospital_scenario.usda`)*

## 🎮 Open-World Digital Twin (Phase 16)
The Dashboard now features a **Three.js Voxel Engine**.
1.  **3D Viewport**: The center panel is now a live 3D render.
    *   **Controls**: Left-Click to Rotate, Right-Click to Pan, Scroll to Zoom.
2.  **Virtual Kinetics**:
    *   Enable the Camera (📷).
    *   **Raise your hand** to see the Robot's arm move in 3D space (Telepresence).

---

**Status:** Code Complete. Ready for Proposal Submission.
