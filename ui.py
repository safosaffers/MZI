"""
Данный файл описывает пользовательский интерфес приложения:
Выбор файлов для анализа и вывод результатов
используя таблицы и рисунки(гистограммы).
"""


from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import pyqtgraph as pg
from static_analyzer import StaticAnalyzer  # import backend


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

        # Кнопки переключения окон (этапов)
        button_layout = QHBoxLayout()
        self.table_button = QPushButton("Статический анализатор")
        self.analyze_result = QPushButton("Результаты анализа")
        self.analyze_result.setEnabled(False)

        button_layout.addWidget(self.table_button)
        button_layout.addWidget(self.analyze_result)
        layout.addLayout(button_layout)

        # Стек для переключения между этапами
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        self.create_load_files_page()

        # # Создание страниц
        # self.create_table_page()
        # self.create_histogram_page()

        # Подключение кнопок к переключению страниц
        self.table_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(0))
        self.analyze_result.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(1))

        # Показываем окно
        self.show()

    def create_load_files_page(self):

        # Контейнер для кнопок и текстовых полей
        combined_container = QWidget()
        combined_layout = QVBoxLayout()  # Вертикальный макет для кнопок и текстовых полей

        # Кнопки для открытия файлов
        button_layout = QHBoxLayout()
        self.button_open_file1 = QPushButton("Загрузить файл")
        self.button_open_file2 = QPushButton("Загрузить файл")
        button_layout.addWidget(self.button_open_file1)
        button_layout.addWidget(self.button_open_file2)
        self.button_open_file1.clicked.connect(lambda: self.open_text_file(1))
        self.button_open_file2.clicked.connect(lambda: self.open_text_file(2))

        # Добавляем кнопки в общий макет
        combined_layout.addLayout(button_layout)

        # Тексты анализируемых файлов
        texts_layout = QHBoxLayout()
        self.text_edit1 = QTextEdit()
        self.text_edit1.setReadOnly(True)
        self.text_edit2 = QTextEdit()
        self.text_edit2.setReadOnly(True)
        texts_layout.addWidget(self.text_edit1)
        texts_layout.addWidget(self.text_edit2)

        # Добавляем текстовые поля в общий макет
        combined_layout.addLayout(texts_layout)

        self.button_analyze = QPushButton("Начать анализ")
        self.button_analyze.clicked.connect(self.start_analyze)
        combined_layout.addWidget(self.button_analyze)

        # Устанавливаем общий макет в контейнер
        combined_container.setLayout(combined_layout)

        # Добавляем контейнер в стек
        self.stacked_widget.addWidget(combined_container)

    # Открытие текстовых файлов и отображение их содержимого

    def open_text_file(self, file_num):
        sa = self.sa1 if file_num == 1 else self.sa2
        text_edit = self.text_edit1 if file_num == 1 else self.text_edit2
        button = self.button_open_file1 if file_num == 1 else self.button_open_file2

        # Если файл уже открыт, очищаем данные
        if sa.file_path:
            sa.clear_text_data()
            text_edit.setText("")
            button.setText("Открыть файл")
            return

        # Открываем диалог выбора файла
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Text File", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            sa.file_path = file_path
            self.show_fileQTextEdit(file_path, file_num)
            button.setText("Очистить файл")

    # Отображение содержимого файла
    def show_fileQTextEdit(self, file_path, QTextEdit_num):
        target_edit = self.text_edit1 if QTextEdit_num == 1 else self.text_edit2
        other_edit = self.text_edit2 if QTextEdit_num == 1 else self.text_edit1
        target_sa = self.sa1 if QTextEdit_num == 1 else self.sa2
        other_sa = self.sa2 if QTextEdit_num == 1 else self.sa1

        # Загружаем текст
        trimmed_to_max_len = target_sa.process_text_forms(
            file_path,  other_sa.text_len)
        # Отображаем его
        target_edit.setText(''.join(target_sa.text_in_alphabet))

        # Если текст был укорочен, сообщаем об этом
        if trimmed_to_max_len:
            self.show_msg_box_text_was_stripped(QTextEdit_num)

        if target_sa.text_len < other_sa.text_len:
            other_sa.text_in_alphabet = other_sa.text_in_alphabet[:target_sa.text_len]
            other_edit.setText(''.join(other_sa.text_in_alphabet))
            self.show_msg_box_text_was_stripped(2 if QTextEdit_num == 1 else 1)

    def show_msg_box_text_was_stripped(self, num):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Предупреждение")
        msg.setText(
            f"Текст {'A' if num == 1 else 'B'} был урезан для соответствия длине текста {'B' if num == 1 else 'A'}.")
        msg.exec_()

    def show_msg_box_file_not_chosen(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Ошибка")
        msg.setText("Пожалуйста, выберите все файлы для анализа")
        msg.exec_()

    def start_analyze(self):
        # Удаляем старые результаты анализа, если
        widget = self.stacked_widget.widget(1)
        if widget:
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
        if self.sa1.file_path == "" or self.sa2.file_path == "":
            self.show_msg_box_file_not_chosen()
            return
        self.analyze_result.setEnabled(True)
        self.sa1.single_text_analyze()
        self.sa2.single_text_analyze()
        # Контейнер для статистики
        stats_container = QWidget()
        stats_layout = QGridLayout()  # Табличный макет

        # Добавляем заголовки и значения в макет
        # Строка 0, столбец 0
        stats_layout.addWidget(QLabel("Энтропия A:"), 0, 0)
        # Строка 0, столбец 1
        stats_layout.addWidget(QLabel(f"{self.sa1.entropy:.4f}"), 0, 1)

        # Строка 0, столбец 2
        stats_layout.addWidget(QLabel("Энтропия B:"), 0, 2)
        # Строка 0, столбец 3
        stats_layout.addWidget(QLabel(f"{self.sa2.entropy:.4f}"), 0, 3)

        # Строка 1, столбец 0
        stats_layout.addWidget(QLabel("Марковская энтропия H(A|A):"), 1, 0)
        # Строка 1, столбец 1
        stats_layout.addWidget(
            QLabel(f"{self.sa1.markov_entropy:.4f}"), 1, 1)

        # Строка 1, столбец 2
        stats_layout.addWidget(QLabel("Марковская энтропия H(B|B):"), 1, 2)
        # Строка 1, столбец 3
        stats_layout.addWidget(
            QLabel(f"{self.sa2.markov_entropy:.4f}"), 1, 3)

        # Строка 2, столбец 0
        stats_layout.addWidget(QLabel("Марковская энтропия H(A|B):"), 2, 0)
        # Строка 2, столбец 1
        stats_layout.addWidget(
            QLabel(f"{self.sa1.markov_entropy_with(self.sa2):.4f}"), 2, 1)

        # Строка 2, столбец 2
        stats_layout.addWidget(QLabel("Марковская энтропия H(B|A):"), 2, 2)
        # Строка 2, столбец 3
        stats_layout.addWidget(
            QLabel(f"{self.sa2.markov_entropy_with(self.sa1):.4f}"), 2, 3)

        # Строка 3, столбец 0
        stats_layout.addWidget(QLabel("Совместная энтропия H(A,B):"), 3, 0)
        # Строка 3, столбец 1
        stats_layout.addWidget(
            QLabel(f"{self.sa1.joint_entropy_with(self.sa2):.4f}"), 3, 1)

        # Строка 3, столбец 2
        stats_layout.addWidget(QLabel("Совместная энтропия H(B,A):"), 3, 2)
        # Строка 3, столбец 3
        stats_layout.addWidget(
            QLabel(f"{self.sa2.joint_entropy_with(self.sa1):.4f}"), 3, 3)

        # Устанавливаем макет в контейнер
        stats_container.setLayout(stats_layout)

        # Добавляем контейнер в стек
        self.stacked_widget.addWidget(stats_container)

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
