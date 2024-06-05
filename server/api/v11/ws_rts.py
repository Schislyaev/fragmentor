from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Query, Depends
from services.security import check_user_get_id
from services.web_socket import get_websocket, WebSocketManager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
        websocket: WebSocket,
        token: str = Query(...),
        manager: WebSocketManager = Depends(get_websocket)
):
    user_id = await check_user_get_id(token)
    await manager.connect(websocket, user_id)

    try:
        while True:
            data = await manager.active_connections[user_id].receive_json()

            if data["type"] == "setID":
                await websocket.send_json({"type": "yourID", "yourID": user_id})
                await manager.notify_users()

            elif data["type"] == "callUser":
                user_to_call = data["userToCall"]
                signal_data = data["signalData"]
                from_user = data["from"]

                if user_to_call in manager.active_connections:
                    await manager.active_connections[user_to_call].send_json({"type": "hey", "signal": signal_data, "from": from_user})

                manager.cache = []

            elif data["type"] == "acceptCall":
                to_user = data["to"]
                signal = data["signal"]

                if to_user in manager.active_connections:
                    await manager.active_connections[to_user].send_json({"type": "callAccepted", "signal": signal})

            elif data["type"] == "endCall":
                await manager.broadcast({"type": "endCall"}, user_id)

    except WebSocketDisconnect:
        if user_id:
            await manager.disconnect(user_id)
            await manager.notify_users()
            manager.cache = []

        # Notify the other party if the user was in a call
            await manager.broadcast({"type": "endCall"}, user_id)


