from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from typing import List
import json
from uuid import uuid4

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f'connected {websocket}')

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, websocket: WebSocket):
        for connection in self.active_connections:
            if connection != websocket:  # Отправляем сообщение всем, кроме отправителя
                await connection.send_text(message)

manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            mes_id = str(uuid4())
            data = await websocket.receive_text()
            print(f"Received: {mes_id} from {websocket}")
            await manager.broadcast(json.dumps({"signal": data}), websocket)  # Изменено, чтобы исключить повторную сериализацию в JSON
            print(f'sent {mes_id} to all')
    except WebSocketDisconnect as e:
        print(f"WebSocket disconnected: {str(e)}")
        manager.disconnect(websocket)
        await manager.broadcast(json.dumps({"type": "notification", "message": "A user has left the chat."}), websocket)

