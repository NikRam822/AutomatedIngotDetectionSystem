from flask import Flask, Response, request, jsonify
from flask_cors import CORS, cross_origin
from waitress import serve

import json
import threading

from core import Core

CORE = Core()

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=['*', 'null'])

# Lock for thread safety
lock = threading.Lock()

@app.route('/event', methods=['POST'])
@cross_origin(supports_credentials=True)
def save_event():
    event = request.get_json(cache=False)
    if CORE.log_event(event):
        return jsonify({})
    return jsonify({}), 400

@app.route('/experiments', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_experiments():
    return jsonify(CORE.config.experiments)

@app.route('/image_next', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_next_image():
    result = CORE.next_unmarked_image()
    if not result:
        return jsonify({"error": "No images available"}), 404
    return jsonify(result)

@app.route('/submit', methods=['POST'])
@cross_origin(supports_credentials=True)
def submit_text():
    data = request.get_json()
    if 'id' not in data or 'text' not in data:
        return jsonify({"error": "Missing 'id' or 'text' in the request"}), 400
    if CORE.submit_mark(image_id=data['id'], mark=data['text']):
        return jsonify({"success": True})
    return jsonify({"error": f"Image with id {data['id']} not found"}), 404

@app.route('/camera_detection')
@cross_origin(supports_credentials=True)
def index():
    return json.dumps(CORE.get_all_cameras())

@app.route('/video_feed/<int:camera_id>')
@cross_origin(supports_credentials=True)
def video_feed(camera_id):
    CORE.choose_camera(camera_id)
    return Response(CORE.generate_frames(camera_id), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/save_frame/<int:camera_id>', methods=['POST'])
@cross_origin(supports_credentials=True)
def save_frame(camera_id):
    brightness = request.args.get('brightness', default=1.0, type=float)
    contrast = request.args.get('contrast', default=1.0, type=float)
    if CORE.save_frame(camera_id=camera_id, brightness=brightness, contrast=contrast):
        return jsonify({'success': True, 'message': 'The frame has been saved successfully.'})
    return jsonify({'success': False, 'message': 'Error: unable to save frame as image.'})


if __name__ == '__main__':
    # For dev server (flask --app flask_server run)
    app.run(debug=True)

    # For Production server (waitress-serve --host=127.0.0.1 --port=5000 flask_server:app)
    # serve(app, host='0.0.0.0', port=5000, device='/dev/video0')
