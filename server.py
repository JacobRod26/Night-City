import socketio
from fastapi import FastAPI
from fastapi.responses import FileResponse

# --- Setup ---
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = FastAPI()
app.mount("/socket.io", socketio.ASGIApp(sio))

# Serve the UI
@app.get("/")
async def root():
    return FileResponse("UI.html")

# --- Events ---
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.on("start_eq")
async def start_eq(sid, data):
    print(f"EQ start requested: {data}")
    await sio.emit("begin_stream", data)

@sio.on("user_input")
async def user_input(sid, data):
    print("User input:", data)
    await sio.emit("user_input", data)

@sio.on("eq_data")
async def eq_data(sid, data):
    await sio.emit("eq_data", data)

@sio.on("ai_instructions")
async def ai_instructions(sid, data):
    await sio.emit("ai_instructions", data)

@sio.on("frame")
async def frame(sid, data):
    await sio.emit("frame", data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
