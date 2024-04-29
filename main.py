import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import time
import subprocess
import platform
from send2trash import send2trash

from findSimilarImages import find_similar_images


class window(QWidget):
    def __init__(self, parent=None):
        super(window, self).__init__(parent)
        self.setWindowTitle("Similar and Duplicate Image Finder")
        self.resize(1600, 1200)

        self.image_width = 128
        self.image_height = 128

        self.file_grid_size = [0, 0]

        self.setFocusPolicy(Qt.StrongFocus)  # Enable keyboard focus
        self.file_paths = []
        self.current_folder_path = ""
        self.selected_file_location = [0, 0]

        # Load the custom icon
        # Replace 'custom_icon.ico' with the path to your custom icon file
        icon = QIcon()
        icon.addFile('assets/icon.ico', QSize(16, 16))  # Add 16x16 icon size

        # Set the window icon
        self.setWindowIcon(icon)

        self.layout_main = QVBoxLayout(self)
        # Set margins from left and bottom
        self.layout_main.setContentsMargins(32, 32, 32, 32)

        #
        self.label_title = QLabel(
            "Find similar and duplicate images", self)
        self.layout_main.addWidget(self.label_title)

        #
        self.label_folder_info = QLabel(
            "No folder selected\n0 similar image pairs", self)
        self.layout_main.addWidget(self.label_folder_info)

        # select folder to open
        self.button_open_folder = QPushButton("Open folder", self)
        self.button_open_folder.clicked.connect(self.folder_opened)
        self.layout_main.addWidget(self.button_open_folder)

        # open selected folder
        self.button_open_folder = QPushButton(
            "Open folder in file explorer", self)
        self.button_open_folder.clicked.connect(
            self.open_folder_in_file_explorer)
        self.layout_main.addWidget(self.button_open_folder)

        # Create a scroll area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.layout_main.addWidget(self.scroll_area)

        # Create a widget to contain the labels in the scroll area
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()

        self.scroll_widget.setLayout(self.scroll_layout)

    def open_folder_in_file_explorer(self):
        try:
            if os.path.exists(self.current_folder_path):
                os.startfile(self.current_folder_path)
        except:
            print('error')

    def open_file_in_default_app(self, file_path):
        print('open')
        try:
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', file_path))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(file_path)
            else:                                   # linux variants
                subprocess.call(('xdg-open', file_path))
        except:
            print('error')

    def folder_opened(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            # self.button_folder.setText(folder_path)
            self.current_folder_path = folder_path
            print(folder_path)
            similar_files = find_similar_images(folder_path, 8, 75)
            self.label_folder_info.setText(folder_path)
            self.display_files(similar_files, folder_path)

    def list_files(self, folder_path):
        file_paths = []
        # Walk through the directory tree
        for root, directories, files in os.walk(folder_path):
            for filename in files:
                # Join the root path with the filename to get the complete file path
                file_path = os.path.join(root, filename)
                file_paths.append(file_path)
        return file_paths

    def display_files(self, files, folder_path):
        # get start time
        start = time.time()
        # Clear existing labels
        self.file_paths.clear()
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        num_files = len(files)
        self.label_folder_info.setText(
            folder_path+"\n"+str(num_files)+' similar image pairs found')

        if (num_files == 0):
            print('no similar image pairs found, aborting')
            return

        print(num_files, "similar image pairs found")

        for index, file_info in enumerate(files):

            # Create a container widget
            container_widget = QWidget()
            container_layout = QHBoxLayout(container_widget)
            container_layout.setContentsMargins(0, 0, 0, 0)

            # Image label
            image1_label = QLabel()
            image2_label = QLabel()
            # Set fixed size for image label
            image1_label.setFixedSize(
                self.image_width, self.image_height)
            image2_label.setFixedSize(
                self.image_width, self.image_height)
            image1_label.setStyleSheet("border: 1px solid black;")
            image2_label.setStyleSheet("border: 1px solid black;")
            pixmap1 = QPixmap(file_info[0])
            pixmap2 = QPixmap(file_info[1])
            if not pixmap1.isNull():
                pixmap1 = pixmap1.scaled(
                    self.image_width, self.image_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image1_label.setPixmap(pixmap1)
                image1_label.mouseDoubleClickEvent = lambda event, path=file_info[0]: self.open_file_in_default_app(
                    path)
            else:
                print('error getting pixmap for image1')
            if not pixmap2.isNull():
                pixmap2 = pixmap2.scaled(
                    self.image_width, self.image_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image2_label.setPixmap(pixmap2)
                image2_label.mouseDoubleClickEvent = lambda event, path=file_info[1]: self.open_file_in_default_app(
                    path)
            else:
                print('error getting pixmap for image2')

            # percentage label
            label_percentage = QLabel(str(file_info[2]) + "%")

            container_layout.addWidget(
                label_percentage, alignment=Qt.AlignCenter)
            # display images
            container_layout.addWidget(
                image1_label, alignment=Qt.AlignCenter)
            container_layout.addWidget(
                image2_label, alignment=Qt.AlignCenter)

            # delete button
            button_delete_file = QPushButton("Delete copy", self)
            button_delete_file.clicked.connect(
                lambda checked, index=index: self.deleteFile(files[index][1]))
            container_layout.addWidget(button_delete_file)

            # Add container widget to the scroll layout
            self.scroll_layout.addWidget(container_widget)

        # Set the scroll widget as the widget to be displayed in the scroll area
        self.scroll_area.setWidget(self.scroll_widget)
        # self.scroll_area.adjustSize()
        print('displayed images in', time.time()-start, "seconds")

    def deleteFile(self, path):
        try:
            path = path.replace('/', '\\')
            send2trash(path)
            print('deleted', path)
        except:
            print('error')


def main():
    app = QApplication(sys.argv)
    path = 'assets/icon.ico'
    app.setWindowIcon(QIcon(path))
    ex = window()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    print('\n')
    main()
