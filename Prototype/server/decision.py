"""
Decision Object
Data class to organize more reliable work with assesment decisions.
"""

class Decision:
    """The data class to store decisions"""
    def __init__(self, key, kind, label):
        self.key = key
        self.kind = kind
        self.label = label

class Decisions:
    """Just a namespace to have all possible decisions in one place."""
    ok = Decision('OK', 'OK', 'OK')
    dross = Decision('DROSS', 'DEFECT', 'Dross')
    color = Decision('COLOR', 'DEFECT', 'Discolorage')
    no_ingot = Decision('EMPTY', 'IMAGE', 'No ingot')
    bad_image = Decision('BAD_IMAGE', 'IMAGE', 'Bad image')
