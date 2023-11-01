from flask import Flask, Response, request, jsonify
from flask_cors import CORS, cross_origin
# from waitress import serve

from camera import Camera, get_all_cameras
from config import configureServer

import csv
import json
import logging
import os
import threading

configureServer()
logger = logging.getLogger(__name__)

from config import csv_file_path, input_folder, output_folder

logger.info("Folders:")
logger.info("  Database: " + csv_file_path)
logger.info("  Input:    " + input_folder)
logger.info("  Output:   " + output_folder)

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=['*', 'null'])

# Current image index
current_image_index = 0

# Create a folder to save the photos in if there is none
image_id_counter = 0

# Dictionary to store counters for each camera
photo_counters = {}

# Lock for thread safety
lock = threading.Lock()

camera = None

# Processing GET request image_next
@app.route('/image_next', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_next_image():
    global current_image_index

    # Reading data from CSV-file
    with open(csv_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        rows = list(csv_reader)

    if not rows:
        return jsonify({"error": "No images available"}), 404

    # The last parameter in the query
    last = request.args.get('last')

    if last == 'true':
        # If the last parameter is present and is 'true', return the latest data
        last_row = rows[-1]
        image_id = last_row['id_img']
        image_source = last_row['source_img']
    else:
        # Otherwise, get data for the current index
        row = rows[current_image_index]
        image_id = row['id_img']
        image_source = row['source_img']

        # Increase the index for the next query
        current_image_index = (current_image_index + 1) % len(rows)

    return jsonify({"id": image_id, "source": image_source})


# Processing POST submit request
@app.route('/submit', methods=['POST'])
@cross_origin(supports_credentials=True)
def submit_text():
    # Getting data from JSON request
    data = request.get_json()

    # Check if the required fields are present
    if 'id' not in data or 'text' not in data:
        return jsonify({"error": "Missing 'id' or 'text' in the request"}), 400

    # Reading data from CSV file
    with open(csv_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        rows = list(csv_reader)

    # Search for string with specified id_img
    found_row = None
    for row in rows:
        if row['id_img'] == data['id']:
            found_row = row
            break

    if found_row is not None:
        found_row['text'] = data['text']

        with open(csv_file_path, mode='w', newline='') as csv_file:
            fieldnames = ['id_camera', 'id_img', 'source_img', 'text']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        return jsonify({"success": True})
    else:
        return jsonify({"error": f"Image with id {data['id']} not found"}), 404

@app.route('/camera_detection')
@cross_origin(supports_credentials=True)
def index():
    logger.debug("Enumerating available cameras")

    ids = get_all_cameras()
    logger.info("Cameras found: " + str(len(ids)))

    cameras_info = []
    for camera_id in ids:
        if camera_id not in photo_counters:
            photo_counters[camera_id] = 0

        camera_info = {
            'id_camera': camera_id,
            'video': f'/video_feed/{camera_id}',
            'photo': f'/photo/{camera_id}'
        }
        cameras_info.append(camera_info)

    return json.dumps(cameras_info)

@app.route('/video_feed/<int:camera_id>')
@cross_origin(supports_credentials=True)
def video_feed(camera_id):
    logger.debug("Starting stream from Camera " + str(camera_id))

    global camera
    camera = Camera(video_source=camera_id)
    camera.run()

    return Response(generate_frames(camera), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/save_frame/<int:camera_id>', methods=['POST'])
@cross_origin(supports_credentials=True)
def save_frame(camera_id):
    global camera
    global photo_counters

    if camera is not None:
        brightness = request.args.get('brightness', default=1.0, type=float)
        contrast = request.args.get('contrast', default=1.0, type=float)

        photo_name = f'photo_camera_{camera_id}_{photo_counters[camera_id]}.jpg'
        photo_path = os.path.join(input_folder, photo_name)
        photo_counters[camera_id] += 1

        if camera.save_photo(path=photo_path, contrast=contrast, brightness=brightness):
            append_to_csv(camera_id, photo_path)
            return jsonify({'success': True, 'message': 'The frame has been saved successfully.'})

    return jsonify({'success': False, 'message': 'Error: unable to save frame as image.'})

# Supporting functions

def generate_frames(camera):
    while True:
        frame = camera.getLastFrame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def append_to_csv(camera_id, photo_path):
    with open(csv_file_path, mode='a', newline='') as csv_file:
        fieldnames = ['id_camera', 'id_img', 'source_img', 'text']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Get the current value of id_img
        with open(csv_file_path, mode='r') as csv_file_read:
            reader = csv.DictReader(csv_file_read)
            rows = list(reader)
            if not rows:
                last_id_img = 0
            else:
                last_id_img = int(rows[-1]['id_img'])

        # Increase id_img by 1
        id_img = last_id_img + 1

        # Create a record for CSV
        new_record = {
            'id_camera': camera_id,
            'id_img': id_img,
            'source_img': photo_path,
            'text': ''
        }

        # Write the record to a CSV file
        writer.writerow(new_record)

if __name__ == '__main__':
    # For dev server (flask --app flask_server run)
    app.run(debug=True)

    # For Production server (waitress-serve --host=127.0.0.1 --port=5000 flask_server:app)
    # serve(app, host='0.0.0.0', port=5000, device='/dev/video0')
