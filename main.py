from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
from ui import UI
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UI()
    sys.exit(app.exec_())
