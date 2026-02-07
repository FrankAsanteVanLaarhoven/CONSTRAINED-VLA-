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
            
        # REAL D-ID CALL
        video_url = None
        if self.api_key and script:
            try:
                # 1. Create Talk
                print(f"[Avatar] Generating D-ID Video for: '{script[:20]}...'")
                headers = {
                    "Authorization": f"Basic {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "script": {"type": "text", "input": script},
                    "source_url": self.source_url # Uses env var or default
                }
                
                resp = requests.post("https://api.d-id.com/talks", json=payload, headers=headers)
                if resp.status_code == 201:
                    talk_id = resp.json().get("id")
                    
                    # 2. Poll for Completion (Simple Blocking for Demo)
                    status = "created"
                    while status not in ["done", "error"]:
                        import time
                        time.sleep(1) # Wait 1s
                        stat_resp = requests.get(f"https://api.d-id.com/talks/{talk_id}", headers=headers)
                        data = stat_resp.json()
                        status = data.get("status")
                        if status == "done":
                            video_url = data.get("result_url")
                            print(f"[Avatar] Video Ready: {video_url}")
                else:
                    print(f"[Avatar] D-ID Error {resp.status_code}: {resp.text}")
                    
            except Exception as e:
                print(f"[Avatar] Exception: {e}")

        return {
            "speech": script,
            "gesture": action,
            "visual_emotion": emotion,
            "did_video_url": video_url # Frontend will auto-play this
        }
