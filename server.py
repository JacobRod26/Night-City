import socketio
from fastapi import FastAPI
import uvicorn

sio = socketio.AsyncServer(async_mode = "asgi", cors_allowed_origins = "*")
app = FastAPI()
asgi_app = socketio.ASGIApp(sio, other_asgi_app = app)

@sio.event
async def connect(sid, environ):
    print("Client connected:", sid)

@sio.event
async def disconnect(sid):
    print("Client disconnected:", sid)

@sio.event
async def user_input(sid, payload):
    await sio.emit("user_input", payload)

@sio.event
async def eq_data(sid, payload):
    await sio.emit("eq_data", payload)

@sio.event
async def ai_instructions(sid, payload):
    await sio.emit("ai_instructions", payload)

@sio.event
async def frame(sid, payload):
    await sio.emit("frame", payload)

if __name__ == "__main__":
    uvicorn.run(asgi_app, host = "0.0.0.0", port = 8000)