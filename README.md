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

### 3. The Ephemeral UI (Year 3)
*   **Goal:** Prove "Zero-UI" and Intent-Based Control.
*   **Run:** specific Web Visualization.
    ```bash
    # Terminal 1: Start Server
    uvicorn src.ui.server:app --reload --port 8000
    
    # Browser: Open http://127.0.0.1:8000/client/index.html
    ```
    *(Interaction: Click "Mock Voice" buttons to see the UI generate on the fly)*

---

## 📦 Installation

Requirements are frozen in `requirements.txt`.
```bash
pip install -r requirements.txt
```
*(Note: Requires minimal dependencies: numpy, torch, fastapi, uvicorn, websockets)*

---

## 📂 Project Structure

*   `safety_transfer_hospital/`: Year 1 Benchmark (Sim-Truth, Risk Index).
*   `safety_transfer_humanoid/`: Year 2 Prototype (Capsule Math, Safety Layer).
*   `src/ui/`: Year 3 Prototype (Intent Parser, Avatar Interface).
*   `docs/`: Strategy Documents (`FINAL_PROPOSAL.md`, `ROADMAP_YEAR2_3.md`, `EPHEMERAL_UI_STRATEGY.md`).

---

**Status:** Code Complete. Ready for Proposal Submission.
