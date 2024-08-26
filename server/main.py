from flask import Flask, Response, request, jsonify
from config import init_db
from flask_cors import CORS
import numpy as np
import cv2
import base64
import time
from collections import deque
import json
from copy import deepcopy
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


mongo = init_db(app, os.getenv("MONGO_DB_URL"))

# Configuration
MAX_FRAMES = int(os.getenv("MAX_FRAMES"))
MAX_COLOR_DATA = int(os.getenv("MAX_COLOR_DATA"))

# Dictionary to hold the last frames and color data for each client
client_frames = {}
display_frames = {}
client_color_data = {}
client_frames_counter = {}

@app.route('/set_frame_interval/<client_id>', methods=['POST'])
def set_frame_interval(client_id):
    """Store the value of n in cache for a specific client."""
    data = request.json
    n = data.get('n')
    if n is not None and isinstance(n, int) and n > 0:
        if client_id in client_frames_counter:
            client_frames_counter[client_id]["display_frames_at"] = n
        else:
            client_frames_counter[client_id] = {}
            client_frames_counter[client_id]["display_frames_at"] = n
            client_frames_counter[client_id]["frame_count"] = 0

        return jsonify({"message": "Value of n stored successfully", "n": n}), 200
    else:
        return jsonify({"message": "Invalid value for n"}), 400

def process_frame(image_data, client_id):
    """Process and store a single frame."""
    nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    average_color = cv2.mean(frame)[:3]  # Get BGR values
    average_color = list(average_color)

    # Store the image in MongoDB
    mongo.db.frames.insert_one({
        "client_id": client_id,
        "image_data": image_data,
        "insertion_time": datetime.now(),
    })

    client_frames_counter[client_id]["frame_count"] += 1
    
    if client_id not in client_frames:
        client_frames[client_id] = deque(maxlen=MAX_FRAMES)

    if client_id not in display_frames:
        display_frames[client_id] = deque(maxlen=MAX_FRAMES)

    encoded_frame = image_data

    if client_frames_counter[client_id]["frame_count"] % client_frames_counter[client_id]["display_frames_at"] == 0:
        display_frames[client_id].append(encoded_frame)
    client_frames[client_id].append(encoded_frame)

    
    if client_id not in client_color_data:
        client_color_data[client_id] = {}
        client_color_data[client_id]["color_data"] = deque(maxlen=MAX_COLOR_DATA)
    client_color_data[client_id]["color_data"].append(average_color)

    # Calculate color difference if there are at least 2 frames
    color_diff = None
    if len(client_frames[client_id]) >= 2:
        last_frame = cv2.imdecode(np.frombuffer(base64.b64decode(client_frames[client_id][-1]), np.uint8), cv2.IMREAD_COLOR)
        second_last_frame = cv2.imdecode(np.frombuffer(base64.b64decode(client_frames[client_id][-2]), np.uint8), cv2.IMREAD_COLOR)
        color_diff = np.abs(np.array(cv2.mean(last_frame)[:3]) - np.array(cv2.mean(second_last_frame)[:3]))

    # Update color difference in the last color data
    if client_color_data[client_id]:
        client_color_data[client_id]["color_difference"] = color_diff.tolist() if color_diff is not None else None

@app.route('/upload/<client_id>', methods=['POST'])
def upload(client_id):
    """Receive images from a client and store color data in MongoDB."""
    if client_id not in client_frames_counter:
        return jsonify({"message": "Please set value of interval at which frames needs to be displayed"}), 400
    
    if request.method == 'POST':
        data = request.data.decode('utf-8')  
        json_data = json.loads(data)  
        image_data = json_data.get('image') 
        # print(image_data)
        process_frame(image_data, client_id)
        return jsonify({"message": "Frame received"}), 200

def generate_frames(client_id):
    """Generate frames for SSE for a specific client."""
    while True:
        if client_id in display_frames and display_frames[client_id]:
            frame = display_frames[client_id].popleft()
            yield f"data: {frame}\n\n"
        else:
            yield ''
        time.sleep(0.1)

def generate_color_data(client_id):
    """Generate color data updates for SSE for a specific client."""
    while True:
        if client_id in client_color_data and client_color_data[client_id]:
            color_data = deepcopy(client_color_data[client_id])
            color_data["color_data"] = list(color_data["color_data"])
            yield f"data: {json.dumps(color_data)}\n\n"
        else:
            yield ''
        time.sleep(0.1)

@app.route('/sse/frames/<client_id>')
def sse_frames(client_id):
    """Stream frames to the client using SSE."""
    return Response(generate_frames(client_id), mimetype='text/event-stream')

@app.route('/sse/color_data/<client_id>')
def sse_color_data(client_id):
    """Stream color data to the client using SSE."""
    return Response(generate_color_data(client_id), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)