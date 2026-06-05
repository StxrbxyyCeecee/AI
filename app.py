from gevent import monkey
monkey.patch_all()

import os
from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit

app = Flask(__name__, static_folder=".", template_folder=".")
app.config['SECRET_KEY'] = 'frank_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/watch')
def watch():
    return render_template('watch.html')

@socketio.on('manual_chat')
def handle_chat(data):
    user_text = data.get('text', '')
    print(f"Received message: {user_text}", flush=True)
    
    response = f"Frank (Local Node): I received '{user_text}'"

    # Emit back to the terminal
    emit('new_log', {'text': f"You: {user_text}"})
    emit('new_log', {'text': f"Frank: {response}"})
    
    # Trigger orb animation
    emit('speak_state', {'active': True})
    socketio.sleep(2)
    emit('speak_state', {'active': False})

@socketio.on('watch_sync_complete')
def watch_sync():
    emit('watch_state_change', {'connected': True}, broadcast=True)
    emit('new_log', {'text': "SYSTEM: Smartwatch link established via Render."}, broadcast=True)

if __name__ == '__main__':
    # Render provides a PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)