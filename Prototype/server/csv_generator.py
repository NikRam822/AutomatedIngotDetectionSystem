import os
import csv

def generate_csv(image_folder, csv_file_path):
    # Get the list of files in the folder with images
    image_files = [f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.jpeg', '.png'))]

    # Create CSV file
    with open(csv_file_path, mode='w', newline='') as csv_file:
        fieldnames = ['id_camera', 'id_img', 'source_img', 'text']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write down the title
        writer.writeheader()

        # Write data for each image
        for idx, image_file in enumerate(image_files, start=1):
            image_path = os.path.join(image_folder, image_file)
            writer.writerow({
                'id_camera': '1',
                'id_img': str(idx),
                'source_img': image_path,
                'text': ''
            })

if __name__ == '__main__':
    # Specify the path to the folder with images and the path to save the CSV file
    image_folder_path = 'output'
    csv_file_path = 'data.csv'

    generate_csv(image_folder_path, csv_file_path)
    print(f"CSV file generated at {csv_file_path}")
