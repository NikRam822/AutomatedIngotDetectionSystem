"""
The Database module.
It encapsulates all the work related to store and fetch data from local DB.
"""

import os
import csv
import logging

class DatabaseRow:
    """Data class which represents a row from the database. It is needed for more strict control over field names and safety."""

    fields = ['ingot_id', 'camera_id', 'image_id', 'image_name', 'processing_mark', 'ml_mark', 'final_mark']

    def __init__(self, ingot_id:int, cam_id:int, img_id:int, img_name:str, pre_mark='', ml_mark='', final_mark=''):
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
            ingot_id=int(raw_value[DatabaseRow.fields[0]]),
            cam_id=int(raw_value[DatabaseRow.fields[1]]),
            img_id=int(raw_value[DatabaseRow.fields[2]]),
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

    def __init__(self, filepath):
        self.logger = logging.getLogger(__name__)
        self.logger.info('Initializing database at %s', filepath)
        self.csv_file_path = filepath
        self._create_file()

    def _create_file(self):
        """Try to create an empty database file if necessary"""
        if not os.path.exists(self.csv_file_path):
            self.logger.debug('Creating empty database...')
            with open(self.csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=DatabaseRow.fields)
                writer.writeheader()

    def append_to_db(self, ingot_id:int, camera_id:int, photo_name:str, pre_mark='', ml_mark=''):
        """Add a new row to the database."""
        self.logger.debug('Appending record for ingot=%d with cam_id=%d and photo_name=%s', ingot_id, camera_id, photo_name)
        with open(self.csv_file_path, mode='r', encoding='utf-8') as csv_file_read:
            rows = list(csv.DictReader(csv_file_read))
            if not rows or len(rows) == 0:
                last_id_img = 0
            else:
                raw_data = rows[-1]
                last_id_img = DatabaseRow.from_dict(raw_data).image_id

        img_id = last_id_img + 1

        with open(self.csv_file_path, mode='a', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=DatabaseRow.fields)
            new_record = DatabaseRow(
                ingot_id=ingot_id,
                cam_id=camera_id,
                img_id=img_id,
                img_name=photo_name,
                pre_mark=pre_mark,
                ml_mark=ml_mark
            )
            writer.writerow(new_record.raw_data())

    def next_unmarked(self):
        """Find the first row with empty 'final_mark' field."""
        self.logger.debug('Getting a record of next unmarked image...')
        with open(self.csv_file_path, mode='r', encoding='utf-8') as csv_file:
            rows = list(csv.DictReader(csv_file))

        for raw_row in rows:
            row = DatabaseRow.from_dict(raw_row)
            if row.final_mark == '':
                return row
        return None

    def update_mark(self, img_id:int, final_mark:str):
        """Set a final mark for the image and save it to the database."""
        self.logger.debug('Updating record with img_id=%d and mark=%s', img_id, final_mark)

        with open(self.csv_file_path, mode='r', encoding='utf-8') as csv_file:
            rows = list(csv.DictReader(csv_file))

        found_row = None
        for row in rows:
            if int(row['image_id']) == img_id:
                found_row = row
                break

        if found_row is None:
            return False

        found_row['final_mark'] = final_mark

        with open(self.csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=DatabaseRow.fields)
            writer.writeheader()
            writer.writerows(rows)

        return True
