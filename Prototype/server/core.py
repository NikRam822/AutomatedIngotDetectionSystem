"""
Core module
"""

import datetime
import os

from camera import Camera

from config import Config
from database import Database
from events import EventsCollector

import logging
import logging.config
from log_config import log_config

import img_process_func

class Core:
    def __init__(self):
        self.config = Config('config.ini')
        logging.config.dictConfig(log_config(os.path.join(self.config.log_folder, 'logfile.log')))
        self.logger = logging.getLogger(__name__)

        self.logger.info(f"Initializing processing core...")
        self.logger.info(f"Enabled experiments: {self.config.experiments}")

        self.database = Database(self.config.csv_file_path)
        # self.database.update_from_folder(self.config.input_folder)

        self.running_cameras = {}

        if self.config.experiments.count('collect_events'):
            os.makedirs(self.config.events_folder, exist_ok=True)
            current_time = datetime.datetime.now().strftime("%Y-%m-%d")
            events_file = os.path.join(self.config.events_folder, f"{current_time}.csv")
            self.event_collector = EventsCollector(events_file)
    
    def log_event(self, event):
        if not self.event_collector:
            return True
        if 'name' not in event:
            return False
        self.event_collector.save_event(event['name'], event['attributes'])
        return True
    
    def get_all_cameras(self):
        self.logger.debug("Enumerating available cameras")

        cameras_info = []

        for camera_id in range(10):
            camera = Camera(fps=1, video_source=camera_id)
            if camera.is_available():
                camera_info = {
                    'id_camera': camera_id,
                    'video': f'/video_feed/{camera_id}',
                    'photo': f'/photo/{camera_id}'
                }
                cameras_info.append(camera_info)

        return cameras_info

    def choose_camera(self, camera_id):
        self.logger.debug("Starting stream from Camera " + str(camera_id))
        camera = Camera(video_source=camera_id)
        camera.run()
        self.running_cameras[camera_id] = camera

    def generate_frames(self, camera_id):
        camera = self.running_cameras[camera_id]
        if camera is None:
            return
        while True:
            frame = camera.get_last_frame()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def next_unmarked_image(self):
        self.logger.debug("Getting next unmarked image...")
        row = self.database.next_unmarked()
        if row is not None:
            photo_path = os.path.join(self.config.output_folder, row.image_name)
            return {'id': row.image_id, 'source': photo_path}
        return None

    def save_frame(self, camera_id, brightness, contrast):
        self.logger.debug("Trying to take a picture...")
        camera = self.running_cameras[camera_id]
        if camera is None:
            return False

        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")[:-3]
        photo_name = f'{current_time}_cam_{camera_id}.jpg'
        photo_path = os.path.join(self.config.input_folder, photo_name)
        if not camera.save_photo(path=photo_path, contrast=contrast, brightness=brightness):
            return False

        pre_mark = 'OK'
        if not img_process_func.image_processing(photo_path, self.config.output_folder):
            pre_mark = 'EMPTY'
        self.database.append_to_db(ingot_id=0, camera_id=camera_id, photo_name=photo_name, pre_mark=pre_mark)
        return True

    def submit_mark(self, image_id, mark):
        self.logger.debug(f"Submitting decision for {image_id}: {mark}")
        return self.database.update_mark(img_id=image_id, final_mark=mark)
