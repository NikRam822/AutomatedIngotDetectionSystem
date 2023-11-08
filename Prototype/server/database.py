"""
The Database module.
It encapsulates all the work related to store and fetch data from local DB.
"""

import os
import csv
import logging

class DB_row:
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
    def from_dict(cls, rawValue):
        return cls(
            ingot_id=int(rawValue[DB_row.fields[0]]), 
            cam_id=int(rawValue[DB_row.fields[1]]), 
            img_id=int(rawValue[DB_row.fields[2]]), 
            img_name=rawValue[DB_row.fields[3]], 
            pre_mark=rawValue[DB_row.fields[4]], 
            ml_mark=rawValue[DB_row.fields[5]],
            final_mark=rawValue[DB_row.fields[6]]
        )

    def raw_data(self):
        return {
            DB_row.fields[0]: self.ingot_id,
            DB_row.fields[1]: self.camera_id,
            DB_row.fields[2]: self.image_id,
            DB_row.fields[3]: self.image_name,
            DB_row.fields[4]: self.pre_mark,
            DB_row.fields[5]: self.ml_mark,
            DB_row.fields[6]: self.final_mark
        }

class Database:
    def __init__(self, filepath):
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing database at {filepath}")
        self.csv_file_path = filepath
        self._create_file()

    def _create_file(self):
        if not os.path.exists(self.csv_file_path):
            self.logger.debug("Creating empty database...")
            with open(self.csv_file_path, mode='w', newline='', encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=DB_row.fields)
                writer.writeheader()

    def update_from_folder(self, image_folder):
        self.logger.debug(f"Appending images from {image_folder}")
        image_files = [f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.jpeg', '.png'))]

        # TODO: Remove files that are already in the database

        with open(self.csv_file_path, mode='a', newline='', encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            for idx, image_file in enumerate(image_files, start=1):
                image_path = os.path.join(image_folder, image_file)
                row = DB_row(ingot_id=0, cam_id=0, img_id=idx, img_path=image_path)
                writer.writerow(row.raw_data())

    def append_to_db(self, ingot_id:int, camera_id:int, photo_name:str, pre_mark='', ml_mark=''):
        self.logger.debug(f"Appending record for ingot={ingot_id} with cam_id={camera_id} and photo_name={photo_name}")
        with open(self.csv_file_path, mode='r') as csv_file_read:
            rows = list(csv.DictReader(csv_file_read))
            if not rows or len(rows) == 0:
                last_id_img = 0
            else:
                raw_data = rows[-1]
                last_id_img = DB_row.from_dict(raw_data).image_id

        img_id = last_id_img + 1

        with open(self.csv_file_path, mode='a', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=DB_row.fields)
            new_record = DB_row(
                ingot_id=ingot_id, 
                cam_id=camera_id, 
                img_id=img_id, 
                img_name=photo_name, 
                pre_mark=pre_mark, 
                ml_mark=ml_mark
            )
            writer.writerow(new_record.raw_data())

    def next_unmarked(self):
        self.logger.debug("Getting a record of next unmarked image...")
        with open(self.csv_file_path, mode='r') as csv_file:
            rows = list(csv.DictReader(csv_file))

        for rawRow in rows:
            row = DB_row.from_dict(rawRow)
            if row.final_mark == '':
                return row
        return None

    def update_mark(self, img_id:int, final_mark:str):
        self.logger.debug(f"Updating record with img_id={img_id} and mark={final_mark}")

        with open(self.csv_file_path, mode='r') as csv_file:
            rows = list(csv.DictReader(csv_file))

        found_row = None
        for row in rows:
            if int(row['image_id']) == img_id:
                found_row = row
                break

        if found_row is None:
            return False

        found_row['final_mark'] = final_mark

        with open(self.csv_file_path, mode='w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=DB_row.fields)
            writer.writeheader()
            writer.writerows(rows)

        return True
