import subprocess
import time
import webbrowser
import os

processes = []

try:
    # Start each service
    processes.append(subprocess.Popen(["python", "server.py"]))
    time.sleep(2)  # give server time to start

    processes.append(subprocess.Popen(["python", "AI_Source.py"]))
    processes.append(subprocess.Popen(["python", "Visualizer.py"]))
    processes.append(subprocess.Popen(["python", "realtime_equalizer.py"]))

    print("All processes started.")

    # Open UI.html in default browser
    ui_path = os.path.abspath("UI.html")
    webbrowser.open(f"file://{ui_path}")
    print(f"UI opened in browser: {ui_path}")

    print("Press CTRL+C to stop everything.")
    
    # Keep running until user interrupts
    for p in processes:
        p.wait()

except KeyboardInterrupt:
    print("\nShutting down...")
    for p in processes:
        p.terminate()
