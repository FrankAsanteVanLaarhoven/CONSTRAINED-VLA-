import json
import random

class IntentParser:
    """
    Simulates the AI-Native 'Intent-to-Widget' pipeline.
    In a real deployment, this would call Gemini 1.5 Pro to parse semantic intent.
    Here, we use keyword heuristics to demonstrate the 'Generative UI' concept.
    """
    
    def parse(self, user_command: str):
        """
        Input: Natural Language string (e.g., "Hand it to me gently")
        Output: JSON dict defining the Ephemeral UI.
        """
        print(f"[LLM] Parsing intent: '{user_command}'...")
        
        ui_config = {
            "intent": "unknown",
            "widgets": [],
            "safety_overlay": [],
            "avatar_emotion": "neutral"
        }
        
        # Rule-based Mock for Prototype
        cmd = user_command.lower()
        
        if "gently" in cmd or "precision" in cmd:
            ui_config["intent"] = "precision_manipulation"
            ui_config["widgets"] = [
                {"type": "slider", "label": "Max Force", "range": [0, 5], "default": 1.0, "unit": "N"},
                {"type": "slider", "label": "Velocity Limit", "range": [0, 1], "default": 0.1, "unit": "m/s"},
                {"type": "toggle", "label": "Haptic Feedback", "default": True}
            ]
            ui_config["safety_overlay"] = ["force_vector_arrows"]
            ui_config["avatar_emotion"] = "focused"
            
        elif "fast" in cmd or "hurry" in cmd:
            ui_config["intent"] = "rapid_transit"
            ui_config["widgets"] = [
                {"type": "button", "label": "Confirm High Speed", "color": "red"},
                {"type": "gauge", "label": "TTC Prediction", "display": "graph"}
            ]
            ui_config["safety_overlay"] = ["dynamic_braking_corridor"]
            ui_config["avatar_emotion"] = "alert"
            
        elif "patient" in cmd or "handoff" in cmd:
            ui_config["intent"] = "medical_handoff"
            ui_config["widgets"] = [
                {"type": "status_indicator", "label": "Patient Capsule", "state": "active"},
                {"type": "button", "label": "Release Grip", "icon": "hand-open"}
            ]
            ui_config["safety_overlay"] = ["patient_safety_capsule_3d"]
            ui_config["avatar_emotion"] = "empathetic"
            
        return ui_config
