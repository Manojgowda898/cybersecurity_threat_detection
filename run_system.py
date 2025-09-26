import os
import subprocess
import sys
import socket
import psutil
import time

# -----------------------------
# Get project folder
# -----------------------------
project_dir = os.path.dirname(os.path.abspath(__file__))

# ⚠️ Use this the very first time you set up the project.
# Afterwards, you can comment this out to avoid reinstalling every run.
# def install_requirements():
#     """
#     ⚠️ Use this if it's the first time running the project.
#     Installs all required Python packages from requirements.txt
#     """
#     requirements_file = os.path.join(project_dir, "requirements.txt")
#     if os.path.exists(requirements_file):
#         print("📦 Installing requirements from requirements.txt ...")
#         subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
#         print("✅ Requirements installed successfully!")
#     else:
#         print("⚠️ requirements.txt not found! Please create it first.")


# -----------------------------
# Helper: Find a free port
# -----------------------------
def find_free_port(start_port=5000):
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                port += 1

# -----------------------------
# Helper: Stop any process on a port
# -----------------------------
def stop_process_on_port(port):
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for conn in proc.connections(kind='inet'):
                if conn.laddr.port == port:
                    print(f"Stopping previous process {proc.info['pid']} ({proc.info['name']}) on port {port}")
                    proc.kill()
        except Exception:
            continue

# -----------------------------
# 0️⃣ Install requirements
# -----------------------------
# ⚠️ UNCOMMENT the next line only the first time you run the project
# install_requirements()

# -----------------------------
# 1️⃣ Choose port
# -----------------------------
port = find_free_port(5000)
stop_process_on_port(port)
print(f"✅ Using port {port} for Flask-SocketIO server")

# -----------------------------
# 2️⃣ Train models
# -----------------------------
train_path = os.path.join(project_dir, "train_models.py")
if os.path.exists(train_path):
    print(f"🤖 Training models using {train_path} ...")
    subprocess.check_call([sys.executable, train_path])
else:
    print("⚠️ train_models.py not found! Skipping model training.")

# -----------------------------
# 3️⃣ Start Flask-SocketIO server
# -----------------------------
app_path = os.path.join(project_dir, "app.py")
if os.path.exists(app_path):
    print(f"🌐 Starting Flask-SocketIO server on port {port} ...")
    subprocess.Popen([sys.executable, app_path, "--port", str(port)])
else:
    print("⚠️ app.py not found! Cannot start Flask server.")

# -----------------------------
# 4️⃣ Optional: Run traffic simulation
# -----------------------------
simulate_path = os.path.join(project_dir, "simulate_traffic.py")
if os.path.exists(simulate_path):
    print(f"🚀 Starting traffic simulation using {simulate_path} ...")
    subprocess.Popen([sys.executable, simulate_path, "--port", str(port)])
