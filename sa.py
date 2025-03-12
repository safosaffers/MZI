from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
import numpy as np
import pyqtgraph as pg
import os
from collections import defaultdict


class StaticAnalyzer:
    def __init__(self, filename, alphabet_number):
        self.alphabet = self.get_alphabet(alphabet_number)
        self.alphabet_len = len(self.alphabet) + 1
        self.filename = filename
        self.text_len = 0
        self.numbers = []
        self.probabilities = []
        self.frequencies = []
        self.join_probabilities = []
        self.join_frequencies = []
        self.condi_probabilities = []
        self.entropy = 0
        self.markov_entropy = 0
        self.conditional_entropy = 0
        self.joint_entropy = 0

    def get_alphabet(self, alphabet_number):
        alphabets = {
            0: "абвгдеёжзийклмнопрстуфхцчшщъыьэюя ",
            1: "абвгдежзийклмнопрстуфхцчшщъыьэюя",
            2: "abcdefghijklmnopqrstuvwxyz ",
            3: "abcdefghiklmnopqrstuvwxyz"
        }
        return alphabets.get(alphabet_number, "")

    def analize(self):
        self.text_into_numbers()
        self.probabilities_and_frequencies()
        self.join_probabilities_and_frequencies()
        self.condition_probabilities()
        self.count_entropy()

    def text_into_numbers(self):
        result = [0]  # начало файла
        self.text_len = 2
        with open(self.filename, 'r', encoding='utf-8') as f:
            while char := f.read(1).lower():
                if char in self.alphabet:
                    result.append(self.alphabet.find(char) + 1)
                    self.text_len += 1
        result.append(0)  # конец файла
        self.numbers = result

    def probabilities_and_frequencies(self):
        frequencies = defaultdict(int)
        total = 0
        for i in self.numbers:
            frequencies[i] += 1
            total += 1
        probabilities = [frequencies[i] /
                         total for i in range(self.alphabet_len)]
        self.probabilities = probabilities
        self.frequencies = [frequencies[i] for i in range(self.alphabet_len)]

    def join_probabilities_and_frequencies(self):
        join_frequencies = [
            [0] * self.alphabet_len for _ in range(self.alphabet_len)]
        total = 1  # пары начала/конца и пара начало-конец
        text_len = len(self.numbers)
        for i in range(text_len - 1):
            char_1 = self.numbers[i]
            char_2 = self.numbers[i + 1]
            join_frequencies[char_1][char_2] += 1
            total += 1
        join_frequencies[0][0] = 1  # "Закольцовывание" начала и конца файла
        join_probabilities = [[join_frequencies[i][j] / total for j in range(
            self.alphabet_len)] for i in range(self.alphabet_len)]
        self.join_probabilities = join_probabilities
        self.join_frequencies = join_frequencies

    def condition_probabilities(self):
        result = [[0] * self.alphabet_len for _ in range(self.alphabet_len)]
        for i in range(self.alphabet_len):
            for j in range(self.alphabet_len):
                if self.probabilities[j] != 0:
                    result[i][j] = self.join_probabilities[j][i] / \
                        self.probabilities[j]
        self.condi_probabilities = result

    def count_entropy(self):
        self.entropy = -sum(p * np.log2(p)
                            for p in self.probabilities if p != 0)

    def draw_histogram(self):
        win = pg.GraphicsLayoutWidget(
            show=True, title="Статический анализатор кода. Каримов С. 1311")
        win.resize(800, 560)
        win.setBackground(QColor(33, 46, 74))
        alphabet_list = list(self.alphabet)
        new_alphabet = alphabet_list[:-1] + ["'_'"]
        xdict = dict(enumerate(new_alphabet))
        stringaxis = pg.AxisItem(orientation='bottom')
        stringaxis.setTicks([xdict.items()])
        plt1 = win.addPlot(axisItems={'bottom': stringaxis})
        plt1.setLimits(xMin=-2, xMax=self.alphabet_len-1, minXRange=7, maxXRange=100,
                       yMin=0, yMax=max(self.frequencies[1:]) + 1, minYRange=100, maxYRange=100)
        hist = pg.BarGraphItem(x=range(
            self.alphabet_len-1), height=self.frequencies[1:], width=0.8, pen=QColor(33, 46, 74), brush=QColor(198, 104, 51))
        plt1.addItem(hist)
        pg.exec()


def count_conditional_entropy(analyzer_A, analyzer_B):
    conditional_entropy = 0
    for i in range(analyzer_A.alphabet_len):
        for j in range(analyzer_B.alphabet_len):
            if analyzer_A.join_probabilities[i][j] != 0 and analyzer_B.condi_probabilities[i][j] != 0:
                conditional_entropy += analyzer_A.join_probabilities[i][j] * np.log2(
                    analyzer_B.condi_probabilities[i][j])
    return -conditional_entropy


def count_joint_entropy(analyzer_A, analyzer_B):
    joint_entropy = 0
    for i in range(analyzer_A.alphabet_len):
        for j in range(analyzer_B.alphabet_len):
            if analyzer_A.join_probabilities[i][j] != 0:
                joint_entropy += analyzer_A.join_probabilities[i][j] * np.log2(
                    analyzer_A.join_probabilities[i][j])
    return -joint_entropy


if __name__ == '__main__':
    dir = os.path.dirname(__file__)
    # easy_2.txt')  #
    A_filename = os.path.join(
        dir, 'E:\\workHARD\\MZI\\test_texts\\Pushking.txt')
    A = StaticAnalyzer(A_filename, 0)
    A.analize()

    B_filename = os.path.join(
        dir, 'E:\\workHARD\\MZI\\test_texts\\Pushking_Caesar.txt')
    B = StaticAnalyzer(B_filename, 0)
    B.analize()
    # total = [0 for i in range(A.alphabet_len)]
    # for i in range(A.alphabet_len):
    #     for j in range(A.alphabet_len):
    #         total[j] += A.condi_probabilities[i][j]

    # total = [0 for i in range(B.alphabet_len)]
    # for i in range(B.alphabet_len):
    #     for j in range(B.alphabet_len):
    #         total[j] += B.condi_probabilities[i][j]
    print("H(A):", A.entropy)
    print("H(A|A):", count_conditional_entropy(A, A))

    print("H(B):", A.entropy)
    print("H(B|B):", count_conditional_entropy(B, B))

    print("H(A, B):", count_joint_entropy(A, B))

    A.draw_histogram()
    B.draw_histogram()
