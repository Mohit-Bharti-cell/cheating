from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging

from events import register_socket_events

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "defaultsecret")

# Disable all logs (Flask & SocketIO)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
register_socket_events(socketio)

@app.route("/")
def index():
    return jsonify({"status": "Server is running."})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
