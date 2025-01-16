from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import json
from sqlalchemy.ext.asyncio import AsyncSession
from models.users import *
from database import get_db_session
from string import ascii_uppercase, digits
from random import choice
from collections import defaultdict
import time

multiplayer_router = APIRouter(
    prefix="/multiplayer"
)

class ConnectionManager:
    def __init__(self, room_code: str):
        self.active_connections: list[WebSocket] = []
        self.room_code: str = room_code
        self.matches = defaultdict(set)
        self.checkboxes = set()
        self.sliders = defaultdict()
        self.previous_matches = set()

    def add_checkbox(self, filter: str):
        self.checkboxes.add(filter)

    def remove_checkbox(self, filter: str):
        try:
            self.checkboxes.remove(filter)

        except:
            pass

    def modify_sliders(self, filter: str, value: int):
        self.sliders[filter] = value

    async def add_match(self, game: int, username: str):
        self.matches[game].add(username)

        if (len(self.matches[game]) == len(self.active_connections)) and game not in self.previous_matches:
            await self.broadcast(json.dumps({"type": "message", "content": {"message": f"Match found!", "game": game, "event": "match"}, "timestamp": int(time.time() * 1000)}))
            self.previous_matches.add(game)
 
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

connectionManagers: dict[str, ConnectionManager] = {}

def generate_room_code():
    code = "".join([choice((ascii_uppercase + digits).replace("0", "")) for i in range(6)])
    if code not in connectionManagers:
        return code
    
    return generate_room_code()

@multiplayer_router.websocket("/create-room/{username}")
async def create_room(websocket: WebSocket, username: str, session: AsyncSession = Depends(get_db_session)):
    #print("start")
    #account = await get_account(account=AccountRequest(username=username, email=None, uid=None), session=session)
    #print(account)
    #if account is None:
    #    return {"success": False, "message": "invalid credentials"}
    #else:
        #account = account.model_dump()
        #username = account["username"]
    manager = ConnectionManager(room_code=generate_room_code())
    connectionManagers[manager.room_code] = manager
    await manager.connect(websocket)
    await manager.send_personal_message(message=json.dumps({
        "type": "message", 
        "username": username, 
        "content": {
            "message": f"Room created! Others can join by entering your room code: {manager.room_code}", 
            "event": "create_room"
        },
        "timestamp": int(time.time() * 1000),
    }), websocket=websocket)
    try:
        while True:
            data = await websocket.receive_text()
            parsed_data = json.loads(data)
            if parsed_data["type"] == "match":
                await manager.add_match(game=parsed_data["content"]["game"], username=username)
                continue
            
            elif parsed_data["type"] == "filter":
                manager.matches = defaultdict(set)
                manager.previous_matches = set()
            
            elif parsed_data["type"] == "checkbox":
                if parsed_data["content"]["value"]:
                    manager.add_checkbox(parsed_data["content"]["id"])
                
                else:
                    manager.remove_checkbox(parsed_data["content"]["id"])

            elif parsed_data["type"] == "slider":
                manager.modify_sliders(parsed_data["content"]["id"], parsed_data["content"]["value"])

            # to change
            await manager.broadcast(data)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(json.dumps({"username": username, "info_type": "leave"}))



@multiplayer_router.websocket("/join-room")
async def join_room(websocket: WebSocket, room_code: str, username: str):
    manager = connectionManagers.get(room_code, None)

    if manager is not None:
        await manager.connect(websocket)
    
    else:
        await websocket.accept()
        await websocket.send_text(json.dumps({"success": False, "message": "Room does not exist"}))
        await websocket.close(reason="invalid room")
        return {"success": False, "message": "room does not exist"}

    await manager.broadcast(json.dumps({"success": True, "type": "message", "username": username, "content": {"message": f"{username} has joined the room!", "event": "join"}, "timestamp": int(time.time() * 1000)}))
    await manager.send_personal_message(json.dumps({
        "type": "joinData", 
        "content": {
            "checkboxList": list(manager.checkboxes),
            "sliderList": manager.sliders
    }}), websocket=websocket)

    try:
        while True:
            data = await websocket.receive_text()
            parsed_data = json.loads(data)
            if parsed_data["type"] == "match":
                await manager.add_match(game=json.loads(data)["content"]["game"], username=username)
                continue

            elif parsed_data["type"] == "checkbox":
                if parsed_data["content"]["value"]:
                    manager.add_checkbox(parsed_data["content"]["id"])
                    
                elif (parsed_data["content"]["value"] == False):
                    manager.remove_checkbox(parsed_data["content"]["id"])

            
            elif parsed_data["type"] == "slider":
                manager.modify_sliders(parsed_data["content"]["id"], parsed_data["content"]["value"])

            # to change
            await manager.broadcast(data)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(json.dumps({"type": "message", "username": username, "content": {"message": f"{username} has left the room!", "event": "leave"}, "timestamp": int(time.time() * 1000)}))