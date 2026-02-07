class AvatarInterface:
    """
    Simulates the D-ID / Digital Twin interface.
    The Avatar visualizes the robot's internal state to the human.
    """
    
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
            
        return {
            "speech": script,
            "gesture": action,
            "visual_emotion": emotion
        }
