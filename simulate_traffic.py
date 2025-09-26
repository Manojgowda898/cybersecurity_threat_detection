import requests
import time
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=5000)
args = parser.parse_args()
port = args.port

# Example synthetic traffic data
traffic_events = [
    {"source_ip": "192.168.1.101", "protocol": "TCP", "duration": 5, "failed_logins": 0},
    {"source_ip": "192.168.1.102", "protocol": "UDP", "duration": 8, "failed_logins": 2},
    {"source_ip": "192.168.1.103", "protocol": "ICMP", "duration": 2, "failed_logins": 0},
]

print(f"🚀 Starting simulation of network traffic events to port {port}...")

while True:
    for event in traffic_events:
        try:
            response = requests.post(f"http://127.0.0.1:{port}/predict", json=event)
            print(f"Sent: {event} -> Received: {response.json()}")
        except requests.exceptions.RequestException as e:
            print("⚠️ Flask server not ready yet, retrying in 2 seconds...")
            time.sleep(2)
            continue
    time.sleep(5)  # wait 5 seconds between batches
