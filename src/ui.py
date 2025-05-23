"""
Данный файл описывает пользовательский интерфес приложения:
Выбор файлов для анализа и вывод результатов
используя таблицы и рисунки(гистограммы).
"""

# Подключение стилей
from PySide6.QtGui import QFont, QTextCharFormat, Qt
from PySide6.QtCore import QEasingCurve
from Custom_Widgets.QCustomModals import QCustomModals
from Custom_Widgets.QCustomCheckBox import QCustomCheckBox
# Подключение основной библиотеки анализатора
from .static_analyzer import StaticAnalyzer
import pyqtgraph as pg
import pyqtgraph.exporters as export
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtMultimedia import QSoundEffect, QMediaDevices
from PySide6.QtGui import QFont, QTextCharFormat, Qt
from datetime import datetime
import xlsxwriter
import os
from pathlib import Path


class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sa1 = StaticAnalyzer()  # Для первого текста
        self.sa2 = StaticAnalyzer()  # Для второго текста
        self.setWindowTitle(
            "Статический анализатор текста. Каримов Сафо, 1311")
        self.setGeometry(100, 100, 990, 700)
        self.centerOnScreen()

        # Центральный виджет
        self.central_widget = QWidget()
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)
        self.setCentralWidget(self.central_widget)

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

        # Подключение кнопок к переключению страниц
        self.table_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(0))
        self.analyze_result.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(1))

        # Делаем шрифт больше
        font = self.font()  # Получаем текущий шрифт приложения
        font.setPointSize(13)  # Устанавливаем размер шрифта
        self.setFont(font)

    def centerOnScreen(self):
        # Получаем геометрию основного экрана
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        # Размеры окна
        window_size = self.size()
        width = window_size.width()
        height = window_size.height()

        # Вычисляем центральные координаты
        x = (screen_geometry.width() - width) // 2
        y = (screen_geometry.height() - height) // 2 - \
            50  # Смещение на 50 пикселей вверх

        # Перемещаем окно
        self.move(x, y)

        # Фиксируем размер окна
        self.setFixedSize(window_size.width(), window_size.height())

    def QLabelWithFont(self, text, fontsize):
        label = QLabel(text)
        font = QFont()
        font.setPointSize(fontsize)
        label.setFont(font)
        return label


    def QTextEdit_with_fixed_style(self, text_edit):
        text_edit.setTextBackgroundColor(Qt.white)
        text_edit.setTextColor(Qt.black)

        format = QTextCharFormat()
        format.setFont(QFont("Times New Roman", 14))
        text_edit.setCurrentCharFormat(format)
        text_edit.setAcceptRichText(False)  # Отключить вставку с форматированием

        self.text_edit1.setAcceptRichText(False)  # Отключить вставку с форматированием
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
        self.QTextEdit_with_fixed_style(self.text_edit1)
        self.text_edit1.setPlaceholderText(
            "Введите текст здесь или загрузите его из файла...")
        
        self.text_edit2 = QTextEdit()
        self.QTextEdit_with_fixed_style(self.text_edit2)

        self.text_edit2.setPlaceholderText(
            "Введите текст здесь или загрузите его из файла...")
        self.text_edit1.textChanged.connect(
            lambda: (self.button_open_file1.setText("Очистить файл") if self.text_edit1.toPlainText() else self.button_open_file1.setText("Загрузить файл")))
        self.text_edit2.textChanged.connect(
            lambda: (self.button_open_file2.setText("Очистить файл") if self.text_edit2.toPlainText() else self.button_open_file2.setText("Загрузить файл")))
        texts_layout.addWidget(self.text_edit1)
        texts_layout.addWidget(self.text_edit2)

        # Добавляем текстовые поля в общий макет
        combined_layout.addLayout(texts_layout)

        # Выбор алфавита
        self.lbl_analyze_alphabet = self.QLabelWithFont(
            "Выберите используемый алфавит:", 14)
        combined_layout.addWidget(
            self.lbl_analyze_alphabet)

        # Создаем контейнер для радиокнопок
        radiobuttons_layout = QHBoxLayout()
        # Группа для управления радиокнопками
        self.radio_group = QButtonGroup(self)

        # Список алфавитов с их метками и значениями
        alphabets = [
            ("Русский", "rus_34"),
            ("Русский без 'ё' и '_'", "rus_32"),
            ("Латиница", "lat_27"),
            ("Латиница без 'j' и '_'", "lat_25")
        ]

        # Создаем радиокнопки
        for idx, (label, value) in enumerate(alphabets):
            radio = QRadioButton(label)
            radio.setStyleSheet("font-size: 20px;")
            radio.setChecked(idx == 0)  # Первая кнопка активна по умолчанию
            radio.alphabet = value  # Добавляем пользовательский атрибут
            radiobuttons_layout.addWidget(radio)
            self.radio_group.addButton(radio)  # Добавляем в группу
            setattr(self, f"radio_{value}", radio)  # Сохраняем в self

        # Подключаем сигналы (если нужно)
        self.radio_group.buttonClicked.connect(self.rb_handle_alphabet_change)

        # Добавляем макет с радиокнопками
        combined_layout.addLayout(radiobuttons_layout)

        # Задание точности округлений результатов анализа
        set_precision_layout = QHBoxLayout()
        set_precision_layout.setContentsMargins(0, 0, 0, 0)
        set_precision_layout.setSpacing(0)
        label_left = self.QLabelWithFont(
            "Округлять результаты до ", 14)
        set_precision_layout.addWidget(label_left)
        self.cb_set_precision = QComboBox()
        self.cb_set_precision.setStyleSheet("font-size: 14px;")
        self.cb_set_precision.addItems(
            ['4', '5', '6', '7', '8'])
        self.cb_set_precision.setCurrentText('6')
        self.cb_set_precision.setFixedWidth(50)
        set_precision_layout.addWidget(self.cb_set_precision)
        label_right = self.QLabelWithFont(
            " знаков после запятой", 14)
        set_precision_layout.addWidget(label_right)
        set_precision_layout.addStretch()
        combined_layout.addLayout(set_precision_layout)

        # Кнопка анализа
        self.button_analyze = QPushButton("Начать анализ")
        font = QFont()
        font.setPointSize(16)
        self.button_analyze.setFont(font)
        self.button_analyze.setMinimumSize(200, 40)
        self.button_analyze.clicked.connect(self.start_analyze)
        combined_layout.addWidget(self.button_analyze)

        self.output_devices = QMediaDevices.audioOutputs()
        if self.output_devices:
            def create_sound_effect(file_name):
                sound = QSoundEffect()

                parent_dir = Path(__file__).parent.parent
                sound.setSource(QUrl.fromLocalFile(
                    os.path.join(parent_dir, "assets", "sounds", file_name)))
                sound.setAudioDevice(audio_device)
                sound.setVolume(0.2)
                return sound
            # Получение устройства вывода
            audio_device = QMediaDevices.defaultAudioOutput()
            # Создание звуковых эффектов
            self.soundError = create_sound_effect("snd_error.wav")
            self.soundWarning = create_sound_effect("snd_warning.wav")
            self.soundSuccess = create_sound_effect("snd_success.wav")

        # Устанавливаем общий макет в контейнер
        combined_container.setLayout(combined_layout)

        # Добавляем контейнер в стек
        self.stacked_widget.addWidget(combined_container)

    # перевод текста в алфавит и цифры, если надо его обрезка, и его отображение
    def process_loaded_text(self, target_sa, other_sa, target_te, other_te):
        if target_sa.text:
            target_sa.process_text_forms(other_sa.text_len)
            self.process_trimming(target_sa, other_sa, other_te)
            self.show_text_in_QTextEdit(target_te, target_sa.text_in_alphabet)
            target_te.setReadOnly(True)

    def rb_handle_alphabet_change(self):
        new_alphabet = self.radio_group.checkedButton().alphabet
        if (self.sa1.alphabet_name != new_alphabet or self.sa2.alphabet_name != new_alphabet):
            old_file_path_1 = self.sa1.file_path
            old_file_path_2 = self.sa2.file_path
            self.sa1.clear_text_data()
            self.sa2.clear_text_data()
            self.sa1.set_alphabet(self.radio_group.checkedButton().alphabet)
            self.sa2.set_alphabet(self.radio_group.checkedButton().alphabet)

            if old_file_path_1:
                self.sa1.read_text_from_file(
                    old_file_path_1)
            else:
                self.read_text_from_QTextEdit(self.text_edit1, self.sa1)

            if old_file_path_2:
                self.sa2.read_text_from_file(
                    old_file_path_2)
            else:
                self.read_text_from_QTextEdit(self.text_edit2, self.sa2)

            self.process_loaded_text(
                self.sa1, self.sa2, self.text_edit1, self.text_edit2)
            self.process_loaded_text(
                self.sa2, self.sa1, self.text_edit2, self.text_edit1)

    def read_text_from_QTextEdit(self, text_edit, sa):
        text = text_edit.toPlainText()
        if text:
            sa.text = list(text)

    def process_trimming(self, sa, other_sa, other_text_edit):
        if sa.trimmed_to_max_len:
            self.show_message("warning")
        elif other_sa.text_len > sa.text_len:
            other_sa.trimm_text_to_n(sa.text_len)
            other_text_edit.setText(''.join(other_sa.text_in_alphabet))
            self.show_message("warning")

    def open_text_file(self, file_num):
        sa = self.sa1 if file_num == 1 else self.sa2
        other_sa = self.sa2 if file_num == 1 else self.sa1
        text_edit = self.text_edit1 if file_num == 1 else self.text_edit2
        other_text_edit = self.text_edit2 if file_num == 1 else self.text_edit1
        button = self.button_open_file1 if file_num == 1 else self.button_open_file2

        # Если файл уже открыт, очищаем данные
        if sa.text or text_edit.toPlainText():
            sa.clear_text_data()
            text_edit.setText("")
            button.setText("Загрузить файл")
            text_edit.setReadOnly(False)
        else:
            # Открываем диалог выбора файла
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Text File", "", "Text Files (*.txt);;All Files (*)")
            if file_path:
                sa.file_path = file_path
                # Загружаем текст
                sa.read_text_from_file(file_path)
                self.process_loaded_text(
                    sa, other_sa, text_edit, other_text_edit)
                button.setText("Очистить файл")

    # Отображение текста в текстовый едитор
    def show_text_in_QTextEdit(self, text_edit, text):
        if text:
            text_edit.setText(''.join(text))

    def apply_shadow_effect(self, modal):
        shadow_effect = QGraphicsDropShadowEffect(modal)
        shadow_effect.setBlurRadius(10)
        shadow_effect.setColor(QColor(0, 0, 0, 150))
        shadow_effect.setOffset(0, 0)
        modal.setGraphicsEffect(shadow_effect)

    def show_message(self, status, title=None, text=None):
        if title is None:
            title = {
                "success": "Успех",
                "warning": "Предупреждение",
                "error": "Ошибка"
            }.get(status, "Сообщение")

        if text is None:
            text = {
                "success": "Анализ успешно завершён и\n доступен на вкладке \"Результаты анализа\"",
                "warning": "Один из текстов был урезан",
                "error": "Пожалуйста, выберите файл(ы)\nдля анализа или введите их \nсодержимое в текстовые поля"
            }.get(status, "Сообщение")

        modal_class = {
            "success": QCustomModals.SuccessModal,
            "warning": QCustomModals.WarningModal,
            "error": QCustomModals.ErrorModal
        }.get(status, QCustomModals.WarningModal)

        kwargs = {
            "title": title,
            "description": text,
            "position": "top-center",
            "parent": self,
            "animationDuration": 3000
        }

        # Создаем и показываем модальное окно
        modal = modal_class(**kwargs)
        self.apply_shadow_effect(modal)
        modal.show()

        if self.output_devices:
            sound = {
                "success": self.soundSuccess,
                "warning": self.soundWarning,
                "error": self.soundError
            }.get(status, self.soundError)
            sound.play()

    def start_analyze(self):
        self.results_precision = int(self.cb_set_precision.currentText())
        # Выполняем анализ
        if not self.sa1.text:
            self.read_text_from_QTextEdit(self.text_edit1, self.sa1)
            self.process_loaded_text(
                self.sa1, self.sa2, self.text_edit1, self.text_edit2)
        if not self.sa2.text:
            self.read_text_from_QTextEdit(self.text_edit2, self.sa2)
            self.process_loaded_text(
                self.sa2, self.sa1, self.text_edit2, self.text_edit1)

        if not self.sa1.text and not self.sa2.text:
            self.show_message("error")
        else:
            if self.sa1.text:
                self.sa1.single_text_analyze()
            if self.sa2.text:
                self.sa2.single_text_analyze()

            # Страница выбора файлов для анализа
            self.analyze_results_page()
            self.show_message("success")

    def analyze_results_page(self):
        # Удаляем старые результаты анализа, если он производился
        widget = self.stacked_widget.widget(1)
        if widget:
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
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
        btn4 = QPushButton("Экспорт результатов")

        btn1.clicked.connect(lambda: self.stats_container.setCurrentIndex(0))
        btn2.clicked.connect(lambda: self.stats_container.setCurrentIndex(1))
        btn3.clicked.connect(lambda: self.stats_container.setCurrentIndex(2))
        btn4.clicked.connect(lambda: self.stats_container.setCurrentIndex(3))

        button_layout.addWidget(btn1)
        button_layout.addWidget(btn2)
        button_layout.addWidget(btn3)
        button_layout.addWidget(btn4)
        main_analyze_layout.addWidget(btns_container)

        # Контейнер для статистики
        self.stats_container = QStackedWidget()

        # 1-я страница для контейнера статистики
        # – Информация о вычисленной энтропии:
        self.stats_container.addWidget(self.entropy_info_widget())
        # 2-я – Информация о вероятностях в текстах:
        self.stats_container.addWidget(self.prob_tables_page())
        # 3-я – Гистограмма частот символов текстов:
        self.stats_container.addWidget(self.histograms_page())
        # 4-я – Экспорт результов в Excel файл:
        self.stats_container.addWidget(self.export_analyze_results())
        # Добавляем контейнер в стек
        main_analyze_layout.addWidget(self.stats_container)

        self.stacked_widget.addWidget(main_analyze_container)

    def entropy_info_widget(self):
        def add_label(text, row, col, span=1, align=Qt.AlignTop | Qt.AlignCenter):
            label = self.QLabelWithFont(text, 17)
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            stats_layout.addWidget(label, row, col, 1, span, alignment=align)
            return label

        container = QWidget()
        stats_layout = QGridLayout()
        stats_layout.setSpacing(5)  # Уменьшаем расстояние между элементами
        stats_layout.setContentsMargins(
            10, 10, 10, 10)  # Уменьшаем внешние отступы
        container.setLayout(stats_layout)

        title_added = False
        if self.sa1.text and self.sa2.text:
            title_added = True
            add_label("Вычисленные энтропии:", 0, 0,
                      4, Qt.AlignTop | Qt.AlignCenter)
        row = 1
        if self.sa1.text:
            if not title_added:
                add_label("Вычисленные энтропии:", 0, 0,
                          2, Qt.AlignTop | Qt.AlignCenter)
            add_label("Энтропия A:", row, 0)
            add_label(str(self.my_round(self.sa1.entropy)), row, 1)
            row += 1

            add_label("Марковская энтропия H(A|A):", row, 0)
            add_label(str(self.my_round(self.sa1.markov_entropy)), row, 1)
            row += 1

        rowB = 1
        if self.sa2.text:
            if not title_added:
                add_label("Вычисленные энтропии:", 0, 2,
                          2, Qt.AlignTop | Qt.AlignCenter)
            add_label("Энтропия B:", rowB, 2)
            add_label(str(self.my_round(self.sa2.entropy)), rowB, 3)
            rowB += 1

            add_label("Марковская энтропия H(B|B):", rowB, 2)
            add_label(str(self.my_round(self.sa2.markov_entropy)), rowB, 3)
            rowB += 1

        if self.sa1.text and self.sa2.text:
            add_label("Марковская энтропия H(A|B):", row, 0)
            add_label(str(self.my_round(
                self.sa1.markov_entropy_with(self.sa2))), row, 1)

            add_label("Марковская энтропия H(B|A):", row, 2)
            add_label(str(self.my_round(
                self.sa2.markov_entropy_with(self.sa1))), row, 3)
            row += 1

            add_label("Совместная энтропия H(A,B):", row, 0)
            add_label(str(self.my_round(
                self.sa1.joint_entropy_with(self.sa2))), row, 1)

            add_label("Совместная энтропия H(B,A):", row, 2)
            add_label(str(self.my_round(
                self.sa2.joint_entropy_with(self.sa1))), row, 3)

        return container

    def get_labels_from_alphabet(self, sa):
        alp_list = list(sa.alphabet)
        labels = []
        if sa.alphabet[-1] == ' ':
            labels += alp_list[:-1] + ["'_'"]
        else:
            labels += alp_list
        return labels

    def prob_tables_page(self):

        # Общий контейнер - вкладки для таблиц
        tab = QTabWidget()

        # Контейнеры страниц
        # 1 страница — безусловные вероятности текстов
        prob_container = QWidget()
        prob_layout = QGridLayout()
        prob_container.setLayout(prob_layout)
        # 2 страница — совместные вероятности текстов
        joint_prob_container = QWidget()
        joint_prob_layout = QGridLayout()
        joint_prob_container.setLayout(joint_prob_layout)
        # 3 страница — условные вероятности текстов
        condi_prob_container = QWidget()
        condi_prob_layout = QGridLayout()
        condi_prob_container.setLayout(condi_prob_layout)

        # Все данные вероятностей по одному тексту A
        if self.sa1.text:
            labels = self.get_labels_from_alphabet(self.sa1)
            prob_layout.addWidget(
                self.QLabelWithFont("Безусловные вероятности текста A", 17), 0, 0, alignment=Qt.AlignCenter)
            prob_A = self.create_table_with_data(self.sa1.prob, labels)
            prob_layout.addWidget(prob_A, 1, 0, alignment=Qt.AlignCenter)

            joint_prob_layout.addWidget(
                self.QLabelWithFont("Совместные вероятности текста A", 17), 0, 0, alignment=Qt.AlignCenter)
            joint_prob_A = self.create_table_with_data(
                self.sa1.joint_prob, labels)
            joint_prob_layout.addWidget(
                joint_prob_A, 1, 0, alignment=Qt.AlignCenter)

            condi_prob_layout.addWidget(
                self.QLabelWithFont("Условные вероятности текста A", 17), 0, 0, alignment=Qt.AlignCenter)
            condi_prob_A = self.create_table_with_data(
                self.sa1.cond_prob, labels)
            condi_prob_layout.addWidget(
                condi_prob_A, 1, 0, alignment=Qt.AlignCenter)

        # Все данные вероятностей по одному тексту B
        if self.sa2.text:
            labels = self.get_labels_from_alphabet(self.sa2)
            prob_layout.addWidget(
                self.QLabelWithFont("Безусловные вероятности текста B", 17), 0, 1, alignment=Qt.AlignCenter)
            prob_B = self.create_table_with_data(self.sa2.prob, labels)
            prob_layout.addWidget(prob_B, 1, 1, alignment=Qt.AlignCenter)

            joint_prob_layout.addWidget(
                self.QLabelWithFont("Совместные вероятности текста B", 17), 0, 1, alignment=Qt.AlignCenter)
            joint_prob_B = self.create_table_with_data(
                self.sa2.joint_prob, labels)
            joint_prob_layout.addWidget(
                joint_prob_B, 1, 1, alignment=Qt.AlignCenter)

            condi_prob_layout.addWidget(
                self.QLabelWithFont("Условные вероятности текста B", 17), 0, 1, alignment=Qt.AlignCenter)
            condi_prob_B = self.create_table_with_data(
                self.sa2.cond_prob, labels)
            condi_prob_layout.addWidget(
                condi_prob_B, 1, 1, alignment=Qt.AlignCenter)

        # Добавляем 1-3 страницы:
        tab.addTab(prob_container, "Безусловные")
        tab.addTab(joint_prob_container, "Совместные")
        tab.addTab(condi_prob_container, "Условные")

        # Все данные вероятностей при паре текстов A и B
        if self.sa1.text and self.sa2.text:
            labels = self.get_labels_from_alphabet(self.sa1)
            # 4 страница — совместные вероятности пары текстов
            joint_prob_two_container = QWidget()
            joint_prob_two_layout = QGridLayout()
            joint_prob_two_container.setLayout(joint_prob_two_layout)

            joint_prob_two_layout.addWidget(
                self.QLabelWithFont("Совместные вероятнсти A и B текстов", 17), 0, 0, alignment=Qt.AlignCenter)
            joint_prob_AB = self.create_table_with_data(
                self.sa1.calculate_conditional_prob_with(self.sa2), labels)
            joint_prob_two_layout.addWidget(
                joint_prob_AB, 1, 0, alignment=Qt.AlignCenter)

            joint_prob_two_layout.addWidget(
                self.QLabelWithFont("Совместные вероятнсти B и A текстов", 17), 0, 1, alignment=Qt.AlignCenter)
            joint_prob_BA = self.create_table_with_data(
                self.sa2.calculate_conditional_prob_with(self.sa1), labels)
            joint_prob_two_layout.addWidget(
                joint_prob_BA, 1, 1, alignment=Qt.AlignCenter)

            tab.addTab(joint_prob_two_container,
                       "Совместные пары текстов")

            # 5 страница — условные вероятности пары текстов
            condi_prob_two_container = QWidget()
            condi_prob_two_layout = QGridLayout()
            condi_prob_two_container.setLayout(condi_prob_two_layout)

            condi_prob_two_layout.addWidget(
                self.QLabelWithFont("Условные вероятнсти A при тексте B", 17), 0, 0, alignment=Qt.AlignCenter)
            condi_prob_AB = self.create_table_with_data(
                self.sa1.calculate_conditional_prob_with(self.sa2), labels)
            condi_prob_two_layout.addWidget(
                condi_prob_AB, 1, 0, alignment=Qt.AlignCenter)

            condi_prob_two_layout.addWidget(
                self.QLabelWithFont("Условные вероятнсти B при тексте A", 17), 0, 1, alignment=Qt.AlignCenter)
            condi_prob_BA = self.create_table_with_data(
                self.sa2.calculate_conditional_prob_with(self.sa1), labels)
            condi_prob_two_layout.addWidget(
                condi_prob_BA, 1, 1, alignment=Qt.AlignCenter)

            tab.addTab(condi_prob_two_container,
                       "Условные пары текстов")

        return tab

    def create_table_with_data(self, data, labels, width=380, height=450, cell_w=83, cell_h=30):
        cell_w = (self.results_precision+1) * 12
        table = QTableWidget()
        table.setRowCount(len(data))
        table.setColumnCount(
            len(data[0]) if isinstance(data[0], list) else 1)
        is_matrix = isinstance(data[0], list)
        # Размер таблицы
        if not (is_matrix):
            table.setFixedWidth(
                cell_w+table.verticalHeader().width()+30)
        else:
            table.setFixedWidth(width)
        table.setFixedHeight(height)
        # Заголовки таблиц
        if is_matrix:
            table.horizontalHeader().setDefaultSectionSize(cell_w)
            table.setHorizontalHeaderLabels(
                list(labels))
        else:
            table.horizontalHeader().setDefaultSectionSize(cell_w+30)
            table.setHorizontalHeaderLabels(["p(a_i)"])
        table.setVerticalHeaderLabels(
            list(labels))
        # Размеры заголовков
        table.verticalHeader().setDefaultSectionSize(cell_h)
        # запрет редактирования значений таблицы
        table.setEditTriggers(
            QAbstractItemView.NoEditTriggers)
        for k in range(len(data)):
            if is_matrix:
                for l in range(len(data[k])):
                    table.setItem(k, l, QTableWidgetItem(
                        str(self.my_round(data[k][l]))))
                    table.item(k, l).setTextAlignment(Qt.AlignCenter)
            else:
                table.setItem(k, 0, QTableWidgetItem(
                    str(self.my_round(data[k]))))
                table.item(k, 0).setTextAlignment(Qt.AlignCenter)
        return table

    def histograms_page(self):
        # Общий контейнер
        container = QWidget()
        layout = QVBoxLayout()

        # Создаем стек для гистограмм
        stacked_widget = QStackedWidget()

        # Первая страница (Гистограмма A)
        if self.sa1.text:
            page1 = QWidget()
            layout1 = QVBoxLayout()
            layout1.addWidget(
                self.QLabelWithFont("Гистограмма встречаемости символов текста A", 17), alignment=Qt.AlignTop | Qt.AlignCenter)
            hist_cont, self.hist_A = self.create_histogram(self.sa1)
            layout1.addWidget(hist_cont)
            page1.setLayout(layout1)
            stacked_widget.addWidget(page1)

        # Вторая страница (Гистограмма B)
        if self.sa2.text:
            page2 = QWidget()
            layout2 = QVBoxLayout()
            layout2.addWidget(
                self.QLabelWithFont("Гистограмма встречаемости символов текста B", 17), alignment=Qt.AlignTop | Qt.AlignCenter)
            hist_cont, self.hist_B = self.create_histogram(self.sa2)
            layout2.addWidget(hist_cont)
            page2.setLayout(layout2)
            stacked_widget.addWidget(page2)

        # Добавляем кнопки переключения
        if self.sa1.text and self.sa2.text:
            button_layout = QHBoxLayout()
            btn1 = QPushButton("Гистограмма A")
            btn2 = QPushButton("Гистограмма B")
            btn1.clicked.connect(lambda: stacked_widget.setCurrentIndex(0))
            btn2.clicked.connect(lambda: stacked_widget.setCurrentIndex(1))
            button_layout.addWidget(btn1)
            button_layout.addWidget(btn2)
            layout.addLayout(button_layout)

        layout.addWidget(stacked_widget)
        container.setLayout(layout)
        return container

    def create_histogram(self, current_sa):
        container = pg.GraphicsLayoutWidget()
        container.setBackground(QColor(33, 46, 74))
        labels = self.get_labels_from_alphabet(current_sa)
        xdict = dict(enumerate(labels))
        stringaxis = pg.AxisItem(orientation='bottom')
        stringaxis.setTicks([xdict.items()])

        plt1 = container.addPlot(axisItems={'bottom': stringaxis})
        plt1.setLimits(
            xMin=-2, xMax=current_sa.alphabet_len, minXRange=1, maxXRange=100,
            yMin=0, yMax=max(current_sa.frequencies)*1.01, minYRange=1, maxYRange=100
        )

        hist = pg.BarGraphItem(
            x=range(current_sa.alphabet_len), height=current_sa.frequencies, width=0.8,
            pen=QColor(33, 46, 74), brush=QColor(198, 104, 51)
        )
        plt1.addItem(hist)
        return container, hist

    def apply_custom_style(self, checkbox):
        checkbox.customizeQCustomCheckBox(
            bgColor="#c3c3c3",
            circlecolor="#fff",
            activecolor="#17a8e3",
            animationEasingCurve=QEasingCurve.Linear,
            animationDuration=200
        )

    def export_analyze_results(self):
        # Создаем контейнер и макет
        container = QWidget()
        layout = QGridLayout()
        container.setLayout(layout)

        # Заголовок
        layout.addWidget(self.QLabelWithFont("Экспорт данных", 17),
                         0, 0, 1, 2, alignment=Qt.AlignTop | Qt.AlignCenter)

        # Список меток и соответствующих им чекбоксов
        options = [
            ("Энтропии:", "cbx_export_entropy"),
            ("Таблицы вероятностей:", "cbx_export_probabilities"),
            ("Гистограммы частот:", "cbx_export_histograms"),
            ("Анализируемые файлы:", "cbx_export_texts")
        ]

        # Создаем фрейм для чекбоксов
        self.frame = QFrame(self.central_widget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)

        # Добавляем метки и чекбоксы
        for row, (label_text, checkbox_name) in enumerate(options, start=1):
            label = self.QLabelWithFont(label_text, 17)
            checkbox = QCustomCheckBox(self.frame)
            checkbox.setChecked(True)
            self.apply_custom_style(checkbox)

            # Устанавливаем минимальные размеры для чекбокса
            # Настройте размеры по необходимости
            checkbox.setMinimumSize(72, 27)

            # Добавляем в макет
            layout.addWidget(
                label, row, 0, alignment=Qt.AlignTop | Qt.AlignRight)
            layout.addWidget(checkbox, row, 1,
                             alignment=Qt.AlignTop | Qt.AlignCenter)

            # Добавляем чекбокс как атрибут класса
            setattr(self, checkbox_name, checkbox)

        # Кнопка экспорта
        self.btn_export = QPushButton("Выполнить экспорт данных")
        font = QFont()
        font.setPointSize(16)
        self.btn_export.setFont(font)
        self.btn_export.setMinimumSize(200, 40)
        self.btn_export.clicked.connect(self.create_export_files)
        layout.addWidget(self.btn_export, len(options) + 1, 0, 1, 2)

        return container

    def my_round(self, num):
        # f"{num:.{self.results_precision}f}"
        return round(num, self.results_precision)

    def add_entropy_worksheet(self, workbook):
        entropy_worksheet = workbook.add_worksheet("Энтропии")
        entropy_results = []
        bg_lbl_format = workbook.add_format(
            {'bg_color': '#5690d6', 'border': 1})
        bg_data_format = workbook.add_format(
            {'bg_color': '#b5cef3', 'border': 1})
        if self.sa1.text:
            entropy_A_results = [
                ("Энтропия A:", self.my_round(self.sa1.entropy)),
                ("Марковская энтропия H(A|A):",
                    self.my_round(self.sa1.markov_entropy))
            ]
            entropy_results.extend(entropy_A_results)

        if self.sa2.text:
            entropy_B_results = [
                ("Энтропия B:", self.my_round(
                    self.sa2.entropy)),
                ("Марковская энтропия H(B|B):",
                    self.my_round(self.sa2.markov_entropy))
            ]
            entropy_results.extend(entropy_B_results)

        if self.sa2.text and self.sa1.text:
            entropy_AB_results = [
                ("Марковская энтропия H(A|B):", self.my_round(
                    self.sa1.markov_entropy_with(self.sa2))),
                ("Марковская энтропия H(B|A):", self.my_round(
                    self.sa2.markov_entropy_with(self.sa1))),
                ("Совместная энтропия H(A,B):", self.my_round(
                    self.sa1.joint_entropy_with(self.sa2))),
                ("Совместная энтропия H(B,A):", self.my_round(
                    self.sa2.joint_entropy_with(self.sa1)))
            ]
            entropy_results.extend(entropy_AB_results)
        if not entropy_results:
            return

        entropy_worksheet.set_column(0, 0, 30)
        for idx, (label, data) in enumerate(entropy_results):
            # Заголовок в первый столбец
            entropy_worksheet.write(idx, 0, label, bg_lbl_format)
            # Значение во второй столбец
            entropy_worksheet.write(idx, 1, data, bg_data_format)

    def probabilities_tables_worksheet(self, workbook):

        if self.sa1.text:
            labels = self.get_labels_from_alphabet(self.sa1)
        elif self.sa2.text:
            labels = self.get_labels_from_alphabet(self.sa2)

        def write_table_to_workbook(title, data, cell_w=50, cell_h=20):
            cell_w = self.results_precision+2
            worksheet = workbook.add_worksheet(title)
            is_matrix = isinstance(data[0], list)
            # Размер таблицы
            if not is_matrix:
                worksheet.set_column(0, 1, cell_w)
            else:
                worksheet.set_column(0, len(data[0]), cell_w)
            bg_lbl_format = workbook.add_format(
                {'bg_color': '#5690d6', 'border': 1, 'align': 'center'})

            # Заголовки для данных
            if not is_matrix:
                worksheet.write(0, 1, "p(a_i)", bg_lbl_format)
            for lbl, i in zip(labels, range(len(labels))):
                worksheet.write(i+1, 0, lbl, bg_lbl_format)
                if is_matrix:
                    worksheet.write(0, i+1, lbl, bg_lbl_format)

            bg_data_format = workbook.add_format(
                {'bg_color': '#b5cef3', 'border': 1})
            for k in range(len(data)):
                if is_matrix:
                    for l in range(len(data[k])):
                        worksheet.write(
                            k+1, l+1, self.my_round(data[k][l]), bg_data_format)
                else:
                    worksheet.write(
                        k+1, 1, self.my_round(data[k]), bg_data_format)

        if self.sa1.text:
            write_table_to_workbook(
                "P(A)", self.sa1.prob)
            write_table_to_workbook(
                "P(A,A)", self.sa1.joint_prob)
            write_table_to_workbook(
                "P(A|A)", self.sa1.cond_prob)

        if self.sa2.text:
            write_table_to_workbook(
                "P(B)", self.sa2.prob)
            write_table_to_workbook(
                "P(B,B)", self.sa2.joint_prob)
            write_table_to_workbook(
                "P(B|B)", self.sa2.cond_prob)

        if self.sa2.text and self.sa1.text:
            # Запись совместных вероятностей A и B
            write_table_to_workbook("P(A,B)",
                                    self.sa1.calculate_joint_prob_with(self.sa2))

            # Запись совместных вероятностей B и A
            write_table_to_workbook("P(B,A)",
                                    self.sa2.calculate_joint_prob_with(self.sa1))

            # Запись условных вероятностей A при тексте B
            write_table_to_workbook("P(A|B)",
                                    self.sa1.calculate_conditional_prob_with(self.sa2))

            # Запись условных вероятностей B при тексте A
            write_table_to_workbook("P(B|A)",
                                    self.sa2.calculate_conditional_prob_with(self.sa1))

    def create_export_files(self):
        time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        folder_path = f"Analyze_results/Result_{time}/"
        workbook = xlsxwriter.Workbook(
            f"{folder_path}entropy_probabilities.xlsx")
        os.makedirs(folder_path, exist_ok=True)
        # Информация по энтропии
        if self.cbx_export_entropy.isChecked():
            self.add_entropy_worksheet(workbook)
        if self.cbx_export_probabilities.isChecked():
            self.probabilities_tables_worksheet(workbook)
        if self.cbx_export_histograms.isChecked():
            if self.sa1.text:
                hist_A_exp = export.ImageExporter(self.hist_A.scene())
                hist_A_exp.export(
                    f'{folder_path}histogramm_A.png')
            if self.sa2.text:
                hist_B_exp = export.ImageExporter(self.hist_B.scene())
                hist_B_exp.export(
                    f'{folder_path}histogramm_B.png')
        if self.cbx_export_texts.isChecked():
            if self.sa1.text:
                with open(os.path.join(folder_path, "A_text.txt"), "w", encoding="utf-8") as file:
                    text_str = ''.join(self.sa1.text_in_alphabet)
                    file.write(text_str)

            if self.sa2.text:
                with open(os.path.join(folder_path, "B_text.txt"), "w", encoding="utf-8") as file:
                    text_str = ''.join(self.sa2.text_in_alphabet)
                    file.write(text_str)

        workbook.close()
        self.show_message(
            "success", text=f"Результаты успешно сохранены\n и доступны по пути:\n{folder_path}")
