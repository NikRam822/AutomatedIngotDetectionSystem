"""
Events Collector module
"""

import logging
import csv
import datetime
import os

"""
EventsCollector class is needed to save user events for future analyzis.
Should be initialized with the valid path to the events.csv file.
"""
class EventsCollector:
    def __init__(self, filepath):
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing events collector at {filepath}")
        self.csv_file_path = filepath
        self.fieldnames = ['timestamp', 'event', 'attributes']
        self._create_file()

    def save_event(self, event, attributes):
        self.logger.debug(f"Saving event {event} with {attributes}")

        with open(self.csv_file_path, mode='a', newline='', encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            writer.writerow({
                'timestamp': datetime.datetime.now(),
                'event': event,
                'attributes': attributes
            })

    def _create_file(self):
        if not os.path.exists(self.csv_file_path):
            with open(self.csv_file_path, mode='w', newline='', encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
                writer.writeheader()