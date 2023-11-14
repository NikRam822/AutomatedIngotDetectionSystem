"""
The Database module.
It encapsulates all the work related to store and fetch data from local DB.
"""

import os
import csv
import logging

from datetime import datetime, timedelta

class DatabaseRow:
    """Data class which represents a row from the database. It is needed for more strict control over field names and safety."""

    fields = ['ingot_id', 'camera_id', 'image_id', 'image_name', 'processing_mark', 'ml_mark', 'final_mark']

    def __init__(self, ingot_id:str, cam_id:str, img_id:str, img_name:str, pre_mark='', ml_mark='', final_mark=''):
        self.ingot_id = ingot_id
        self.camera_id = cam_id
        self.image_id = img_id
        self.image_name = img_name
        self.pre_mark = pre_mark
        self.ml_mark = ml_mark
        self.final_mark = final_mark

    @classmethod
    def from_dict(cls, raw_value):
        """Create an instance object from dictionary."""
        return cls(
            ingot_id=raw_value[DatabaseRow.fields[0]],
            cam_id=raw_value[DatabaseRow.fields[1]],
            img_id=raw_value[DatabaseRow.fields[2]],
            img_name=raw_value[DatabaseRow.fields[3]],
            pre_mark=raw_value[DatabaseRow.fields[4]],
            ml_mark=raw_value[DatabaseRow.fields[5]],
            final_mark=raw_value[DatabaseRow.fields[6]]
        )

    def raw_data(self):
        """Make a dictionary from the object"""
        return {
            DatabaseRow.fields[0]: self.ingot_id,
            DatabaseRow.fields[1]: self.camera_id,
            DatabaseRow.fields[2]: self.image_id,
            DatabaseRow.fields[3]: self.image_name,
            DatabaseRow.fields[4]: self.pre_mark,
            DatabaseRow.fields[5]: self.ml_mark,
            DatabaseRow.fields[6]: self.final_mark
        }

class Database:
    """The Database class which encapsulates all the work with data files."""

    search_depth = 7

    def __init__(self, directory):
        self.logger = logging.getLogger(__name__)
        self.logger.info('Initializing database at %s', directory)
        self.directory = directory

    def append_to_db(self, ingot_id:str, camera_id:str, photo_name:str, pre_mark='', ml_mark=''):
        """Add a new row to the database and return it to the caller."""
        self.logger.debug('Appending record for ingot=%s with cam_id=%s and photo_name=%s', ingot_id, camera_id, photo_name)

        filepath = self._get_filepath()
        self._create_file_if_necessary(filepath)

        with open(filepath, mode='r', encoding='utf-8') as csv_file_read:
            rows = list(csv.DictReader(csv_file_read))
            if not rows or len(rows) == 0:
                image_id = self._next_image_id()
            else:
                raw_data = rows[-1]
                last_img_id = DatabaseRow.from_dict(raw_data).image_id
                image_id = self._next_image_id(last_img_id)

        new_record = DatabaseRow(
            ingot_id=ingot_id,
            cam_id=camera_id,
            img_id=image_id,
            img_name=photo_name,
            pre_mark=pre_mark,
            ml_mark=ml_mark
        )

        with open(filepath, mode='a', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=DatabaseRow.fields)
            writer.writerow(new_record.raw_data())

    def last_unmarked(self):
        """Find the first row with empty 'final_mark' field."""
        self.logger.debug('Getting a record of next unmarked image...')
        return self._get_last_unmarked()

    def update_mark(self, img_id:str, final_mark:str):
        """Set a final mark for the image and save it to the database."""
        self.logger.debug('Updating record with img_id=%s and mark=%s', img_id, final_mark)

        filename = self._db_file_for_image(img_id)
        if not filename or not os.path.exists(filename):
            return False

        with open(filename, mode='r', encoding='utf-8') as csv_file:
            rows = list(csv.DictReader(csv_file))

        found_row = None
        for row in rows:
            if row['image_id'] == img_id:
                found_row = row
                break

        if found_row is None:
            return False

        found_row['final_mark'] = final_mark

        with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=DatabaseRow.fields)
            writer.writeheader()
            writer.writerows(rows)

        return True

    def _get_filepath(self, days_before=0):
        """Get a full path for the current databases file"""
        date = datetime.today() - timedelta(days=days_before)
        name = date.strftime('db-%Y-%m-%d.csv')
        return os.path.join(self.directory, name)

    def _create_file_if_necessary(self, filename):
        """Try to create an empty database file if necessary"""
        if not os.path.exists(filename):
            with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=DatabaseRow.fields)
                writer.writeheader()

    def _next_image_id(self, image_id:str=None):
        """Create an image ID next to the provided one"""
        if not image_id:
            return datetime.today().strftime('%Y%m%d_000000')
        parts = image_id.split('_', 1)
        if len(parts) is not 2:
            return datetime.today().strftime('%Y%m%d_000000')
        idx = int(parts[1]) + 1
        return f'{parts[0]}_{idx:06d}'

    def _db_file_for_image(self, image_id:str):
        """Get DB file name for provided image ID"""
        parts = image_id.split('_', 1)
        if len(parts) is not 2:
            return None
        date = datetime.strptime(parts[0], '%Y%m%d').date()
        name = date.strftime('db-%Y-%m-%d.csv')
        return os.path.join(self.directory, name)

    def _get_last_unmarked(self, days_before=0):
        """Search for unmarked image recursively"""
        filepath = self._get_filepath(days_before)
        if not os.path.exists(filepath):
            return None

        with open(filepath, mode='r', encoding='utf-8') as csv_file:
            rows = list(csv.DictReader(csv_file))

        for raw_row in reversed(rows):
            row = DatabaseRow.from_dict(raw_row)
            if row.final_mark == '':
                return row

        if days_before >= self.search_depth:
            return None

        return self._get_last_unmarked(days_before + 1)
