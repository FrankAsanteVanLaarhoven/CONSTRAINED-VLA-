# Ephemeral UI Strategy: The "Zero-UI" Control Plane
**Target:** Year 3 (Human-Robot Interaction Layer)

> "User interfaces are going to go away... The system adapts to your intent, not a fixed layout." — Eric Schmidt

## 1. The Core Philosophy: From Static to Generative

Traditional Robot Control Panels (ROS Rviz, cockpits) are **Static**. They show every button, every sensor, all the time. This is overwhelming and rigid.

**The Ephemeral UI** is **Generative**. It exists *only* when needed, and contains *only* what is relevant to the current intent.

### The "Intent-to-Widget" Pipeline
1.  **Input:** Multimodal (Voice, Gaze, Gesture).
    *   *User:* "Hand me the scalpel, but be careful of the IV line."
2.  **Intent Analysis (Gemini 1.5 Pro):**
    *   Context: `Medical_Handoff`
    *   Critical Param: `Force_Limit`, `Precision_Mode`
    *   Constraint: `Avoid_Object(IV_Line)`
3.  **Generative UI render:**
    *   The system DOES NOT show a joystick.
    *   The system spawns a **floating slider** for "Grip Force" and a **Red Augmented Reality Zone** around the IV line.
    *   Once the task is done, the UI dissolves.

---

## 2. The Avatar as the Interface (D-ID / Live Portrait)

We replace the "Terminal" with a **Digital Humanoid Twin**.

### A. The "Mirror" Concept
*   **The Problem:** How does a user know what the robot is thinking?
*   **The Solution:** The Avatar (displayed on a screen or AR glasses) mirrors the robot's *internal state*.
*   **Example:**
    *   *Robot State:* "Detecting collision risk."
    *   *Avatar:* Looks concerned, points to the patient's arm, and verbalizes: "I am too close to the patient. Adjusting trajectory."

### B. Technical Integration
*   **Input:** User Voice $\to$ STT $\to$ LLM.
*   **Processing:** LLM generates (1) Robot Command, (2) Avatar Script, (3) Emotional State.
*   **Output:** D-ID Avatar speaks the response while the Robot executes the command.

---

## 3. Implementation Roadmap

### Phase A: The "Intent Parser" (Backend)
*   **Component:** `src/ui/intent_parser.py`
*   **Function:** Takes natural language. Returns a JSON definition of the UI widgets needed *right now*.
    *   Input: "Move faster." $\to$ Output: `{ "widgets": ["Speed_Slider"], "defaults": { "speed": 1.5 } }`

### Phase B: The "Spatial Canvas" (Frontend)
*   **Component:** **Apple Vision Pro / Meta Quest** (or WebXR for prototype).
*   **Function:** Renders the widgets in 3D space relative to the user's hand.

### Phase C: Integration with Safety Layer
*   The Ephemeral UI is the **Command Center** for the **Safety Adapter**.
*   If the user says "Override safety," the Avatar resists: "I cannot do that. The patient capsule is active." (Verbalizing the `SafetyLayer` penalty).

## 4. Why this is SOTA
*   **Current SOTA:** Teleoperation using joysticks or fixed GUIs.
*   **Our SOTA:** **No-UI.** The interface is a conversation. The "Controls" are generated strictly for the micro-task at hand and then vanish.
