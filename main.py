# PyQt Imports
from PyQt5 import QtSvg
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QAction, QMenu

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
    for i in range(0, len(user_dirs)):
        user_dirs[i] = home + "/" + user_dirs[i]

    temp_dirs = [
        "/tmp",
        f"{home}/Trash"
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


# Colour palette
light_grey = Colour(189, 193, 198)
border_grey = Colour(83, 84, 86)
grey = Colour(63, 64, 66)
dark_grey = Colour(41, 42, 45)
blue = Colour(138, 180, 248)
red = Colour(248, 180, 138)

# Declare CSS
CSS = """
QMenu {
    padding: 5px;
    border: 1px solid """ + border_grey.get_style() + """;
}
QMenu::item {
    padding: 5px;
}
QMenu::item:selected { 
    background-color: """ + border_grey.get_style() + """;
    color: white;
}
QMenu::separator {
    height: 1px;
    width: 100%;
    background: """ + border_grey.get_style() + """;
}
"""
App.setStyleSheet(CSS)

# Disk usage variables
total = float()
usage = float()
free = float()
ratio = float()


def human_readable(num):
    if num / float(1000 ** 3) > 1:
        return "%.1f GB" % (num / float(1000 ** 3))
    elif num / float(1000 * 2) > 1:
        return "%.1f MB" % (num / float(1000 ** 2))
    elif num / 1000 > 1:
        return "%.1f KB" % (num / 1000)
    else:
        return "%.1f B" % num


def async_directory_usage(directories, index):
    for directory in directories:
        for path, names, filenames in os.walk(directory):
            for f in filenames:
                fp = os.path.join(path, f)

                # Avoid any symlinks
                if not os.path.islink(fp):
                    storage_items[index - 1].usage += os.path.getsize(fp)

            # Return if thread done
            if storage_items[index - 1].thread_done:
                return

    storage_items[index - 1].thread_done = True


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


# The selected storage item to be displayed
selected = 0


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

    def contextMenuEvent(self, event):
        self.menu = QMenu(self)
        if self.thread_done:
            refresh_action = QAction('Refresh', self)
            refresh_action.triggered.connect(lambda: self.queue_size_get())
            self.menu.addAction(refresh_action)
            self.menu.addSeparator()

        actions = list()
        i = 0
        for directory in self.directories_pretty:
            actions.append(QAction(str(directory), self))
            actions[i].triggered.connect(lambda: print(directory))
            self.menu.addAction(actions[i])
            i += 1

        self.menu.popup(QCursor.pos())

    def queue_size_get(self):
        self.usage = 0
        self.thread_done = False
        self.thread = threading.Thread(target=async_directory_usage, name=self.name,
                                       args=[self.directories, self.index])
        self.thread.start()

    def update(self):
        self.percent = self.usage / (usage * float(1000 ** 3))
        self.usage_label.setText(human_readable(self.usage))
        if self.thread_done:
            self.percent_label.setText("%.1f%%" % (self.percent * 100))
        else:
            self.percent_label.setText("Calculating...")
        super(StorageItem, self).update()

    def __init__(self, name, directories, directories_pretty, parent):
        super().__init__(parent)

        # Constants for rendering
        text_height = 20
        vmargin = 15
        hmargin = 40

        # Set variables from arguments
        self.directories = directories
        self.name = name
        self.directories_pretty = directories_pretty

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
        self.link_icon = QtSvg.QSvgWidget("src/link.svg", self)
        self.link_icon.setGeometry(geometry.width() - int(height / 2) - 8, int(height / 2) - 8, 16, 16)
        self.link_icon.setStyleSheet("background-color: rgba(0,0,0,0);")
        self.link_icon.show()

    def enterEvent(self, event):
        self.hover = True

    def leaveEvent(self, event):
        self.hover = False

    def mouseReleaseEvent(self, event):
        global selected
        if selected == self.index:
            selected = 0
        else:
            selected = self.index

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

    sel = 0

    def updateAll(self):
        if selected == 0:
            if self.sel > 0.001:
                self.sel = (self.sel * 9) / 10
            else:
                self.sel = 0
        else:
            self.sel = ((self.sel * 9) + storage_items[selected - 1].percent) / 10
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
        self.setMinimumSize(250, 400)
        self.show()

        # Create labels
        # Used space labels
        self.usage_label = QLabel("In use", self)
        self.usage_label.setStyleSheet("color: white;")
        self.usage_label.show()
        self.usage_value_label = QLabel("%.1f GB" % usage, self)
        self.usage_value_label.setStyleSheet("color: %s;" % light_grey.get_style())
        self.usage_value_label.show()

        # Free space labels
        self.free_label = QLabel("Available", self)
        self.free_label.setStyleSheet("color: white;")
        self.free_label.show()
        self.free_value_label = QLabel("%.1f GB" % free, self)
        self.free_value_label.setStyleSheet("color: %s;" % light_grey.get_style())
        self.free_value_label.show()

        # selected space labels
        self.sel_label = QLabel("", self)
        self.sel_label.setStyleSheet("color: white;")
        self.sel_value_label = QLabel("", self)
        self.sel_value_label.setStyleSheet("color: %s;" % light_grey.get_style())

        # Set the alignment
        self.usage_label.setAlignment(Qt.AlignCenter)
        self.usage_value_label.setAlignment(Qt.AlignCenter)
        self.free_label.setAlignment(Qt.AlignCenter)
        self.free_value_label.setAlignment(Qt.AlignCenter)
        self.sel_label.setAlignment(Qt.AlignCenter)
        self.sel_value_label.setAlignment(Qt.AlignCenter)

        # Update and animate everything
        label_timer = QTimer(self)
        label_timer.setInterval(10)
        label_timer.timeout.connect(self.updateAll)
        label_timer.start()

    def updateLabels(self):
        real_sel = 0
        if selected != 0:
            if not self.sel_label.isVisible():
                self.sel_label.show()
                self.sel_value_label.show()
            self.sel_label.setText(storage_items[selected - 1].name)
            self.sel_value_label.setText(human_readable(storage_items[selected - 1].usage))

            real_sel = storage_items[selected - 1].usage / float(1000 ** 3)

        elif self.sel_label.isVisible():
            self.sel_label.hide()
            self.sel_value_label.hide()

        self.usage_value_label.setText("%.1f GB" % (usage - real_sel))
        self.free_value_label.setText("%.1f GB" % free)

    def paintEvent(self, event):
        # Ensure our disk usage variables are up to date
        get_usage()
        self.updateLabels()

        # Get the bar dimensions
        bar_width = int(ratio * (self.frameGeometry().width() - 80))
        if self.sel != 0:
            sel_bar_width = int(self.sel * ratio * (self.frameGeometry().width() - 80))
        else:
            sel_bar_width = 0
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

        # Draw selected bar
        if self.sel != 0:
            if self.sel > 0.1 or selected != 0:
                painter.setPen(QPen(red.get_qcolor(), border, Qt.SolidLine))
            else:
                painter.setPen(QPen(red.get_qcolor(), border * self.sel * 10, Qt.SolidLine))
            painter.setBrush(QBrush(red.get_qcolor(), Qt.SolidPattern))
            painter.drawRect(margin, margin, sel_bar_width, bar_height)

        # Draw labels
        painter.setPen(QPen(grey.get_qcolor(), 2, Qt.SolidLine))

        # Used space
        label_a_x = margin + int((bar_width + sel_bar_width) / 2)
        painter.drawLine(label_a_x, line_offset - 1, label_a_x, line_offset + line_length)
        self.usage_label.setGeometry(label_a_x - 20, line_offset + line_length + 5, 40, 10)
        self.usage_value_label.setGeometry(label_a_x - 30, line_offset + line_length + 22, 60, 10)

        # Unused space
        label_b_x = margin + bar_width + int((self.frameGeometry().width() - (margin * 2) - bar_width) / 2)
        painter.drawLine(label_b_x, line_offset - 1, label_b_x, line_offset + line_length)
        self.free_label.setGeometry(label_b_x - 30, line_offset + line_length + 5, 60, 10)
        self.free_value_label.setGeometry(label_b_x - 30, line_offset + line_length + 22, 60, 10)

        # Selected space
        if selected != 0:
            label_c_x = margin + int(sel_bar_width / 2)
            painter.drawLine(label_c_x, line_offset - 1, label_c_x, line_offset + line_length)
            self.sel_label.setGeometry(label_c_x - 50, line_offset + line_length, 100, 20)
            self.sel_value_label.setGeometry(label_c_x - 30, line_offset + line_length + 22, 60, 10)


window = Window()
storage_items = [
    StorageItem("System", sys_dirs, [root], window),
    StorageItem("Applications", app_dirs, app_dirs, window),
    StorageItem("Temp files", temp_dirs, temp_dirs, window),
    StorageItem("My files", user_dirs, [home], window)
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

end_code = App.exec()

for item in storage_items:
    item.thread_done = True
    item.thread.join()

sys.exit(end_code)
