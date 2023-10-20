from flask import Flask, Response, request, jsonify, send_file
from flask_cors import CORS, cross_origin
from waitress import serve
from config import csv_file_path, input_folder, output_folder

import csv
import cv2
import json
import os
import threading

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

last_frame = None

# Processing GET request image_next
@app.route('/image_next', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_next_image():
    global current_image_index

    # Чтение данных из CSV-файла
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
        # Updating the value in the found string
        found_row['text'] = data['text']

        # Writing updated data to a CSV file
        with open(csv_file_path, mode='w', newline='') as csv_file:
            fieldnames = ['id_camera', 'id_img', 'source_img', 'text']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            # Write down the title
            writer.writeheader()

            # Write the updated rows
            writer.writerows(rows)

        return jsonify({"success": True})
    else:
        return jsonify({"error": f"Image with id {data['id']} not found"}), 404

@app.route('/camera_detection')
@cross_origin(supports_credentials=True)
def index():
    cameras_info = []
    # Search all possible cameras with an id from 0 to 9
    for camera_id in range(10):
        camera = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        if camera.isOpened():
            # Initialize a counter for each camera if it does not already exist
            if camera_id not in photo_counters:
                photo_counters[camera_id] = 0

            camera_info = {
                'id_camera': camera_id,
                'video': f'/video_feed/{camera_id}',
                'photo': f'/photo/{camera_id}'
            }
            cameras_info.append(camera_info)
            camera.release()

    return json.dumps(cameras_info)

@app.route('/video_feed/<int:camera_id>')
@cross_origin(supports_credentials=True)
def video_feed(camera_id):
    return Response(generate_frames(camera_id), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/save_frame/<int:camera_id>', methods=['POST'])
@cross_origin(supports_credentials=True)
def save_frame(camera_id):
    global last_frame
    global photo_counters
    if last_frame is not None:
        photo_name = f'photo_camera_{camera_id}_{photo_counters[camera_id]}.jpg'
        photo_path = os.path.join(input_folder, photo_name)
        photo_counters[camera_id] += 1
        cv2.imwrite(photo_path, last_frame)

        # Записываем данные в CSV
        append_to_csv(camera_id, photo_path)

        return jsonify({'message': 'The frame has been saved successfully.', 'path': photo_path})
    else:
        return jsonify({'message': 'Error: there is no available frame to save.'})


def generate_frames(camera_id):
    global last_frame
    camera = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    while True:
        success, frame = camera.read()
        last_frame =frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
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