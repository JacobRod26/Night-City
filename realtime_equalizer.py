import socketio
import asyncio
import random

sio = socketio.AsyncClient()
streaming = False

def generate_percentages():
    values = [random.random() for _ in range(4)]
    total = sum(values)
    normalized = [v / total for v in values]
    return {
        'drums': round(normalized[0], 3),
        'bass': round(normalized[1], 3),
        'other': round(normalized[2], 3),
        'vocals': round(normalized[3], 3)
    }

@sio.event
async def connect():
    print("Connected to server (EQ Service)")

@sio.event
async def disconnect():
    print("Disconnected (EQ Service)")

@sio.on("begin_stream")
async def on_begin_stream(data):
    global streaming
    print(f"Starting EQ stream for {data.get('filename')}")
    streaming = True

async def main():
    await sio.connect("http://localhost:8000")
    chunk = 0
    while True:
        if streaming:
            chunk += 1
            bands = generate_percentages()
            await sio.emit("eq_data", {"chunk": chunk, "bands": bands})
            await asyncio.sleep(0.1)
        else:
            await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main())
