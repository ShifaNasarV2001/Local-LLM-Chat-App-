import subprocess
import sys
import time
import os

def run_uvicorn():
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
        cwd=os.path.dirname(__file__)
    )

def run_streamlit():
    return subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py"],
        cwd=os.path.dirname(__file__)
    )

if __name__ == "__main__":
    print("Starting FastAPI (uvicorn)...")
    uvicorn_proc = run_uvicorn()
    time.sleep(2)  # Give FastAPI a moment to start

    print("Starting Streamlit...")
    streamlit_proc = run_streamlit()

    try:
        uvicorn_proc.wait()
        streamlit_proc.wait()
    except KeyboardInterrupt:
        print("Shutting down...")
        uvicorn_proc.terminate()
        streamlit_proc.terminate()
