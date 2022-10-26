from PyQt5.QtGui import QPainter, QBrush, QPen, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
import sys
import shutil

disk_data = shutil.disk_usage("/")

total = disk_data[0] / float(10.0 ** 9.0)
remaining = disk_data[1] / float(10.0 ** 9.0)
free = disk_data[2] / float(10.0 ** 9.0)
ratio = remaining / total
print(ratio)


class Window(QMainWindow):
    in_use = QLabel("In use")

    def __init__(self):
        super().__init__()
        self.title = "PyQt5 Drawing Tutorial"
        self.top = 150
        self.left = 150
        self.width = 750
        self.height = 500
        self.InitWindow()

    def InitWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.show()

    def paintEvent(self, event):
        # Get the bar dimensions
        bar_width = int(40 + (ratio * (self.width - 80)))
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
        painter.drawRect(margin, margin, self.width - (margin * 2), bar_height)

        # Draw bar
        painter.setPen(QPen(bar_color, border, Qt.SolidLine))
        painter.setBrush(QBrush(bar_color, Qt.SolidPattern))
        painter.drawRect(margin, margin, bar_width, bar_height)

        # Draw labels
        painter.setPen(QPen(fill_color, 2, Qt.SolidLine))
        # Used space
        label_a_x = margin + int(bar_width / 2)
        painter.drawLine(label_a_x, line_offset - 1, label_a_x, line_offset + line_length)

        # Unused space
        label_b_x = margin + bar_width + int((self.width - (margin * 2) - bar_width) / 2)
        painter.drawLine(label_b_x, line_offset - 1, label_b_x, line_offset + line_length)


App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())
