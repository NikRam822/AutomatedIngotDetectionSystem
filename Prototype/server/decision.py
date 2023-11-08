"""
Decision Object
Data class to organize more reliable work with assesment decisions.
"""

class Decision:
    def __init__(self, key, type, label):
        self.key = key
        self.type = type
        self.label = label

class Decisions:
    ok = Decision('OK', 'OK', 'OK')
    dross = Decision('DROSS', 'DEFECT', 'Dross')
    color = Decision('COLOR', 'DEFECT', 'Discolorage')
    no_ingot = Decision('EMPTY', 'IMAGE', 'No ingot')
    bad_image = Decision('BAD_IMAGE', 'IMAGE', 'Bad image')
