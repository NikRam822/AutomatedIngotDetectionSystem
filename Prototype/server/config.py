import os
import sys
from configparser import ConfigParser
from csv_generator import generate_csv

config_file = "config.ini"

if len(sys.argv) > 1:
    config_file = sys.argv[1]

filepath = os.path.join(os.getcwd(), "config.ini")
conf = ConfigParser()

# Read the configuration file
if os.path.exists(filepath):
    conf.read(filepath, encoding='utf-8')
else:
    raise FileNotFoundError(f"Configuration file not found: {filepath}")

# Check if 'directories' section is present
if conf.has_section('directories'):
    directories = dict(conf.items('directories'))
else:
    raise ValueError("Configuration file does not have the 'directories' section.")

csv_file_path = os.path.join(directories['database'], 'data.csv')
input_folder = directories['raw_images']
output_folder = directories['marked_images']

generate_csv(input_folder, csv_file_path)

os.makedirs(directories['database'], exist_ok=True)
os.makedirs(input_folder, exist_ok=True)
