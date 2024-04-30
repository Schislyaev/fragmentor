from fastapi import WebSocket
from typing import List, Dict
from functools import lru_cache
import websockets
import json
from core.settings import settings
from services.helpers import generate_random_string
from urllib.parse import quote_plus
from services.security import create_access_token


class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

    async def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


async def send_message_to_websocket(status: str, booking_id: int):
    from db.models.booking import Booking
    booking = await Booking.get_booking_by_booking_id(booking_id)
    trainer_id = str(booking.trainer.user_id)
    access_token = create_access_token(
        data={
            'id': trainer_id,
        }
    )
    uri = (f'ws://{settings.host}:{settings.port}'
           f'/api/v11/ws/{generate_random_string(5)}?token={quote_plus(access_token)}')

    async with websockets.connect(uri, timeout=300) as websocket:
        message = json.dumps({
            'type': 'update_status',
            'booking_status': status,
            'booking_id': booking_id
        })

        await websocket.send(message)
        # await websocket.close()


@lru_cache()
def get_websocket() -> WebSocketManager:
    return WebSocketManager()
