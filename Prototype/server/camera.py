"""
The Camera module.
"""

import logging
import threading
import time

import cv2

class Camera:
    """It's a class that encapsulate all ther camera work."""
    def __init__(self, fps=20, video_source=0):
        self.logger = logging.getLogger(__name__)
        self.logger.info('Initializing camera class with %d fps and video_source=%d}', fps, video_source)

        self.fps = fps
        self.video_source = video_source
        self.camera = cv2.VideoCapture(video_source)
        self.frames = []
        self.is_running = False
        self.thread = None

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
        dt = 1 / self.fps
        self.logger.debug('Observation started')
        while self.is_running:
            is_read, im = self.camera.read()
            if is_read:
                if len(self.frames) == (self.fps * 2):
                    self.frames = self.frames[1:]
                self.frames.append(im)
            time.sleep(dt)
        self.logger.info('Thread stopped successfully')

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

    def save_photo(self, path, contrast, brightness):
        """Try to get the most recent frame from the framebuffer, make some adjustments and save it to the file."""
        if len(self.frames) == 0:
            self.logger.error('No frames captured from camera yet')
            return False

        self.logger.debug('Saving photo to %s', path)
        adjusted_frame = cv2.convertScaleAbs(self.frames[-1], alpha=contrast, beta=brightness)
        is_encoded, encoded_data = cv2.imencode('.jpg', adjusted_frame)
        if is_encoded and len(encoded_data) > 0:
            encoded_data.tofile(path)
            return True

        self.logger.error('Photo is not saved to %s', path)
        return False
