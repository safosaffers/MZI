
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from src.ui import UI
import sys
if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = UI()
    window.show()

    sys.exit(app.exec())
