import random
import time
import requests

URL = "http://127.0.0.1:5000/predict"  # Your Flask endpoint

PROTOCOLS = [0, 1, 2]  # TCP, UDP, ICMP
THREAT_TYPES = ['normal', 'dos', 'probe', 'r2l', 'u2r']

def generate_packet():
    return {
        "source_ip": f"192.168.1.{random.randint(1,254)}",
        "features": [
            random.randint(1, 60),          # duration
            random.choice(PROTOCOLS),       # protocol
            random.random()*4, random.random()*4,
            random.randint(0,1000), random.randint(0,1000),
            0,0,0,0,
            random.randint(0,10),           # failed logins
            1,0,0,0,0,0,0,0,10,8,
            random.random(), random.random(),
            random.random(), random.random(),
            random.random(), random.random(),
            random.random(), 20,15,
            random.random(), random.random(),
            random.random(), random.random(),
            random.random(), random.random(),
            random.random(), random.random()
        ]
    }

def send_packet(packet):
    try:
        response = requests.post(URL, json=packet)
        print(response.json())
    except Exception as e:
        print("Error sending packet:", e)

if __name__ == "__main__":
    while True:
        packet = generate_packet()
        send_packet(packet)
        time.sleep(5)  # every 5 seconds
