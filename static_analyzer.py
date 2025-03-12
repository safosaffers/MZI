from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
import numpy as np
import pyqtgraph as pg
import os


class StaticAnalyzer:
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
        self.join_probabilities = []
        self.join_frequencies = []
        self.condi_probabilities = []
        self.entropy = 0

    def text_into_numbers(self):
        result = []
        result.append(0)  # начало файла
        self.text_len = 2
        with open(self.filename, 'r', encoding='utf-8') as f:
            while char := f.read(1).lower():
                if char in self.alphabet:
                    result.append(self.alphabet.find(char)+1)
                    self.text_len += 1
        result.append(0)  # конец файла
        self.numbers = result

    def probabilities_and_frequencies(self):
        frequencies = [0] * (self.alphabet_len)
        total = 0
        for i in self.numbers:
            frequencies[i] += 1
            total += 1
        probabilities = [freq / total if total !=
                         0 else 0 for freq in frequencies]
        self.probabilities = probabilities
        self.frequencies = frequencies

    def join_probabilities_and_frequencies(self):
        alp_len = self.alphabet_len
        join_frequencies = [
            [0 for j in range(alp_len)] for i in range(alp_len)]  # +1
        total = 1  # пары начала/конца и пара начало-конец
        text_len = len(self.numbers)
        for i in range(text_len-1):
            char_1 = self.numbers[i]
            char_2 = self.numbers[i+1]  # tab
            join_frequencies[char_1][char_2] += 1  # tab
            total += 1
        join_frequencies[0][0] = 1  # "Закольцовывание" начала и конца файла
        join_probabilities = [[join_frequencies[i][j]/total for j in range(alp_len)]
                              for i in range(alp_len)]
        self.join_probabilities = join_probabilities
        self.join_frequencies = join_frequencies

    def condition_probabilities(self):
        alp_len = self.alphabet_len
        result = [[0 for j in range(alp_len)] for i in range(alp_len)]
        for i in range(alp_len):
            for j in range(alp_len):
                if self.probabilities[j] != 0:
                    result[i][j] = self.join_probabilities[j][i] / \
                        self.probabilities[j]
        self.condi_probabilities = result

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
        hist = pg.BarGraphItem(x=range(self.alphabet_len-1), height=self.frequencies[1:], width=0.8, pen=QColor(
            33, 46, 74), brush=QColor(198, 104, 51))
        plt1.addItem(hist)
        pg.exec()

    def count_entropy(self):
        self.entropy = 0
        for i in self.probabilities:
            if i != 0:
                self.entropy += i*np.log2(1.0/i)


if __name__ == '__main__':
    dir = os.path.dirname(__file__)
    filename = os.path.join(
        dir, 'E:\\workHARD\\MZI\\test_texts\\Pushking.txt')  # easy_2.txt')  #

    analyzer = StaticAnalyzer(filename, 0)
    analyzer.text_into_numbers()
    analyzer.probabilities_and_frequencies()
    analyzer.join_probabilities_and_frequencies()
    analyzer.condition_probabilities()
    analyzer.count_entropy()

    # print("Вероятности отдельных символов:", analyzer.probabilities)
    # print("Совместные вероятности:", analyzer.join_probabilities)
    # print("Условные вероятности:", analyzer.condi_probabilities)
    print("Энтропия:", analyzer.entropy)
    # Рисование гистограммы
    analyzer.draw_histogram()
    total = [0 for i in range(analyzer.alphabet_len)]
    for i in range(analyzer.alphabet_len):
        for j in range(analyzer.alphabet_len):
            total[j] += analyzer.condi_probabilities[i][j]
    print(total)
