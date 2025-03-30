import tempfile
from PySide6.QtWidgets import *
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from src.ui import UI
import sys
import os
import ctypes

from pathlib import Path
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

# Уникальный идентификатор для Windows
myappid = u'mycompany.myproduct.subproduct.version'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    parent_dir = Path(__file__).parent
    app.setWindowIcon(
        QIcon( os.path.join(parent_dir, "assets",  "images", "logos.ico")))

    window = UI()
    window.show()

    sys.exit(app.exec())
