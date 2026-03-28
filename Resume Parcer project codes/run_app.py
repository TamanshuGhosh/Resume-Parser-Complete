import subprocess
import time

# Start FastAPI backend
backend = subprocess.Popen(
    ["uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"])

# Wait a bit to ensure backend starts first
time.sleep(3)

# Start Streamlit frontend
frontend = subprocess.Popen(
    ["streamlit", "run", "dashboard.py"])
try:
    backend.wait()
    frontend.wait()
except KeyboardInterrupt:
    print("Shutting down...")
    backend.terminate()
    frontend.terminate()