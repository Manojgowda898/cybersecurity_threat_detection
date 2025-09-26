from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from models.threat_model import ThreatDetectionModel, init_database, store_alert
import time
import threading
import pandas as pd

# -----------------------------
# Initialize Flask & SocketIO
# -----------------------------
app = Flask(__name__)
CORS(app)

# Use eventlet for async WebSocket support
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")



# -----------------------------
# Initialize database and model
# -----------------------------
init_database()
detector = ThreatDetectionModel()
detector.load_models('models_saved/')

# -----------------------------
# Home / Dashboard route
# -----------------------------
@app.route("/")
def dashboard():
    return render_template('dashboard.html')

# -----------------------------
# Predict threat API
# -----------------------------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json
        features = data.get("features") or [data.get(col, 0) for col in detector.feature_names]

        # Wrap features in DataFrame to match model's expected column names
        features_df = pd.DataFrame([features], columns=detector.feature_names)
        result = detector.predict_threat(features_df)

        if result:
            store_alert(
                result['predicted_class'],
                result['confidence'],
                data.get('source_ip', '0.0.0.0'),
                result['probabilities']
            )
            # Emit alert to live dashboard
            socketio.emit('threat_update', {
                "timestamp": time.time(),
                "threat": result['predicted_class'],
                "value": int(result['confidence'] * 100)
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

# -----------------------------
# Background simulator (optional)
# -----------------------------
def simulate_threats():
    """Simulate live threat data every 5 seconds"""
    import random
    while True:
        simulated = {
            "timestamp": time.time(),
            "threat": random.choice(["benign", "malicious"]),
            "value": random.randint(1, 100)
        }
        socketio.emit('threat_update', simulated)
        socketio.sleep(5)  # eventlet-friendly sleep

# Start simulator in background
threading.Thread(target=simulate_threats, daemon=True).start()

# -----------------------------
# Print all Flask routes (optional)
# -----------------------------
print("\n🔹 Registered Flask routes:")
for rule in app.url_map.iter_rules():
    print(f"{rule} -> {', '.join(rule.methods)}")

# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    import sys
    port = 5000
    if "--port" in sys.argv:
        port_index = sys.argv.index("--port") + 1
        port = int(sys.argv[port_index])
    
    print(f"🌐 Starting Flask-SocketIO server on port {port}...")
    # Disable debug and reloader to avoid termios error
    socketio.run(app, host="0.0.0.0", port=port, debug=False, use_reloader=False)
