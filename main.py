import time
from pathlib import Path
import tempfile
from PySide6.QtWidgets import *
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from src.ui import UI
import sys
import os
import ctypes
# Уникальный идентификатор для Windows
myappid = 'mycompany.myproduct.subproduct.version'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

if "NUITKA_ONEFILE_PARENT" in os.environ:
    splash_filename = os.path.join(
        tempfile.gettempdir(),
        "onefile_%d_splash_feedback.tmp" % int(
            os.environ["NUITKA_ONEFILE_PARENT"]),
    )
    print("splash filename: ", splash_filename)
    if os.path.exists(splash_filename):
        os.unlink(splash_filename)
print("Splash Screen has been removed")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    parent_dir = Path(__file__).parent
    icon_path = os.path.join(parent_dir, "assets",  "images", "logos.ico")
    print(icon_path)
    app.setWindowIcon(QIcon(icon_path))
    window = UI()
    window.show()

    sys.exit(app.exec())
