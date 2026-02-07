import sys
import os
import json
import asyncio
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Path hack to include src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ui.intent_parser import IntentParser
from src.ui.avatar_interface import AvatarInterface

app = FastAPI()

# Serve static client files
app.mount("/client", StaticFiles(directory="src/ui/client", html=True), name="client")

@app.get("/dashboard")
async def get_dashboard():
    with open("src/ui/client/dashboard.html", "r") as f:
        return HTMLResponse(content=f.read())

# State
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()
parser = IntentParser()
avatar = AvatarInterface()

# Models
class VoiceCommand(BaseModel):
    text: str

@app.post("/api/command")
async def process_command(cmd: VoiceCommand):
    """
    Simulates receiving a Voice Command (STT output).
    1. Parses Intent -> UI Config
    2. Generates Avatar Response
    3. Pushes UI update to Frontend via Websocket
    """
    print(f"[Server] Received command: {cmd.text}")
    
    # 1. Generate UI / Parse Special Commands
    if "reset" in cmd.text.lower() and "layout" in cmd.text.lower():
        # Special System Command
        payload = { "type": "RESET_LAYOUT" }
        await manager.broadcast(payload)
        return {"status": "success", "intent": "system_reset"}

    ui_config = parser.parse(cmd.text)
    
    # 2. Generate Avatar Response
    # Mock safety status for now
    safety_status = "SAFE" 
    avatar_resp = avatar.generate_response(ui_config, safety_status)
    
    # payload to frontend
    payload = {
        "type": "UI_UPDATE",
        "config": ui_config,
        "avatar": avatar_resp
    }
    
    # 3. Broadcast
    await manager.broadcast(payload)
    
    return {"status": "success", "intent": ui_config["intent"]}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, maybe handle client-side gestures later
            data = await websocket.receive_text() 
            # If client sends "shake", we clear UI
            if "clear" in data:
                await manager.broadcast({"type": "UI_CLEAR"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
