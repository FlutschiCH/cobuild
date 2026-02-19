from extensions import socketio
from flask_socketio import emit
import gevent

_heartbeat_running = False

def heartbeat():
    """Sends a heartbeat ping to the client every 20 seconds."""
    while True:
        socketio.sleep(20)
        socketio.emit('heartbeat', {'data': 'ping'})

@socketio.on('connect')
def handle_connect():
    global _heartbeat_running
    print('Client connected')
    if not _heartbeat_running:
        gevent.spawn(heartbeat)
        _heartbeat_running = True

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('file_update')
def handle_file_update(data):
    print('received json: ' + str(data))
    # Here you would typically save the file content to the database
    # For now, we'll just send a confirmation back to the client
    emit('file_update_confirmation', {'status': 'success', 'file': data.get('filename')})
