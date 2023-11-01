"""
The Camera module.
"""

import cv2
import threading
import time
import logging

LOGGER = logging.getLogger(__name__)
THREAD = None

"""
It's a class that incapsulate all ther camera work.
"""
class Camera:
    def __init__(self, fps=20, video_source=0):
        LOGGER.info(f"Initializing camera class with {fps} fps and video_source={video_source}")
        self.fps = fps
        self.video_source = video_source
        self.camera = cv2.VideoCapture(video_source)
        # We want a max of 2s history to be stored, thats 5s*fps
        self.max_frames = 2 * fps
        self.frames = []
        self.is_running = False

    def is_available(self):
        logging.debug("Checking camera " + str(self.video_source))
        if self.camera.read()[0]:
            return True
        else:
            return False

    def run(self):
        logging.debug("Perparing thread")
        global THREAD
        if THREAD is None:
            logging.debug("Creating thread")
            THREAD = threading.Thread(target=self._capture_loop, daemon=True)
            LOGGER.debug("Starting thread")
            self.is_running = True
            THREAD.start()
            LOGGER.info("Thread started")

    def _capture_loop(self):
        dt = 1 / self.fps
        LOGGER.debug("Observation started")
        while self.is_running:
            is_read, im = self.camera.read()
            if is_read:
                if len(self.frames) == self.max_frames:
                    self.frames = self.frames[1:]
                self.frames.append(im)
            time.sleep(dt)
        LOGGER.info("Thread stopped successfully")

    def stop(self):
        LOGGER.debug("Stopping thread")
        self.is_running = False

    def get_last_frame(self, _bytes=True):
        if len(self.frames) > 0:
            if _bytes:
                img = cv2.imencode('.jpg', self.frames[-1])[1].tobytes()
            else:
                img = self.frames[-1]
        else:
            with open("images/not_found.jpeg","rb") as stub:
                img = stub.read()
        return img

    def save_photo(self, path, contrast, brightness):
        if len(self.frames) == 0:
            LOGGER.error("No frames captured from camera yet")
            return False

        LOGGER.debug("Saving photo to " + path)
        adjustedFrame = cv2.convertScaleAbs(self.frames[-1], alpha=contrast, beta=brightness)
        isEncoded, encodedData = cv2.imencode('.jpg', adjustedFrame)
        if isEncoded and len(encodedData) > 0:
            encodedData.tofile(path)
            return True

        LOGGER.error("Photo is not saved to " + path)
        return False


def get_all_cameras():
    cameras_id = []
    for camera_id in range(10):
        camera = Camera(fps=1, video_source=camera_id)
        if camera.is_available():
            cameras_id.append(camera_id)

    return cameras_id
