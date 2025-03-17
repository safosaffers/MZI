from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
import os

from ui_mixins import UIMixin
from probability_mixins import ProbabilityMixin
from entropy_mixins import EntropyMixin


class StaticAnalyzer(UIMixin, ProbabilityMixin, EntropyMixin):
    def __init__(self, filename, alphabet_number):
        rus_34 = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя "
        rus_32 = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
        lat_27 = "abcdefghijklmnopqrstuvwxyz "
        lat_25 = "abcdefghiklmnopqrstuvwxyz"
        self.alphabet_number = alphabet_number
        match alphabet_number:
            case 0:
                self.alphabet = rus_34
            case 1:
                self.alphabet = rus_32
            case 2:
                self.alphabet = lat_27
            case 3:
                self.alphabet = lat_25
        self.alphabet_len = len(self.alphabet)+1
        self.filename = filename
        self.text_len = 0
        self.numbers = []
        self.probabilities = []
        self.frequencies = []
        self.joint_probabilities = []
        self.joint_frequencies = []
        self.condi_probabilities = []
        self.entropy = 0


if __name__ == '__main__':
    dir = os.path.dirname(__file__)
    file1 = os.path.join(dir, 'test_texts\\Pushking_2.txt')
    file2 = os.path.join(dir, 'test_texts\\Pushking_2_Gronsfield_351.txt')

    app = QApplication(sys.argv)

    # Создаем два анализатора для разных текстов
    analyzer1 = StaticAnalyzer(file1, 0)
    analyzer2 = StaticAnalyzer(file2, 0)

    # Обрабатываем тексты
    analyzer1.text_into_numbers()
    analyzer1.probabilities_and_frequencies()
    analyzer1.joint_probabilities_and_frequencies()
    analyzer1.condition_probabilities()
    analyzer1.show_main_window()
    analyzer2.text_into_numbers()
    analyzer2.probabilities_and_frequencies()
    analyzer2.joint_probabilities_and_frequencies()
    analyzer2.condition_probabilities()
    analyzer2.show_main_window()

    # Вычисляем энтропии
    print("Энтропия A:", analyzer1.count_entropy())
    print("Энтропия B:", analyzer2.count_entropy())

    markov_entropy_AA = analyzer1.count_markov_entropy()
    print("Марковская энтропия H(A|A):", markov_entropy_AA)

    markov_entropy_AB = analyzer1.count_markov_entropy_with(analyzer2)
    print("Марковская энтропия H(A|B):", markov_entropy_AB)

    joint_entropy_AB = analyzer1.count_joint_entropy_with(analyzer2)
    print("Совместная энтропия H(A, B):", joint_entropy_AB)

    sys.exit(app.exec_())
