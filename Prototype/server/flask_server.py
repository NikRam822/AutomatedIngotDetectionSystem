"""
The Router module.
It is a Flask server implementation with basic routing.
"""
import json
import threading

from flask import Flask, Response, request, jsonify, render_template, send_file, make_response
from flask_cors import CORS, cross_origin
# from waitress import serve

from core import Core

CORE = Core()

app = Flask(__name__, static_folder='../client', template_folder='../client')

CORS(app, supports_credentials=True, origins=['*', 'null'])

# Lock for thread safety
lock = threading.Lock()

@app.route('/event', methods=['POST'])
@cross_origin(supports_credentials=True)
def save_event():
    """Endpoint for recieving analytics events from the client."""
    event = request.get_json(cache=False)
    if CORE.log_event(event):
        return jsonify({})
    return jsonify({}), 400

@app.route('/experiments', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_experiments():
    """The configuration of all enabled experiments."""
    return jsonify(CORE.config.experiments)

@app.route('/decisions', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_decisions():
    """List of possible decisions. See Core.decisions for a full list."""
    return jsonify(CORE.get_all_decisions())

@app.route('/image_next', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_next_image():
    """Endpoint to retrieve next unmarked image. Only images without 'final_mark' set in the DB file will be returned."""
    result = CORE.last_unmarked_image()
    if not result:
        return jsonify({"error": "No images available"}), 404

    image_path = result['source']
    image_id = result['id']
    decision = result['decision']

    response = make_response(send_file(image_path, mimetype='image/jpeg'))
    response.headers['image_id'] = str(image_id)
    response.headers['decision'] = str(decision)
    return response


@app.route('/submit', methods=['POST'])
@cross_origin(supports_credentials=True)
def submit_text():
    """Submitting the final decision from the user."""
    image_id = request.form.get('id')
    mark_text = request.form.get('text')

    if not image_id or not mark_text:
        return jsonify({"error": "Missing 'id' or 'text' in the request"}), 400

    if CORE.submit_mark(image_id=image_id, mark=mark_text):
        return jsonify({"success": True})
    return jsonify({"error": f"Image with id {image_id} not found"}), 404


@app.route('/')
@cross_origin(supports_credentials=True)
def get_index():
    return render_template('index.html')


@app.route('/camera_detection')
@cross_origin(supports_credentials=True)
def index():
    """Request all available cameras."""
    return json.dumps(CORE.get_all_cameras())

@app.route('/camera_settings/<int:camera_id>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_camera_settings(camera_id):
    """Get current camera settings"""
    return jsonify(CORE.get_camera_settings(camera_id))

@app.route('/camera_settings/<int:camera_id>', methods=['POST'])
@cross_origin(supports_credentials=True)
def set_camera_settings(camera_id):
    """Set new settings for the camera"""
    settings = request.get_json()
    CORE.set_camera_settings(camera_id, settings)
    return jsonify({})

@app.route('/video_feed/<int:camera_id>')
@cross_origin(supports_credentials=True)
def video_feed(camera_id):
    """Choose a camera to get frames."""
    CORE.choose_camera(camera_id)
    return Response(CORE.generate_frames(camera_id), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/save_frame/<int:camera_id>', methods=['POST'])
@cross_origin(supports_credentials=True)
def save_frame(camera_id):
    """Save a frame from the selected camera and prepare it for analysis."""
    if CORE.save_frame(camera_id):
        return jsonify({'success': True, 'message': 'The frame has been saved successfully.'})
    return jsonify({'success': False, 'message': 'Error: unable to save frame as image.'})

if __name__ == '__main__':
    # For dev server (flask --app flask_server run)
    app.run(debug=True)

    # For Production server (waitress-serve --host=127.0.0.1 --port=5000 flask_server:app)
    # serve(app, host='0.0.0.0', port=5000, device='/dev/video0')
