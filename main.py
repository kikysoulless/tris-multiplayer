from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

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
            data = await websocket.receive_text()
            for client in rooms[room_code]:
                if client != websocket:
                    await client.send_text(data)
    except WebSocketDisconnect:
        rooms[room_code].remove(websocket)
        if not rooms[room_code]:
            del rooms[room_code]

@app.get("/")
def root():
    return {"message": "Server WebSocket attivo con supporto stanze"}
