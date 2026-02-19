import requests
import socketio
import time
import urllib3
import os

# Suppress warnings for self-signed certificates (since we are using verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION ---
# We use 127.0.0.1 to force IPv4. 
# If your server is on a different machine, change this IP.
BASE_URL = 'https://127.0.0.1:8051' 
SOCKET_PATH = '/ws'

print(f"🔍 DIAGNOSTIC TOOL: Connecting to {BASE_URL}")
print("-" * 60)

# ---------------------------------------------------------
# 1. Test Basic HTTP Connectivity (Is the server running?)
# ---------------------------------------------------------
print("\n[1] Checking HTTP Root (GET /)...")
try:
    # verify=False is needed because you are using self-signed certs in dev
    response = requests.get(f"{BASE_URL}/", verify=False, timeout=5)
    print(f"   ✅ Status Code: {response.status_code}")
    print(f"   📄 Response: {response.text}")
except Exception as e:
    print(f"   ❌ HTTP Request Failed: {e}")
    print("   -> Is the server running? Check the terminal for errors.")
    exit(1)

# ---------------------------------------------------------
# 2. Test Socket.IO Handshake via HTTP (CORS/Path Check)
# ---------------------------------------------------------
print("\n[2] Checking Socket.IO Handshake (HTTP Polling)...")
# Socket.IO connection starts with a standard HTTP GET request.
# If this fails, the WebSocket upgrade will never happen.
handshake_url = f"{BASE_URL}{SOCKET_PATH}/?EIO=4&transport=polling"

try:
    print(f"   Requesting: {handshake_url}")
    
    # Test A: Without Origin (Simulating a script or backend-to-backend call)
    resp = requests.get(handshake_url, verify=False, timeout=5)
    if resp.status_code == 200:
        print("   ✅ Handshake (No Origin) -> Success")
    else:
        print(f"   ⚠️ Handshake (No Origin) -> Failed ({resp.status_code})")
        print(f"      Response: {resp.text}")

    # Test B: With Origin (Simulating a Browser/CORS)
    # We use localhost:3000 as it is in your allowed origins list
    test_origin = "http://localhost:3000"
    print(f"   Requesting with Origin: {test_origin}")
    resp_cors = requests.get(handshake_url, headers={'Origin': test_origin}, verify=False, timeout=5)
    
    if resp_cors.status_code == 200:
        print(f"   ✅ Handshake (With Origin) -> Success")
    else:
        print(f"   ❌ Handshake (With Origin) -> Failed ({resp_cors.status_code})")
        print(f"      Response: {resp_cors.text}")
        print("      -> This indicates a CORS configuration issue in extensions.py")

except Exception as e:
    print(f"   ❌ Handshake Request Failed: {e}")

# ---------------------------------------------------------
# 3. Test Full Socket.IO Client Connection
# ---------------------------------------------------------
print("\n[3] Testing Full Socket.IO Client Connection...")

# Initialize client with debug logging enabled
sio = socketio.Client(
    ssl_verify=False, 
    logger=True, 
    engineio_logger=True
)

@sio.event
def connect():
    print("   >>> ✅ CLIENT CONNECTED SUCCESSFULLY! <<<")

@sio.event
def connect_error(data):
    print(f"   >>> ❌ CONNECTION ERROR: {data}")

@sio.event
def disconnect():
    print("   >>> ⚠️ CLIENT DISCONNECTED")

@sio.event
def heartbeat(data):
    print(f"   >>> ❤️ Heartbeat received: {data}")

try:
    # socketio_path must match the 'path' arg in your Flask-SocketIO init
    print(f"   Attempting connection to {BASE_URL} path={SOCKET_PATH}...")
    sio.connect(BASE_URL, socketio_path=SOCKET_PATH, wait_timeout=5)
    
    # Keep alive for 5 seconds to listen for heartbeats or events
    print("   Waiting for events (5s)...")
    time.sleep(5)
    
    sio.disconnect()

except Exception as e:
    print(f"   ❌ Client Exception: {e}")

print("\nDone.")
