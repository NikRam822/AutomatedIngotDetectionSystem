"""
Image Analysis module
The AI model should be integrated here.
"""

import random

from decision import Decisions

def classify_image(filename):
    all = [ Decisions.ok, Decisions.dross, Decisions.color, Decisions.no_ingot, Decisions.bad_image ]
    idx = random.randrange(0, len(all) - 1)
    return all[idx]
