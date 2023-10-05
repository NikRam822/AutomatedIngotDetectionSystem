import sys
import os

import cv2
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QMessageBox
from PyQt6.QtGui import QPixmap
from PIL import Image

import read


class ImageChangerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.image_folder = "photos"
        self.image_files = [f for f in os.listdir(self.image_folder) if
                            f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        self.current_image_index = 0
        self.target_size = (400, 400)

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        self.scroll_area = QScrollArea(self)
        self.image_label = QLabel(self.scroll_area)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.image_label)

        self.layout.addWidget(self.scroll_area)

        btn_check = QPushButton('✅', self)
        btn_cross = QPushButton('❌', self)

        btn_check.clicked.connect(self.on_check_clicked)
        btn_cross.clicked.connect(self.on_check_clicked)

        self.layout.addWidget(btn_check)
        self.layout.addWidget(btn_cross)

        self.setLayout(self.layout)

        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle('Image Changer App')
        self.show()

        self.update_image()

    def update_image(self):
        if self.image_files:
            image_path = os.path.join(self.image_folder, self.image_files[self.current_image_index])

            try:
                original_image = Image.open(image_path)
                original_image = cv2.imread(image_path)
                _, filename = os.path.split(image_path)
                cropped_image = read.cropImage(original_image, filename)

                resized_image = cropped_image.resize(self.target_size, Image.LANCZOS)
                resized_image_path = os.path.join('output',
                                                  'cropped_' + self.image_files[self.current_image_index])
                resized_image.save(resized_image_path)




                # pixmap = QPixmap(resized_image_path)
                pixmap = QPixmap(cropped_image)
                self.image_label.setPixmap(pixmap)

                # os.remove(resized_image_path)
            except Exception as e:
                QMessageBox.warning(self, 'Ошибка', f'Ошибка при открытии изображения: {str(e)}')

    def on_check_clicked(self):
        self.current_image_index = (self.current_image_index + 1) % len(self.image_files)
        self.update_image()

    def on_cross_clicked(self):
        self.current_image_index = (self.current_image_index - 1) % len(self.image_files)
        self.update_image()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageChangerApp()
    sys.exit(app.exec())
