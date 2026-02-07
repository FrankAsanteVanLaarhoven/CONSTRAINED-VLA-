import sys
import os
import json

# Path hack
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ui.intent_parser import IntentParser
from src.ui.avatar_interface import AvatarInterface

def demo_ephemeral_ui():
    print("=== DEMO: Ephemeral UI & Avatar Control (Zero-UI) ===\n")
    
    parser = IntentParser()
    avatar = AvatarInterface()
    
    # Mock User Interactions
    scenarios = [
        "Please hand the scalpel to the patient gently.",
        "Move fast to the emergency room!",
        "System check."
    ]
    
    for cmd in scenarios:
        print(f"USER: \"{cmd}\"")
        print("-" * 40)
        
        # 1. Parse Intent (Generate UI)
        ui_config = parser.parse(cmd)
        print(f"GEN_UI: Spawning {len(ui_config['widgets'])} widgets for '{ui_config['intent']}'")
        print(f"        Widgets: {[w['label'] for w in ui_config['widgets']]}")
        print(f"        AR Overlay: {ui_config['safety_overlay']}")
        
        # 2. Simulate Safety Check (Mock)
        safety_status = "SAFE"
        if "patient" in cmd:
            # Simulate a momentary risk
            print("SAFETY_LAYER: Checking Patient Capsule... OK.")
        
        # 3. Avatar Response
        response = avatar.generate_response(ui_config, safety_status)
        print(f"AVATAR ({response['visual_emotion']}): {response['gesture']}")
        print(f"AVATAR SPEAKS: \"{response['speech']}\"")
        
        print("=" * 40 + "\n")

if __name__ == "__main__":
    demo_ephemeral_ui()
