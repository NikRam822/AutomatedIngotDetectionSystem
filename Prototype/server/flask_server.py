import cv2
from flask import Flask, Response, request, jsonify
from flask_cors import CORS, cross_origin
from waitress import serve
import csv
import json
import os
import threading

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=['*', 'null'])
# Path to CSV file
csv_file_path = 'data.csv'

# Current image index
current_image_index = 0

# Create a folder to save the photos in if there is none
photo_folder = 'output'
os.makedirs(photo_folder, exist_ok=True)
image_id_counter = 0


# Dictionary to store counters for each camera
photo_counters = {}

# Lock for thread safety
lock = threading.Lock()

# Processing GET request image_next
@app.route('/image_next', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_next_image():
    global current_image_index

    # Reading data from CSV file
    with open(csv_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        rows = list(csv_reader)

    if rows:
        # Obtaining data for the current index
        row = rows[current_image_index]
        image_id = row['id_img']
        image_source = row['source_img']

        # Increasing the index for the next query
        current_image_index = (current_image_index + 1) % len(rows)

        return jsonify({"id": image_id, "source": image_source})
    else:
        return jsonify({"error": "No images available"}), 404

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
    return Response(generate_frames(camera_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/photo/<int:camera_id>', methods=['POST'])
@cross_origin(supports_credentials=True)
def capture_photo_route(camera_id):
    global photo_counters
    photo_name = f'photo_camera_{camera_id}_{photo_counters[camera_id]}.jpg'
    photo_path = os.path.join(photo_folder, photo_name)
    photo_counters[camera_id] += 1

    # Start a new thread for capturing photo
    threading.Thread(target=capture_photo, args=(camera_id, photo_path)).start()

    return jsonify({'photo_path': photo_path})

def generate_frames(camera_id):
    camera = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def capture_photo(camera_id, photo_path):
    global image_id_counter

    with lock:
        # Reading data from CSV file to get the last recorded id_img
        with open(csv_file_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            rows = list(csv_reader)

        # Get the last recorded id_img
        last_id_img = int(rows[-1]['id_img']) if rows else 0

        # Increment the global image ID counter
        image_id_counter = last_id_img + 1

        # Open the camera to read the frame
        camera = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)

        # Read the frame
        success, frame = camera.read()
        if success:
            try:
                # Save the photo
                cv2.imwrite(os.path.join(photo_path), frame)
                print(os.path.join(photo_path))
            except Exception as e:
                print(f"Error saving image: {e}")
        else:
            print("Error capturing frame")

        # Freeing up the cell's resources
        camera.release()

        # Define id_img as the current counter value
        id_img = image_id_counter

        # Write the data to a CSV file
        with open(csv_file_path, mode='a', newline='') as csv_file:
            fieldnames = ['id_camera', 'id_img', 'source_img', 'text']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            # Create a line with the new data
            new_row = {
                'id_camera': camera_id,
                'id_img': id_img,
                'source_img': photo_path,
                'text': ''
            }

            # Write the string to a CSV file
            writer.writerow(new_row)

    # Return id_img
    return id_img




if __name__ == '__main__':
    # For dev server (flask --app flask_server run)
    app.run(debug=True)

    # For Production server (waitress-serve --host=127.0.0.1 --port=5000 flask_server:app)
    # serve(app, host='0.0.0.0', port=5000)