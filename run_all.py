import subprocess
import time

processes = []

try:
    processes.append(subprocess.Popen(["python", "server.py"]))
    time.sleep(2)

    processes.append(subprocess.Popen(["python", "realtime_equalizer.py"]))
    processes.append(subprocess.Popen(["python", "AI_Source.py"]))
    processes.append(subprocess.Popen(["python", "Visualizer.py"]))

    print("All processes started. Open http://localhost:8000 in your browser.")
    print("Press CTRL+C to stop.")

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopping processes...")
    for p in processes:
        p.terminate()
