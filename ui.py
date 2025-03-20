"""
Данный файл описывает пользовательский интерфес приложения:
Выбор файлов для анализа и вывод результатов
используя таблицы и рисунки(гистограммы).
"""


from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import pyqtgraph as pg
from static_analyzer import StaticAnalyzer  # import backend


class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sa1 = StaticAnalyzer()  # Для первого текста
        self.sa2 = StaticAnalyzer()  # Для второго текста
        self.setWindowTitle("Анализатор текста")
        self.setGeometry(100, 100, 900, 700)
        self.show()

        # Центральный виджет
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Кнопки переключения окон (этапов)
        button_layout = QHBoxLayout()
        self.table_button = QPushButton("Выбор файлов для анализа")
        self.analyze_result = QPushButton("Результаты анализа")
        self.analyze_result.setEnabled(False)

        button_layout.addWidget(self.table_button)
        button_layout.addWidget(self.analyze_result)
        layout.addLayout(button_layout)

        # Стек для переключения между этапами
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Страница выбора файлов для анализа
        self.selecting_files_for_analysis_page()

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

    def selecting_files_for_analysis_page(self):

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

        # Выбор алфавита
        self.lbl_analyze_alphabet = QLabel("Выберите используемый алфавит:")
        combined_layout.addWidget(self.lbl_analyze_alphabet)

        # Создаем контейнер для радиокнопок
        radiobuttons_layout = QHBoxLayout()
        # Группа для управления радиокнопками
        self.radio_group = QButtonGroup(self)

        # Список алфавитов с их метками и значениями
        alphabets = [
            ("Русский", "rus_34"),
            ("Русский без 'ё' и '_'", "rus_32"),
            ("Латиница", "lat_27"),
            ("Латиница без 'j' и ' '", "lat_25")
        ]

        # Создаем радиокнопки
        for idx, (label, value) in enumerate(alphabets):
            radio = QRadioButton(label)
            radio.setChecked(idx == 0)  # Первая кнопка активна по умолчанию
            radio.alphabet = value  # Добавляем пользовательский атрибут
            radiobuttons_layout.addWidget(radio)
            self.radio_group.addButton(radio)  # Добавляем в группу
            setattr(self, f"radio_{value}", radio)  # Сохраняем в self

        # Подключаем сигналы (если нужно)
        self.radio_group.buttonClicked.connect(self.rb_handle_alphabet_change)

        # Добавляем макет с радиокнопками
        combined_layout.addLayout(radiobuttons_layout)
        # Кнопка анализа
        self.button_analyze = QPushButton("Начать анализ")
        self.button_analyze.clicked.connect(self.start_analyze)
        combined_layout.addWidget(self.button_analyze)

        # Устанавливаем общий макет в контейнер
        combined_container.setLayout(combined_layout)

        # Добавляем контейнер в стек
        self.stacked_widget.addWidget(combined_container)

    # Открытие текстовых файлов и отображение их содержимого
    def rb_handle_alphabet_change(self):
        new_alphabet = self.radio_group.checkedButton().alphabet
        if (self.sa1.alphabet_name != new_alphabet or self.sa2.alphabet_name != new_alphabet):
            old_file_path_1 = self.sa1.file_path
            old_file_path_2 = self.sa2.file_path
            self.sa1.clear_text_data()
            self.sa2.clear_text_data()
            self.sa1.set_alphabet(self.radio_group.checkedButton().alphabet)
            self.sa2.set_alphabet(self.radio_group.checkedButton().alphabet)
            self.show_fileQTextEdit(old_file_path_1, 1)
            self.show_fileQTextEdit(old_file_path_2, 2)

    def open_text_file(self, file_num):
        sa = self.sa1 if file_num == 1 else self.sa2
        text_edit = self.text_edit1 if file_num == 1 else self.text_edit2
        button = self.button_open_file1 if file_num == 1 else self.button_open_file2

        # Если файл уже открыт, очищаем данные
        if sa.file_path:
            sa.clear_text_data()
            text_edit.setText("")
            button.setText("Открыть файл")
        else:
            # Открываем диалог выбора файла
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Text File", "", "Text Files (*.txt);;All Files (*)")
            if file_path:
                sa.file_path = file_path
                self.show_fileQTextEdit(file_path, file_num)
                button.setText("Очистить файл")

    # Отображение содержимого файла
    def show_fileQTextEdit(self, file_path, QTextEdit_num):
        if file_path == "":
            return
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
            self.show_msg_box_text_was_trimmed(QTextEdit_num)
        elif other_sa.text_len > target_sa.text_len:
            other_sa.text_in_alphabet = other_sa.text_in_alphabet[:target_sa.text_len]
            other_edit.setText(''.join(other_sa.text_in_alphabet))
            self.show_msg_box_text_was_trimmed(2 if QTextEdit_num == 1 else 1)

    def show_msg_box_text_was_trimmed(self, num=-1):
        if num == -1:
            return
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
        msg.setText("Пожалуйста, выберите файл(ы) для анализа")
        msg.exec_()

    def start_analyze(self):
        # Выполняем анализ
        self.sa1.single_text_analyze()
        self.sa2.single_text_analyze()

        # Страница выбора файлов для анализа
        self.analyze_results_page()

    def analyze_results_page(self):
        # Удаляем старые результаты анализа, если он производился
        widget = self.stacked_widget.widget(1)
        if widget:
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
        if self.sa1.file_path == "" and self.sa2.file_path == "":
            self.show_msg_box_file_not_chosen()
            return
        self.analyze_result.setEnabled(True)

        main_analyze_container = QWidget()
        main_analyze_layout = QVBoxLayout()
        main_analyze_container.setLayout(main_analyze_layout)

        # Добавляем кнопки переключения
        btns_container = QWidget()
        button_layout = QHBoxLayout()
        btns_container.setLayout(button_layout)
        btn1 = QPushButton("Энтропии")
        btn2 = QPushButton("Таблицы вероятностей")
        btn3 = QPushButton("Гистограммы частот")
        btn1.clicked.connect(lambda: self.stats_container.setCurrentIndex(0))
        btn2.clicked.connect(lambda: self.stats_container.setCurrentIndex(1))
        btn3.clicked.connect(lambda: self.stats_container.setCurrentIndex(2))
        button_layout.addWidget(btn1)
        button_layout.addWidget(btn2)
        button_layout.addWidget(btn3)
        main_analyze_layout.addWidget(btns_container)

        # Контейнер для статистики
        self.stats_container = QStackedWidget()

        # 1-я страница для контейнера статистики
        # – Информация о вычисленной энтропии:
        self.stats_container.addWidget(self.entropy_info_widget())
        # 2-я – Информация о вероятностях в текстах:
        self.stats_container.addWidget(self.probabilities_tables_page())
        # 3-я – Гистограмма частот символов текстов:
        self.stats_container.addWidget(self.histograms_page())
        # Добавляем контейнер в стек
        main_analyze_layout.addWidget(self.stats_container)

        self.stacked_widget.addWidget(main_analyze_container)

    def entropy_info_widget(self):
        container = QWidget()
        stats_layout = QGridLayout()  # Табличный макет
        container.setLayout(stats_layout)
        # Добавляем заголовки и значения в макет
        if self.sa1.file_path != "":
            stats_layout.addWidget(QLabel("Энтропия A:"), 0, 0)
            stats_layout.addWidget(QLabel(f"{self.sa1.entropy:.4f}"), 0, 1)

            stats_layout.addWidget(QLabel("Марковская энтропия H(A|A):"), 1, 0)
            stats_layout.addWidget(
                QLabel(f"{self.sa1.markov_entropy:.4f}"), 1, 1)
        if self.sa2.file_path != "":
            stats_layout.addWidget(QLabel("Энтропия B:"), 0, 2)
            stats_layout.addWidget(QLabel(f"{self.sa2.entropy:.4f}"), 0, 3)

            stats_layout.addWidget(QLabel("Марковская энтропия H(B|B):"), 1, 2)
            stats_layout.addWidget(
                QLabel(f"{self.sa2.markov_entropy:.4f}"), 1, 3)
        if self.sa2.file_path != "" and self.sa1.file_path != "":
            stats_layout.addWidget(QLabel("Марковская энтропия H(A|B):"), 2, 0)
            stats_layout.addWidget(
                QLabel(f"{self.sa1.markov_entropy_with(self.sa2):.4f}"), 2, 1)

            stats_layout.addWidget(QLabel("Марковская энтропия H(B|A):"), 2, 2)
            stats_layout.addWidget(
                QLabel(f"{self.sa2.markov_entropy_with(self.sa1):.4f}"), 2, 3)

            stats_layout.addWidget(QLabel("Совместная энтропия H(A,B):"), 3, 0)
            stats_layout.addWidget(
                QLabel(f"{self.sa1.joint_entropy_with(self.sa2):.4f}"), 3, 1)

            stats_layout.addWidget(QLabel("Совместная энтропия H(B,A):"), 3, 2)
            stats_layout.addWidget(
                QLabel(f"{self.sa2.joint_entropy_with(self.sa1):.4f}"), 3, 3)
        return container

    def probabilities_tables_page(self):
        # Создаем стек для таблиц
        stacked_widget = QStackedWidget()

        # Первая страница (Таблицы для A)
        page1 = QWidget()
        layout1 = QVBoxLayout()
        layout1.addWidget(QLabel("Таблицы для текста A"))
        self.add_tables_to_layout(layout1, self.sa1)
        page1.setLayout(layout1)

        # Вторая страница (Таблицы для B)
        page2 = QWidget()
        layout2 = QVBoxLayout()
        layout2.addWidget(QLabel("Таблицы для текста B"))
        self.add_tables_to_layout(layout2, self.sa2)
        page2.setLayout(layout2)

        # Добавляем страницы в стек
        stacked_widget.addWidget(page1)
        stacked_widget.addWidget(page2)

        # Добавляем кнопки переключения
        button_layout = QHBoxLayout()
        btn1 = QPushButton("Таблицы A")
        btn2 = QPushButton("Таблицы B")
        btn1.clicked.connect(lambda: stacked_widget.setCurrentIndex(0))
        btn2.clicked.connect(lambda: stacked_widget.setCurrentIndex(1))
        button_layout.addWidget(btn1)
        button_layout.addWidget(btn2)

        # Общий контейнер
        container = QWidget()
        layout = QVBoxLayout()
        layout.addLayout(button_layout)
        layout.addWidget(stacked_widget)
        container.setLayout(layout)

        return container

    def add_tables_to_layout(self, layout, sa):
        # Функция для создания таблицы
        def create_table(data, title, alphabet=None, max_row_elems=9, max_col_elems=9):
            alp_len = len(alphabet)
            row_parts_count = (alp_len+max_row_elems-1)//max_row_elems
            col_parts_count = (alp_len+max_col_elems-1)//max_col_elems
            table_part = [[QTableWidget() for i in range(col_parts_count)]
                          for j in range(row_parts_count)]
            for i in range(row_parts_count):
                for j in range(col_parts_count):
                    table_part[i][j].setRowCount(max_row_elems)
                    table_part[i][j].setColumnCount(max_col_elems)
                    table_part[i][j].verticalHeader().setDefaultSectionSize(30)
                    table_part[i][j].horizontalHeader(
                    ).setDefaultSectionSize(30)
                    k_begin = i*max_row_elems
                    k_end = (i*max_row_elems+max_row_elems)
                    k_end = k_end if k_end <= alp_len else alp_len
                    l_begin = j*max_col_elems
                    l_end = (j*max_col_elems+max_col_elems)
                    l_end = l_end if l_end < alp_len else alp_len
                    for k in range(k_begin, k_end):
                        for l in range(l_begin, l_end):
                            elem = QTableWidgetItem(str(round(data[k][l], 3)))
                            table_part[i][j].setItem(
                                k-k_begin, l-l_begin, elem)
                    table_part[i][j].setHorizontalHeaderLabels(
                        list(alphabet[l_begin:l_end]))
                    table_part[i][j].setVerticalHeaderLabels(
                        list(alphabet[k_begin:k_end]))

            layout.addWidget(table_part[0][1])

            btns_container = QWidget()
            btns_layout = QGridLayout()
            btns_layout.setHorizontalSpacing(5)
            btns_container.setLayout(btns_layout)
            btn_left = QPushButton("←")
            btn_left.setFixedSize(40, 40)
            btn_right = QPushButton("→")
            btn_right.setFixedSize(40, 40)
            btn_up = QPushButton("↑")
            btn_up.setFixedSize(40, 40)
            btn_down = QPushButton("↓")
            btn_down.setFixedSize(40, 40)
            btns_layout.addWidget(btn_left, 0, 0, alignment=Qt.AlignRight)
            btns_layout.addWidget(btn_right, 0, 1, alignment=Qt.AlignLeft)
            btns_layout.addWidget(btn_up, 1, 0, alignment=Qt.AlignRight)
            btns_layout.addWidget(btn_down, 1, 1, alignment=Qt.AlignLeft)
            layout.addWidget(btns_container)

        sa.alphabet
        # Добавляем таблицы с использованием алфавита
        new_alphabet = "Ø" + sa.alphabet[:-1]+"_"
        # create_table(sa.probabilities,
        #              "Безусловные вероятности: P(a_i)", new_alphabet)
        # create_table(sa.joint_probabilities,
        #              "Совместные вероятности: P(a_{i}|a_{i+1})", new_alphabet)
        create_table(sa.condi_probabilities,
                     "Условные вероятности: P(a_{i}|a_{i-1})", new_alphabet)

    def histograms_page(self):
        # Создаем стек для гистограмм
        stacked_widget = QStackedWidget()

        # Первая страница (Гистограмма A)
        page1 = QWidget()
        layout1 = QVBoxLayout()
        layout1.addWidget(
            QLabel("Гистограмма встречаемости символов текста A"))
        layout1.addWidget(self.create_histogram(self.sa1))
        page1.setLayout(layout1)

        # Вторая страница (Гистограмма B)
        page2 = QWidget()
        layout2 = QVBoxLayout()
        layout2.addWidget(
            QLabel("Гистограмма встречаемости символов текста B"))
        layout2.addWidget(self.create_histogram(self.sa2))
        page2.setLayout(layout2)

        # Добавляем страницы в стек
        stacked_widget.addWidget(page1)
        stacked_widget.addWidget(page2)

        # Добавляем кнопки переключения
        button_layout = QHBoxLayout()
        btn1 = QPushButton("Гистограмма A")
        btn2 = QPushButton("Гистограмма B")
        btn1.clicked.connect(lambda: stacked_widget.setCurrentIndex(0))
        btn2.clicked.connect(lambda: stacked_widget.setCurrentIndex(1))
        button_layout.addWidget(btn1)
        button_layout.addWidget(btn2)

        # Общий контейнер
        container = QWidget()
        layout = QVBoxLayout()
        layout.addLayout(button_layout)
        layout.addWidget(stacked_widget)
        container.setLayout(layout)

        return container

    def create_histogram(self, current_sa):
        histogram_widget = pg.GraphicsLayoutWidget()
        histogram_widget.setBackground(QColor(33, 46, 74))

        alphabet_list = list(current_sa.alphabet)
        new_alphabet = alphabet_list[:-1] + ["'_'"]
        xdict = dict(enumerate(new_alphabet))
        stringaxis = pg.AxisItem(orientation='bottom')
        stringaxis.setTicks([xdict.items()])

        plt1 = histogram_widget.addPlot(axisItems={'bottom': stringaxis})
        plt1.setLimits(
            xMin=-2, xMax=current_sa.alphabet_len - 1, minXRange=7, maxXRange=100,
            yMin=0, yMax=max(current_sa.frequencies[1:]) + 1, minYRange=100, maxYRange=100
        )

        hist = pg.BarGraphItem(
            x=range(current_sa.alphabet_len - 1), height=current_sa.frequencies[1:], width=0.8,
            pen=QColor(33, 46, 74), brush=QColor(198, 104, 51)
        )
        plt1.addItem(hist)

        return histogram_widget
