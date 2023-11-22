"""
Core module
"""

import datetime
import logging
import logging.config
import os

from camera import Camera, CameraSettings
from config import Config
from database import Database
from decision import Decisions
from events import EventsCollector

from image_analysis import AI
from image_processing import image_processing

from log_config import log_config

class Core:
    """Core module. It organizes all image processing and other manipulations."""

    decisions = [ Decisions.ok, Decisions.dross, Decisions.color, Decisions.no_ingot, Decisions.bad_image ]

    def __init__(self):
        self.config = Config('config.ini')
        logging.config.dictConfig(log_config(os.path.join(self.config.log_folder, 'logfile.log')))
        self.logger = logging.getLogger(__name__)

        self.logger.info('Initializing processing core...')
        self.logger.info('Enabled experiments: %s', str(self.config.experiments))

        self.ai = AI(Core.decisions)
        self.database = Database(self.config.db_folder)

        self.cameras_info = []
        self.running_cameras = {}

        if self.config.experiments.count('collect_events'):
            os.makedirs(self.config.events_folder, exist_ok=True)
            self.event_collector = EventsCollector(self.config.events_folder)

    def log_event(self, event):
        """Save analytics event for future analysis, if necessary."""
        if not self.event_collector:
            return True
        if 'name' not in event:
            return False
        self.event_collector.save_event(event['name'], event['attributes'])
        return True

    def get_all_decisions(self):
        """Send all available decisions to show them in the UI."""
        self.logger.debug('Enumerating available decisions')
        result = []
        for value in Core.decisions:
            result.append({'key': value.key, 'type': value.kind, 'label': value.label})
        return result

    def get_all_cameras(self, force=False):
        """Enumerate all available cameras."""
        self.logger.debug('Enumerating available cameras')

        if not force and len(self.cameras_info) > 0:
            return self.cameras_info

        for camera_id in range(10):
            camera = Camera(fps=1, video_source=camera_id)
            if camera.is_available():
                camera_info = {
                    'id_camera': camera_id,
                    'video': f'/video_feed/{camera_id}',
                    'photo': f'/photo/{camera_id}'
                }
                self.cameras_info.append(camera_info)

        return self.cameras_info

    def release_all_cameras(self):
        """Release all captured cameras so they could be used again."""
        for camera in self.running_cameras.values():
            if camera is not None:
                camera.stop()
        self.running_cameras = {}

    def get_camera_settings(self, camera_id):
        """Return current settings for the specified camera"""
        camera = self.running_cameras.get(camera_id)
        if camera is None:
            return []
        return camera.settings.to_dict()

    def set_camera_settings(self, camera_id, settings):
        """Set new settings for the specified camera"""
        camera = self.running_cameras.get(camera_id)
        if camera is not None:
            camera.apply_settings(settings)

    def choose_camera(self, camera_id):
        """Choose a camera for capture."""
        camera = self.running_cameras.get(camera_id)
        if camera is not None:
            return

        self.logger.debug('Starting stream from Camera %d', camera_id)
        camera = Camera(video_source=camera_id)
        camera.run()
        self.running_cameras[camera_id] = camera

    def generate_frames(self, camera_id):
        """Run an infinite loop of taking frames from the camera."""
        camera = self.running_cameras.get(camera_id)
        if camera is None:
            return
        while True:
            frame = camera.get_last_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def last_unmarked_image(self):
        """Return next unmarked image in a special format."""
        self.logger.debug('Getting next unmarked image...')
        row = self.database.last_unmarked()
        if row is None:
            return None
        photo_path = os.path.join(self.config.output_folder, row.image_name)
        if row.final_mark != '':
            decision = self._decision_description(row.final_mark, 'User')
        elif row.ml_mark != '':
            decision = self._decision_description(row.ml_mark, 'AI')
        elif row.pre_mark != '':
            decision = self._decision_description(row.pre_mark, 'Processing')
        else:
            decision = ''
        return {'id': row.image_id, 'source': photo_path, 'decision': decision}

    def save_frame(self, camera_id):
        """Save the most recent captured frame as an image and run it through analysis pipeline."""
        self.logger.debug('Trying to take a picture...')
        camera = self.running_cameras[camera_id]
        if camera is None:
            return False

        current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S%f')[:-3]
        photo_name = current_time + '_cam_' + str(camera_id) + '.jpg'
        photo_path = os.path.join(self.config.input_folder, photo_name)
        if not camera.save_photo(path=photo_path):
            return False

        pre_mark = image_processing(photo_path, self.config.output_folder).key
        ml_mark = ''
        if pre_mark == Decisions.ok.key:
            ml_mark = self.ai.classify_image(photo_path).key

        self.database.append_to_db(ingot_id=0, camera_id=camera_id, photo_name=photo_name, pre_mark=pre_mark, ml_mark=ml_mark)
        return True

    def submit_mark(self, image_id, mark):
        """Save a final mark from user input."""
        self.logger.debug('Submitting decision for image_id %d: %s', image_id, mark)
        return self.database.update_mark(image_id, mark)

    def _decision_description(self, decision, source):
        """Internal helper function for decision label decoration."""
        if source == 'User':
            prefix = 'Decision: '
        else:
            prefix = 'Prediction: '
        for val in Core.decisions:
            if val.key == decision:
                return prefix + val.label
        return ''
