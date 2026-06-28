import sys, os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui import RoboGUI, resource_path


def main():
    app = QApplication(sys.argv)

    icon_path = resource_path("..\\icon\\robogui.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = RoboGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
