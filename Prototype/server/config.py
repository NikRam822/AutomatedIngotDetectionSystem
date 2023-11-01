import os
import logging
import logging.config

from configparser import ConfigParser
from csv_generator import generate_csv
from log_config import log_config

config_file = 'config.ini'
input_folder = 'data/input'
output_folder = 'data/marked'
csv_file_path = 'data/db/data.csv'

def configureServer():
    global config_file

    filepath = os.path.abspath(config_file)
    conf = ConfigParser()

    if os.path.exists(filepath):
        conf.read(filepath, encoding='utf-8')
    else:
        raise FileNotFoundError(f"Configuration file not found: {filepath}")

    if conf.has_section('directories'):
        directories = dict(conf.items('directories'))
    else:
        raise ValueError("Configuration file does not have the 'directories' section.")

    global input_folder
    global output_folder
    global csv_file_path

    db_folder = os.path.abspath(directories['database'])
    log_folder = os.path.abspath(directories['logs'])
    input_folder = os.path.abspath(directories['raw_images'])
    output_folder = os.path.abspath(directories['marked_images'])
    csv_file_path = os.path.join(db_folder, 'data.csv')

    os.makedirs(log_folder, exist_ok=True)
    os.makedirs(db_folder, exist_ok=True)
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    generate_csv(input_folder, csv_file_path)

    logging.config.dictConfig(log_config(os.path.join(log_folder, 'logfile.log')))
