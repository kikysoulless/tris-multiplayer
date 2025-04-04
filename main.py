from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Permette le connessioni da qualsiasi origine (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for client in clients:
                if client != websocket:
                    await client.send_text(data)
    except Exception:
        clients.remove(websocket)

@app.get("/")
def root():
    return {"message": "Server WebSocket attivo per il gioco Tris"}

# Per eseguire in locale (opzionale se usi render.com)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
