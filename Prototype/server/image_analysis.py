"""
Image Analysis module
The AI model should be integrated here.
"""

import logging
import random

class AI:
    """Class that implements all AI work. It should be initialized with the decisions list for consistency."""

    def __init__(self, decisions):
        self.logger = logging.getLogger(__name__)
        self.decisions = decisions

    def classify_image(self, filename):
        """Returns a predicted decision for the input image. Filename is the full path to the image."""

        # OVERRIDE POINT
        idx = random.randrange(0, len(self.decisions) - 1)
        self.logger.debug('Decision for ' + filename + ' is ' + self.decisions[idx].label)
        return self.decisions[idx]
