
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rooms = {}

@app.websocket("/ws/{room_code}")
async def websocket_endpoint(websocket: WebSocket, room_code: str):
    await websocket.accept()

    if room_code not in rooms:
        rooms[room_code] = []

    rooms[room_code].append(websocket)

    try:
        while True:
            data = await websocket.receive_json()

            # JOIN / CREATE HANDLING
            if data.get("type") == "create_room":
                await websocket.send_json({"type": "room_created", "roomId": room_code})

            elif data.get("type") == "join_room":
                await websocket.send_json({"type": "room_joined", "roomId": room_code})
                for client in rooms[room_code]:
                    if client != websocket:
                        await client.send_json({"type": "opponent_joined"})

            # GAME MOVES
            elif data.get("type") == "move":
                for client in rooms[room_code]:
                    if client != websocket:
                        await client.send_json(data)

            # ROUND RESET
            elif data.get("type") == "reset_round":
                for client in rooms[room_code]:
                    await client.send_json({"type": "reset_round"})

            # TOTAL RESET / RESET SFIDE
            elif data.get("type") == "reset_game":
                for client in rooms[room_code]:
                    await client.send_json({"type": "reset_game"})

    except WebSocketDisconnect:
        rooms[room_code].remove(websocket)
        if not rooms[room_code]:
            del rooms[room_code]

@app.get("/")
def root():
    return {"message": "Server WebSocket attivo e pronto."}
