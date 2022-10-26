from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
import sys
import shutil

App = QApplication(sys.argv)

disk_data = shutil.disk_usage("/")

total = disk_data[0] / float(10.0 ** 9.0)
usage = disk_data[1] / float(10.0 ** 9.0)
free = disk_data[2] / float(10.0 ** 9.0)
ratio = usage / total
print(usage)
print(free)

class Window(QMainWindow):
    usage_label = QLabel()
    usage_value_label = QLabel()
    free_label = QLabel()
    free_value_label = QLabel()

    def __init__(self):
        super().__init__()

        # Set up the style
        self.setStyleSheet("background-color: rgba(41,42,45,255);")

        # Window dimensions
        self.top = 150
        self.left = 150
        self.width = 750
        self.height = 500

        # Init the window
        self.title = "PyQt5 Drawing Tutorial"
        self.InitWindow()

        # Create labels
        self.usage_label = QLabel("In use", self)
        self.usage_label.setStyleSheet("color: white;")
        self.usage_label.show()
        self.usage_value_label = QLabel("%.1f GB" % usage, self)
        self.usage_value_label.setStyleSheet("color: rgba(140, 148, 148, 255);")
        self.usage_value_label.show()
        self.free_label = QLabel("Available", self)
        self.free_label.setStyleSheet("color: white;")
        self.free_label.show()
        self.free_value_label = QLabel("%.1f GB" % free, self)
        self.free_value_label.setStyleSheet("color: rgba(140, 148, 148, 255);")
        self.free_value_label.show()

    def InitWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.show()

    def paintEvent(self, event):
        # Get the bar dimensions
        bar_width = int(40 + (ratio * (self.frameGeometry().width() - 80)))
        bar_height = 30
        margin = 40
        border = 5

        # Get label dimensions
        line_offset = margin + bar_height + border
        line_length = 7

        # Define colors
        bar_color = QColor.fromRgbF(138 / 255, 180 / 255, 248 / 255, 1)
        fill_color = QColor.fromRgbF(63.0 / 255.0, 64.0 / 255.0, 66.0 / 255.0, 1.0)

        # Init painter
        painter = QPainter(self)

        # Draw bar background
        painter.setPen(QPen(fill_color, border, Qt.SolidLine))
        painter.setBrush(QBrush(fill_color, Qt.SolidPattern))
        painter.drawRect(margin, margin, self.frameGeometry().width() - (margin * 2), bar_height)

        # Draw bar
        painter.setPen(QPen(bar_color, border, Qt.SolidLine))
        painter.setBrush(QBrush(bar_color, Qt.SolidPattern))
        painter.drawRect(margin, margin, bar_width, bar_height)

        # Draw labels
        painter.setPen(QPen(fill_color, 2, Qt.SolidLine))
        # Used space
        label_a_x = margin + int(bar_width / 2)
        painter.drawLine(label_a_x, line_offset - 1, label_a_x, line_offset + line_length)
        self.usage_label.setAlignment(Qt.AlignCenter)
        self.usage_label.setGeometry(label_a_x - 20, line_offset + line_length + 5, 40, 10)
        self.usage_value_label.setAlignment(Qt.AlignCenter)
        self.usage_value_label.setGeometry(label_a_x - 30, line_offset + line_length + 22, 60, 10)

        # Unused space
        label_b_x = margin + bar_width + int((self.frameGeometry().width() - (margin * 2) - bar_width) / 2)
        painter.drawLine(label_b_x, line_offset - 1, label_b_x, line_offset + line_length)
        self.free_label.setAlignment(Qt.AlignCenter)
        self.free_label.setGeometry(label_b_x - 30, line_offset + line_length + 5, 60, 10)
        self.free_value_label.setAlignment(Qt.AlignCenter)
        self.free_value_label.setGeometry(label_b_x - 30, line_offset + line_length + 22, 60, 10)


window = Window()
sys.exit(App.exec())
