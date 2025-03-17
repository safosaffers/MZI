from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import pyqtgraph as pg


class UIMixin:
    def show_main_window(self):
        # Главное окно
        self.window = QMainWindow()
        self.window.setWindowTitle("Анализатор текста")
        self.window.setGeometry(100, 100, 800, 600)
        self.window.show()

        # Центральный виджет
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.window.setCentralWidget(central_widget)

        # Кнопки переключения
        button_layout = QHBoxLayout()
        self.table_button = QPushButton("Показать таблицу")
        self.histogram_button = QPushButton("Показать гистограмму")
        button_layout.addWidget(self.table_button)
        button_layout.addWidget(self.histogram_button)
        layout.addLayout(button_layout)

        # Стек для переключения между таблицей и гистограммой
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Создание страниц
        self.create_table_page()
        self.create_histogram_page()

        # Подключение кнопок к переключению страниц
        self.table_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(0))
        self.histogram_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(1))

        # Показываем окно
        self.window.show()

    def create_table_page(self):
        # Виджет для таблиц
        table_widget = QWidget()
        table_layout = QVBoxLayout()
        table_widget.setLayout(table_layout)

        # Функция для создания таблицы
        def create_table(data, title):
            table = QTableWidget()
            table.setWindowTitle(title)
            table.setRowCount(len(data))
            table.setColumnCount(
                len(data[0]) if isinstance(data[0], list) else 1)

            for i in range(len(data)):
                if isinstance(data[0], list):  # Для матриц
                    for j in range(len(data[0])):
                        table.setItem(i, j, QTableWidgetItem(
                            str(round(data[i][j], 6))))
                else:  # Для одномерных массивов
                    table.setItem(i, 0, QTableWidgetItem(
                        str(round(data[i], 6))))

            label = QLabel(title)
            table_layout.addWidget(label)
            table_layout.addWidget(table)

        # Добавляем таблицы
        create_table(self.probabilities, "Безусловные вероятности")
        create_table(self.joint_probabilities, "Совместные вероятности")
        create_table(self.condi_probabilities, "Условные вероятности")

        # Добавляем виджет таблиц в стек
        self.stacked_widget.addWidget(table_widget)

    def create_histogram_page(self):
        # Виджет для гистограммы
        histogram_widget = pg.GraphicsLayoutWidget()
        histogram_widget.setBackground(QColor(33, 46, 74))

        alphabet_list = list(self.alphabet)
        new_alphabet = alphabet_list[:-1] + ["'_'"]
        xdict = dict(enumerate(new_alphabet))
        stringaxis = pg.AxisItem(orientation='bottom')
        stringaxis.setTicks([xdict.items()])

        plt1 = histogram_widget.addPlot(axisItems={'bottom': stringaxis})
        plt1.setLimits(xMin=-2, xMax=self.alphabet_len - 1, minXRange=7, maxXRange=100,
                       yMin=0, yMax=max(self.frequencies[1:]) + 1, minYRange=100, maxYRange=100)

        hist = pg.BarGraphItem(x=range(self.alphabet_len - 1), height=self.frequencies[1:], width=0.8,
                               pen=QColor(33, 46, 74), brush=QColor(198, 104, 51))
        plt1.addItem(hist)

        # Добавляем виджет гистограммы в стек
        self.stacked_widget.addWidget(histogram_widget)
