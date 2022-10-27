# PyQt Imports
from PyQt5 import QtSvg
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton

# For command line args
import sys

# For getting disk usage
from pathlib import Path
import os
import psutil
import threading

# Init the application
App = QApplication(sys.argv)

# Choose paths based on platform
home = str(Path.home())
if os.name == "nt":
    root = "C:\\"

    app_dirs = []

    user_dirs = [home]

    temp_dirs = []

    sys_dirs = os.listdir(root)
    sys_dirs.remove("Users")
    for i in range(0, len(sys_dirs)):
        sys_dirs[i] = root + sys_dirs[i]
else:
    root = "/"

    app_dirs = [
        "/usr/local",
        "/usr/share",
        home + "/.local",
        "/opt"
    ]

    user_dirs = os.listdir(home)
    user_dirs.remove(".local")
    user_dirs.remove(".config")
    for i in range(0, len(user_dirs)):
        user_dirs[i] = home + "/" + user_dirs[i]

    temp_dirs = [
        "/tmp",
        home + "/.config"
    ]

    sys_dirs = [
        "etc"
    ]
    for i in range(0, len(sys_dirs)):
        sys_dirs[i] = root + sys_dirs[i]
    for item in os.listdir("/usr"):
        if item != "share" and item != "local":
            sys_dirs.append(f"/usr/{item}")


# Colour class using RGB to simplify colour definitions
class Colour:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def get_style(self):
        return f"rgba({self.r}, {self.g}, {self.b}, 255)"

    def get_qcolor(self):
        return QColor.fromRgbF(self.r / 255, self.g / 255, self.b / 255, 1)


# Disk usage variables
total = float()
usage = float()
free = float()
ratio = float()

# Colour palette
light_grey = Colour(189, 193, 198)
border_grey = Colour(83, 84, 86)
grey = Colour(63, 64, 66)
dark_grey = Colour(41, 42, 45)
blue = Colour(138, 180, 248)


def human_readable(num):
    if num / float(1000 ** 3) > 1:
        return "%.1f GB" % (num / float(1000 ** 3))
    elif num / float(1000 * 2) > 1:
        return "%.1f MB" % (num / float(1000 ** 2))
    elif num / 1000 > 1:
        return "%.1f KB" % (num / 1000)
    else:
        return "%.1f B" % num


def async_directory_usage(directory, index):
    for path, names, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(path, f)

            # Avoid any symlinks or mount points
            if not (os.path.islink(fp) or os.path.ismount(fp)):
                try:
                    storage_items[index - 1].usage += os.path.getsize(fp)
                except Exception as e:
                    print(e)

    storage_items[index - 1].thread_done = True
    storage_items[index - 1].update_size()


def get_directory_usage(directory):
    size = 0
    for path, names, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(path, f)

            # Avoid any symlinks or mount points
            if not (os.path.islink(fp) or os.path.ismount(fp)):
                try:
                    size += os.path.getsize(fp)
                except Exception as e:
                    print(e)
    return size


# Get disk usage
def get_usage():
    # Gets a tuple with the info we need
    disk_data = psutil.disk_usage(root)

    # Process the disk data into a more readable form
    global total, usage, free, ratio
    total = disk_data[0] / float(1000 ** 3)
    usage = disk_data[1] / float(1000 ** 3)
    free = disk_data[2] / float(1000 ** 3)
    ratio = disk_data[3] / 100


# Classes
class StorageItem(QPushButton):
    hover = False
    index = 1

    # Usage metrics
    usage = 0
    percent = 0
    directories = list()

    # For getting size
    thread_done = False

    def queue_size_get(self):
        self.thread_done = False
        self.thread = threading.Thread(target=async_directory_usage, name=self.directories[0],
                                       args=[self.directories[0], self.index])
        self.thread.start()

    def update_size(self):
        if self.thread_done and len(self.directories) > 1:
            self.directories.pop(0)
            self.queue_size_get()

    def update(self):
        self.percent = self.usage / (usage * float(1000 ** 3))
        self.usage_label.setText(human_readable(self.usage))
        if self.thread_done:
            self.percent_label.setText("%.1f%%" % (self.percent * 100))
        else:
            self.percent_label.setText("Calculating...")
        super(StorageItem, self).update()

    def __init__(self, name, directories, parent):
        super().__init__(parent)

        # Constants for rendering
        text_height = 20
        vmargin = 15
        hmargin = 40

        # Set variables from arguments
        self.directories = directories
        self.name = name

        # Prototype thread for queue_size_get()
        self.thread = None

        # Declare geometry
        geometry = self.parent().geometry()
        height = 70
        self.setGeometry(0, geometry.height() - (height * self.index), geometry.width(), height)

        # Set up labels
        self.name_label = QLabel(name, self)
        self.usage_label = QLabel(human_readable(self.usage), self)
        self.percent_label = QLabel("%.1f%%" % (self.percent * 100), self)
        self.name_label.setGeometry(hmargin, vmargin, self.name_label.width(), text_height)
        self.usage_label.setGeometry(hmargin, vmargin + text_height, self.usage_label.width(), text_height)
        self.percent_label.setGeometry(hmargin + 70, vmargin + text_height, self.usage_label.width(), text_height)

        # Set up styles
        self.name_label.setStyleSheet("""
        color: white;
        background-color: rgba(0,0,0,0);""")
        self.usage_label.setStyleSheet("color: %s;" % light_grey.get_style() + "background-color: rgba(0,0,0,0);")
        self.percent_label.setStyleSheet("color: %s;" % light_grey.get_style() + "background-color: rgba(0,0,0,0);")

        # Set up open icon
        self.link_icon = QtSvg.QSvgWidget("link.svg", self)
        self.link_icon.setGeometry(geometry.width() - int(height / 2) - 8, int(height / 2) - 8, 16, 16)
        self.link_icon.setStyleSheet("background-color: rgba(0,0,0,0);")
        self.link_icon.show()

    def enterEvent(self, event):
        self.hover = True

    def leaveEvent(self, event):
        self.hover = False

    def paintEvent(self, event):
        # Update geometry
        geometry = self.parent().geometry()
        height = 70
        self.setGeometry(0, geometry.height() - (height * self.index), geometry.width(), height)

        # Update link icon
        self.link_icon.setGeometry(geometry.width() - int(height / 2) - 8, int(height / 2) - 8, 16, 16)

        # Init painter
        painter = QPainter(self)

        # Draw bar background
        painter.setPen(QPen(border_grey.get_qcolor(), 1, Qt.SolidLine))
        if self.hover:
            painter.setBrush(QBrush(grey.get_qcolor(), Qt.SolidPattern))
        else:
            painter.setBrush(QBrush(dark_grey.get_qcolor(), Qt.SolidPattern))
        painter.drawRect(-1, 1, self.geometry().width() + 2, self.geometry().height())


class Window(QMainWindow):
    usage_label = QLabel()
    usage_value_label = QLabel()
    free_label = QLabel()
    free_value_label = QLabel()

    def updateAll(self):
        self.update()
        for storage in storage_items:
            storage.update()

    def __init__(self):
        super().__init__()

        # Set the style
        self.setStyleSheet("background-color: %s;" % dark_grey.get_style())

        # Set up the window
        self.setWindowTitle("Storage Manager")
        self.setGeometry(150, 150, 750, 500)
        self.show()

        # Create labels
        self.usage_label = QLabel("In use", self)
        self.usage_label.setStyleSheet("color: white;")
        self.usage_label.show()
        self.usage_value_label = QLabel("%.1f GB" % usage, self)
        self.usage_value_label.setStyleSheet("color: %s;" % light_grey.get_style())
        self.usage_value_label.show()
        self.free_label = QLabel("Available", self)
        self.free_label.setStyleSheet("color: white;")
        self.free_label.show()
        self.free_value_label = QLabel("%.1f GB" % free, self)
        self.free_value_label.setStyleSheet("color: %s;" % light_grey.get_style())
        self.free_value_label.show()

        # Set the alignment
        self.usage_label.setAlignment(Qt.AlignCenter)
        self.usage_value_label.setAlignment(Qt.AlignCenter)
        self.free_label.setAlignment(Qt.AlignCenter)
        self.free_value_label.setAlignment(Qt.AlignCenter)

        # Update the window every second
        timer = QTimer(self)
        timer.setInterval(200)
        timer.timeout.connect(self.updateAll)
        timer.start()

    def updateLabels(self):
        self.usage_value_label.setText("%.1f GB" % usage)
        self.free_value_label.setText("%.1f GB" % free)

    def paintEvent(self, event):
        # Ensure our disk usage variables are up to date
        get_usage()
        self.updateLabels()

        # Get the bar dimensions
        bar_width = int(ratio * (self.frameGeometry().width() - 80))
        bar_height = 30
        margin = 40
        border = 5

        # Get label dimensions
        line_offset = margin + bar_height + border
        line_length = 7

        # Init painter
        painter = QPainter(self)

        # Draw bar background
        painter.setPen(QPen(grey.get_qcolor(), border, Qt.SolidLine))
        painter.setBrush(QBrush(grey.get_qcolor(), Qt.SolidPattern))
        painter.drawRect(margin, margin, self.frameGeometry().width() - (margin * 2), bar_height)

        # Draw bar
        painter.setPen(QPen(blue.get_qcolor(), border, Qt.SolidLine))
        painter.setBrush(QBrush(blue.get_qcolor(), Qt.SolidPattern))
        painter.drawRect(margin, margin, bar_width, bar_height)

        # Draw labels
        painter.setPen(QPen(grey.get_qcolor(), 2, Qt.SolidLine))

        # Used space
        label_a_x = margin + int(bar_width / 2)
        painter.drawLine(label_a_x, line_offset - 1, label_a_x, line_offset + line_length)
        self.usage_label.setGeometry(label_a_x - 20, line_offset + line_length + 5, 40, 10)
        self.usage_value_label.setGeometry(label_a_x - 30, line_offset + line_length + 22, 60, 10)

        # Unused space
        label_b_x = margin + bar_width + int((self.frameGeometry().width() - (margin * 2) - bar_width) / 2)
        painter.drawLine(label_b_x, line_offset - 1, label_b_x, line_offset + line_length)
        self.free_label.setGeometry(label_b_x - 30, line_offset + line_length + 5, 60, 10)
        self.free_value_label.setGeometry(label_b_x - 30, line_offset + line_length + 22, 60, 10)


window = Window()
storage_items = [
    StorageItem("System", sys_dirs, window),
    StorageItem("Applications", app_dirs, window),
    StorageItem("User data", temp_dirs, window),
    StorageItem("My files", user_dirs, window)
]

# Set the initial values
get_usage()

# Show all the storage items
i = 1
for item in storage_items:
    item.index = i
    item.queue_size_get()
    item.show()
    i = i + 1

sys.exit(App.exec())
