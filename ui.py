"""
Данный файл описывает пользовательский интерфес приложения:
Выбор файлов для анализа и вывод результатов
используя таблицы и рисунки(гистограммы).
"""


from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import pyqtgraph as pg
from static_analyzer import StaticAnalyzer


class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sa1 = StaticAnalyzer()  # Для первого текста
        self.sa2 = StaticAnalyzer()  # Для второго текста
        self.setWindowTitle("Анализатор текста")
        self.setGeometry(100, 100, 800, 600)
        self.show()

        # Центральный виджет
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Кнопки для открытия файлов
        button_layout = QHBoxLayout()
        # self.label = QLabel("Выберите файлы для анализа:")
        # layout.addWidget(self.label)
        self.open_file1 = QPushButton("Открыть файл")
        self.open_file2 = QPushButton("Открыть файл")
        button_layout.addWidget(self.open_file1)
        button_layout.addWidget(self.open_file2)
        layout.addLayout(button_layout)
        self.open_file1.clicked.connect(lambda: self.open_text_file(1))
        self.open_file2.clicked.connect(lambda: self.open_text_file(2))

        # Тексты анализируемых файлов
        texts_layout = QHBoxLayout()
        self.text_edit1 = QTextEdit()
        self.text_edit2 = QTextEdit()
        texts_layout.addWidget(self.text_edit1)
        texts_layout.addWidget(self.text_edit2)
        layout.addLayout(texts_layout)

        # # Кнопки переключения
        # button_layout = QHBoxLayout()
        # self.table_button = QPushButton("Показать таблицу")
        # self.histogram_button = QPushButton("Показать гистограмму")
        # button_layout.addWidget(self.table_button)
        # button_layout.addWidget(self.histogram_button)
        # layout.addLayout(button_layout)

        # # Стек для переключения между таблицей и гистограммой
        # self.stacked_widget = QStackedWidget()
        # layout.addWidget(self.stacked_widget)

        # # Создание страниц
        # self.create_table_page()
        # self.create_histogram_page()

        # # Подключение кнопок к переключению страниц
        # self.table_button.clicked.connect(
        #     lambda: self.stacked_widget.setCurrentIndex(0))
        # self.histogram_button.clicked.connect(
        #     lambda: self.stacked_widget.setCurrentIndex(1))

        # Показываем окно
        self.show()

    def open_text_file(self, file_num):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Text File", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            if file_num == 1:
                self.sa1.filename = file_path
                self.show_fileQTextEdit(file_path, 1)
            else:
                self.sa2.filename = file_path
                self.show_fileQTextEdit(file_path, 2)

    def show_fileQTextEdit(self, file_path, QTextEdit_num):
        with open(file_path, 'r', encoding='utf-8') as f:
            if QTextEdit_num == 1:
                self.text_edit1.append(f.read())
            else:
                self.text_edit2.append(f.read())

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
        create_table(self.sa.probabilities, "Безусловные вероятности")
        create_table(self.sa.joint_probabilities, "Совместные вероятности")
        create_table(self.sa.condi_probabilities, "Условные вероятности")

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
