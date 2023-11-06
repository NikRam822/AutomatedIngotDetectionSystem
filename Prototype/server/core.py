"""
Core module
"""

import datetime
import os

import config
import events

import logging
import logging.config
from log_config import log_config

from csv_generator import generate_csv

class Core:
    def __init__(self, should_collect_events=False):
        self.config = config.Config('config.ini')
        logging.config.dictConfig(log_config(os.path.join(self.config.log_folder, 'logfile.log')))
        self.logger = logging.getLogger(__name__)

        self.logger.info(f"Initializing processing core...")

        generate_csv(self.config.input_folder, self.config.csv_file_path)

        if should_collect_events:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d")
            os.makedirs('../data/events/', exist_ok=True)
            self.event_collector = events.EventsCollector(f"../data/events/{current_time}.csv")
    
    def log_event(self, event):
        if not self.event_collector:
            return True
        if 'name' not in event:
            return False
        self.event_collector.save_event(event['name'], event['attributes'])
        return True