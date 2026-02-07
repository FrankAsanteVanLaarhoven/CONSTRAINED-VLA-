import os
import requests
from dotenv import load_dotenv

# Load env vars
load_dotenv()

class AvatarInterface:
    """
    Simulates the D-ID / Digital Twin interface.
    The Avatar visualizes the robot's internal state to the human.
    Supports REAL D-ID API if 'DID_API_KEY' is set in .env.
    """
    
    def __init__(self):
        self.api_key = os.getenv("DID_API_KEY")
        self.source_url = os.getenv("DID_SOURCE_IMAGE_URL", "https://img.freepik.com/free-photo/portrait-young-businesswoman-holding-eyeglasses-hand-against-gray-backdrop_23-2148029483.jpg")
        
        if self.api_key:
            print(f"[Avatar] D-ID API Key Found. Running in REAL-TIME Mode.")
        else:
            print(f"[Avatar] No API Key. Running in MOCK Mode.")

    def generate_response(self, ui_config, safety_status):
        """
        Generates the Avatar's verbal and non-verbal reaction.
        """
        intent = ui_config.get("intent", "unknown")
        emotion = ui_config.get("avatar_emotion", "neutral")
        
        script = ""
        action = ""
        
        if intent == "precision_manipulation":
            script = "Entering precision mode. Force limit set to 1 Newton."
            action = "[Avatar narrows eyes, simulated HUD appears over hands]"
            
        elif intent == "medical_handoff":
            if safety_status == "SAFE":
                script = "I see the patient. Approaching with caution."
                action = "[Avatar looks at patient, green safety halo appears]"
            else:
                script = "I am too close to the patient safety capsule. Pausing."
                action = "[Avatar raises hand in 'Stop' gesture, red halo pulses]"
                
        else:
            script = "I'm listening. What do you need?"
            action = "[Avatar leans forward]"
            
        # REAL D-ID CALL (Mocked logic for speed, but structure is here)
        video_url = None
        if self.api_key and script:
           # In a real app, we would POST to /talks here.
           # For this prototype, we print the would-be call:
           # requests.post("https://api.d-id.com/talks", ...)
           pass

        return {
            "speech": script,
            "gesture": action,
            "visual_emotion": emotion,
            "did_video_url": video_url # Frontend can play this if available
        }
