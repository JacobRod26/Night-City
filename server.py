import socketio
import uvicorn
from fastapi import FastAPI

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = FastAPI()
asgi_app = socketio.ASGIApp(sio, app)

@sio.event
async def connect(sid, environ):
    print("Client connected:", sid)

@sio.event
async def disconnect(sid):
    print("Client disconnected:", sid)

# Forward user input to AI
@sio.on("user_input")
async def on_user_input(sid, data):
    print("User input:", data)
    await sio.emit("user_input", data)

# Forward EQ start request to EQ service
@sio.on("start_eq")
async def start_eq(sid, data):
    print(f"EQ start requested for {data.get('filename')}")
    # Broadcast to EQ service (so realtime_equalizer starts generating)
    await sio.emit("begin_stream", data)

# Forward EQ data to AI + Visualizer
@sio.on("eq_data")
async def on_eq_data(sid, data):
    await sio.emit("eq_data", data)

# Forward AI instructions to Visualizer + UI
@sio.on("ai_instructions")
async def on_ai_instructions(sid, data):
    await sio.emit("ai_instructions", data)

# Forward visualizer frames to UI
@sio.on("frame")
async def on_frame(sid, data):
    await sio.emit("frame", data)

if __name__ == "__main__":
    uvicorn.run(asgi_app, host="0.0.0.0", port=8000)
