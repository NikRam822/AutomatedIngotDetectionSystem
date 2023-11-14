"""
Events Collector module
"""

import logging
import csv
import datetime
import os

class EventsCollector:
    """
    EventsCollector class is needed to save user events for future analyzis.
    Should be initialized with the valid path to the events.csv file.
    """
    def __init__(self, directory):
        self.logger = logging.getLogger(__name__)
        self.logger.info('Initializing events collector at %s', directory)
        self.directory = directory
        self.fieldnames = ['timestamp', 'event', 'attributes']

    def save_event(self, event, attributes):
        """Add a new event row to the database."""
        self.logger.debug('Saving event %s with %s', event, str(attributes))

        filepath = self._get_log_filepath()
        self._create_file_if_necessary(filepath)

        with open(filepath, mode='a', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            writer.writerow({
                'timestamp': datetime.datetime.now(),
                'event': event,
                'attributes': attributes
            })

    def _get_log_filepath(self):
        """Get a full path for the current logfile"""
        name = datetime.date.today().strftime('log-%Y-%m-%d.csv')
        return os.path.join(self.directory, name)

    def _create_file_if_necessary(self, filename):
        """Try to create an empty events database file if necessary"""
        if not os.path.exists(filename):
            with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
                writer.writeheader()
