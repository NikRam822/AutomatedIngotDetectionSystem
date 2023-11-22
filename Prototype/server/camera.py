"""
The Camera module.
"""

import logging
import threading
import time

import cv2

class CameraSettings:
    """Special data class to store camera settings"""
    def __init__(self, fps=20, contrast:float=1.0, brightness:int=0):
        self.fps = fps
        self.contrast = contrast
        self.brightness = brightness

    keys = ['fps', 'contrast', 'brightness']

    def to_dict(self):
        """Make a map of values suitable to show controls in the UI"""
        return [
            {'key': CameraSettings.keys[0], 'label': 'FPS', 'value': self.fps, 'from': 1, 'to': 30},
            {'key': CameraSettings.keys[1], 'label': 'Contrast', 'value': self.contrast, 'from': 0.0, 'to': 10.0, 'step': 0.1},
            {'key': CameraSettings.keys[2], 'label': 'Brightness', 'value': self.brightness, 'from': -255, 'to': 255},
        ]

    @classmethod
    def from_dict(cls, values):
        """Create a new settings object from the provided map"""
        fps = values[CameraSettings.keys[0]]
        contrast = values[CameraSettings.keys[1]]
        brightness = values[CameraSettings.keys[2]]
        return cls(fps, contrast, brightness)

class Camera:
    """It's a class that encapsulate all ther camera work."""
    def __init__(self, fps=20, video_source=0):
        self.logger = logging.getLogger(__name__)
        self.logger.info('Initializing camera class with %d fps and video_source=%d}', fps, video_source)

        self.settings = CameraSettings(fps)
        self.video_source = video_source
        self.camera = cv2.VideoCapture(video_source)
        self.frames = []
        self.is_running = False
        self.thread = None

    def apply_settings(self, settings):
        """Change values for keys specified in 'settings' object"""
        key = settings.get('key')
        value = settings.get('value')
        if not key or not value:
            return
        if key == CameraSettings.keys[0]:
            self.settings.fps = int(value)
        elif key == CameraSettings.keys[1]:
            self.settings.contrast = float(value)
        elif key == CameraSettings.keys[2]:
            self.settings.brightness = int(value)

    def is_available(self):
        """Check if the camera is available - it can return an image"""
        self.logger.debug('Checking camera %d', self.video_source)
        return bool(self.camera.read()[0])

    def is_released(self):
        """Check if the camera is released."""
        return not self.is_running

    def run(self):
        """Run the frame capture in a separate thread."""
        if self.is_running:
            return

        self.logger.debug('Starting thread')
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.is_running = True
        self.thread.start()
        self.logger.info('Thread started')

    def _capture_loop(self):
        """Internal function that captures frame into special framebuffer"""
        self.logger.debug('Observation started')
        while self.is_running:
            is_read, im = self.camera.read()
            if is_read:
                if len(self.frames) == 60:
                    self.frames = self.frames[1:]
                adjusted = self._apply_image_settings(im, self.settings)
                self.frames.append(adjusted)
            time.sleep(1 / self.settings.fps)
        self.logger.info('Thread stopped successfully')

    def _apply_image_settings(self, image, settings: CameraSettings):
        """
        Adjusts contrast and brightness of an uint8 image.
        contrast:   (0.0,  inf) with 1.0 leaving the contrast as is
        brightness: [-255, 255] with 0 leaving the brightness as is
        """
        brightness = settings.brightness + int(round(255 * (1 - settings.contrast) / 2))
        return cv2.addWeighted(image, settings.contrast, image, 0, brightness)

    def stop(self):
        """Stop the frame capture and destroy the thread."""
        self.logger.debug('Stopping thread')
        if self.is_running:
            self.thread.join()
            self.thread = None
            self.is_running = False
        self.camera.release()

    def get_last_frame(self, _bytes=True):
        """Try to return the most recent frame from the framebuffer. Otherwise, return a stub image."""
        if len(self.frames) > 0:
            if _bytes:
                img = cv2.imencode('.jpg', self.frames[-1])[1].tobytes()
            else:
                img = self.frames[-1]
        else:
            with open('images/not_found.jpeg', 'rb') as stub:
                img = stub.read()
        return img

    def save_photo(self, path):
        """Try to get the most recent frame from the framebuffer, make some adjustments and save it to the file."""
        if len(self.frames) == 0:
            self.logger.error('No frames captured from camera yet')
            return False

        self.logger.debug('Saving photo to %s', path)
        is_encoded, encoded_data = cv2.imencode('.jpg', self.frames[-1])
        if is_encoded and len(encoded_data) > 0:
            encoded_data.tofile(path)
            return True

        self.logger.error('Photo is not saved to %s', path)
        return False
