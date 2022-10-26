from PyQt5 import QtSvg
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QImage
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QPushButton

# For command line args
import sys

# For getting disk usage
import psutil, os


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


def get_directory_usage(directory):
    size = 0
    for ele in os.scandir(directory):
        add = 0
        try:
            add = os.stat(ele).st_size
        except Exception as e:
            print(e)
        size += add
    return size


# Get disk usage
def get_usage():
    # Gets a tuple with the info we need
    disk_data = psutil.disk_usage("/")

    # Process the disk data into a more readable form
    global total, usage, free, ratio
    total = disk_data[0] / float(10.0 ** 9.0)
    usage = disk_data[1] / float(10.0 ** 9.0)
    free = disk_data[2] / float(10.0 ** 9.0)
    ratio = disk_data[3] / 100


# Set the initial values
get_usage()

# Init the application
App = QApplication(sys.argv)


class StorageItem(QPushButton):
    hover = False
    index = 1

    def __init__(self, name, directory, parent):
        super().__init__(parent)

        # Constants for rendering
        text_height = 20
        vmargin = 15
        hmargin = 40

        # Set variables from arguments
        self.usage = get_directory_usage(directory) / float(10.0 ** 9.0)
        self.percent = psutil.disk_usage(directory)[3]
        self.name = name

        # Declare geometry
        geometry = self.parent().geometry()
        height = 70
        self.setGeometry(0, geometry.height() - (height * self.index), geometry.width(), height)

        # Set up labels
        self.name_label = QLabel(name, self)
        self.usage_label = QLabel("%.1f GB" % self.usage, self)
        self.percent_label = QLabel("%.1f%%" % self.percent, self)
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
        timer.setInterval(1000)
        timer.timeout.connect(self.update)
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
    StorageItem("Home", "/home/declan", window)
]
i = 1
for item in storage_items:
    item.index = i
    item.show()
    i = i + 1
sys.exit(App.exec())
