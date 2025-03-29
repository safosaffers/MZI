from PySide6.QtWidgets import *
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from src.ui import UI
import sys
import os
import ctypes

# Функция для получения пути к ресурсам


def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Уникальный идентификатор для Windows
myappid = u'mycompany.myproduct.subproduct.version'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(
        QIcon(resource_path(os.path.join("src", "images", "logo_white.ico"))))

    window = UI()
    window.show()

    sys.exit(app.exec())
