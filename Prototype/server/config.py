import os
import sys

from configparser import ConfigParser
from csv_generator import generate_csv

config = "config.ini"

if (len(sys.argv) > 1):
    config = sys.argv[1]

filepath = os.path.join(os.getcwd(), config)
conf = ConfigParser()
conf.read(filepath, encoding='utf-8')

directories = dict(conf.items('directories'))

csv_file_path = os.path.join(directories['database'], 'data.csv')
input_folder = directories['raw_images']
output_folder = directories['marked_images']

generate_csv(input_folder, csv_file_path)

os.makedirs(directories['database'], exist_ok=True)
os.makedirs(input_folder, exist_ok=True)
