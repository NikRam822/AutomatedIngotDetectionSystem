import os
from csv_generator import generate_csv
from configparser import ConfigParser

class Config:
    def __init__(self, filepath):
        self.config_file = filepath
        self.input_folder = 'data/input'
        self.output_folder = 'data/marked'
        self.csv_file_path = 'data/db/data.csv'
        self.experiments = []

        fullpath = os.path.abspath(filepath)
        conf = ConfigParser()

        if os.path.exists(fullpath):
            conf.read(fullpath, encoding='utf-8')
        else:
            raise FileNotFoundError(f"Configuration file not found: {fullpath}")

        self._read_config(conf)
        self._read_experiments(conf)
        self._make_dirs()

    def _read_config(self, conf):
        if conf.has_section('directories'):
            directories = dict(conf.items('directories'))
        else:
            raise ValueError("Configuration file does not have the 'directories' section.")

        self.db_folder = os.path.abspath(directories['database'])
        self.log_folder = os.path.abspath(directories['logs'])
        self.input_folder = os.path.abspath(directories['raw_images'])
        self.output_folder = os.path.abspath(directories['marked_images'])
        self.csv_file_path = os.path.join(self.db_folder, 'data.csv')

    def _read_experiments(self, conf):
        if conf.has_section('experiments'):
            raw_experiments = dict(conf.items('experiments'))
            self.experiments = [k for k, v in raw_experiments.items() if int(v) == 1]

    def _make_dirs(self):
        os.makedirs(self.log_folder, exist_ok=True)
        os.makedirs(self.db_folder, exist_ok=True)
        os.makedirs(self.input_folder, exist_ok=True)
        os.makedirs(self.output_folder, exist_ok=True)
