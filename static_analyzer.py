"""
Данный файл определяет методы для вычисления энтропии и вероятностей.
"""
import numpy as np


class StaticAnalyzer:
    def __init__(self):
        self.alphabet_number = 0
        self.alphabet_len = 34
        self.alphabet = ""
        self.filename = ""
        self.text_len = 0
        self.numbers = []
        self.probabilities = []
        self.frequencies = []
        self.joint_probabilities = []
        self.joint_frequencies = []
        self.condi_probabilities = []
        self.entropy = 0

    def set_alphabet(self, alphabet_number):
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

    def text_into_numbers(self, filename, alphabet_number):
        self.filename = filename
        self.set_alphabet(alphabet_number)
        result = []
        result.append(0)  # начало файла
        self.text_len = 2  # добавляем два символа начало и конец файла
        with open(self.filename, 'r', encoding='utf-8') as f:
            while char := f.read(1).lower():
                if char in self.alphabet:
                    result.append(self.alphabet.find(char)+1)
                    self.text_len += 1
        result.append(0)  # конец файла
        self.numbers = result

#################################################################################
#                       Методы для вычисления вероятностей                      #
#################################################################################

# Для одного текста:

# Вычисление вероятностей и частот отдельных символов
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

# Вычисление совместных вероятностей и частот пар символов
    def joint_probabilities_and_frequencies(self):
        joint_frequencies = [
            [0 for _ in range(self.alphabet_len)] for _ in range(self.alphabet_len)]  # +1
        total_pairs = 1  # пары начала/конца и пара начало-конец
        text_len = len(self.numbers)
        for i in range(text_len-1):
            char_1 = self.numbers[i]
            char_2 = self.numbers[i+1]  # tab
            joint_frequencies[char_1][char_2] += 1
            total_pairs += 1
        joint_frequencies[0][0] = 1  # "Закольцовывание" начала и конца файла
        joint_probabilities = [
            [freq / total_pairs if total_pairs != 0 else 0 for freq in row]
            for row in joint_frequencies
        ]
        self.joint_probabilities = joint_probabilities
        self.joint_frequencies = joint_frequencies

# Вычисление условных вероятностей
    def condition_probabilities(self):
        alp_len = self.alphabet_len
        result = [[0 for _ in range(alp_len)] for _ in range(alp_len)]
        for i in range(alp_len):
            for j in range(alp_len):
                if self.probabilities[j] != 0:
                    result[i][j] = self.joint_probabilities[j][i] / \
                        self.probabilities[j]
        self.condi_probabilities = result

# Проверка корректности вычислений
    def check_probabilities(self):
        print("----ПРОВЕРКА КОРРЕКТНОСТИ ВЫЧИСЛЕНИЙ ВЕРОЯТНОСТЕЙ----")
        # Проверка безусловных вероятностей:
        total = sum(self.probabilities)
        print(f"Суммарное значение вероятностей: {total}")
        print(" — корректно" if abs(1. - total) < 1E-6 else " — некорректно")

        # Проверка совместных вероятностей:
        # Сумма всех элементов матрицы
        total_joint = sum(sum(row) for row in self.joint_probabilities)
        print(f"Суммарное значение совместных вероятностей: {total_joint}")
        print(" — корректно" if abs(1. - total_joint)
              < 1E-6 else " — некорректно")

        # Проверка условных вероятностей:
        total_cond = [sum(self.condi_probabilities[i][j] for i in range(
            self.alphabet_len)) for j in range(self.alphabet_len)]
        # Учитываем случай, когда сумма равна 0
        is_correct_cond = all(abs(1. - i) < 1E-6 or i == 0 for i in total_cond)
        print(f"Суммарное значение условных вероятностей: {total_cond}")
        print(" — корректно" if is_correct_cond else " — некорректно")


# Для пары текстов:

# Вычисление совместной вероятности для пары текстов


    def calculate_joint_probabilities_with(self, other):
        if self.alphabet_number != other.alphabet_number:
            raise ValueError("Тексты должны иметь одинаковый алфавит!.")
        alp_len = self.alphabet_len

        joint_frequencies = [
            [0 for _ in range(alp_len)] for _ in range(alp_len)]
        # Считаем частоты пар символов из обоих текстов
        minLen = min(len(self.numbers), len(other.numbers))
        total_pairs = 0
        for i in range(minLen):  # Для случаев двух текстов последний "нуль символ" не смотрится
            char_a = self.numbers[i]
            char_b = other.numbers[i]
            joint_frequencies[char_a][char_b] += 1
            total_pairs += 1

        # Преобразуем частоты в вероятности
        joint_probabilities = [
            [freq / total_pairs if total_pairs != 0 else 0 for freq in row]
            for row in joint_frequencies
        ]
        return joint_probabilities

# Вычисление условной вероятности для пары текстов
    def calculate_conditional_probabilities_with(self, other):
        if self.alphabet_number != other.alphabet_number:
            raise ValueError(
                "Тексты должны иметь одинаковый алфавит!.")
        alp_len = self.alphabet_len
        joint_probabilities = self.calculate_joint_probabilities_with(other)
        conditional_probabilities = [
            [0 for _ in range(alp_len)] for _ in range(alp_len)]

        for i in range(alp_len):
            for j in range(alp_len):
                if other.probabilities[j] != 0:
                    conditional_probabilities[i][j] = joint_probabilities[i][j] / \
                        other.probabilities[j]

        return conditional_probabilities

#################################################################################
#                       Методы для вычисления энтропии                          #
#################################################################################

# Вычисление энтропии
    def count_entropy(self):
        self.entropy = 0
        for i in self.probabilities:
            if i != 0:
                self.entropy += i*np.log2(1.0/i)
        return self.entropy

# Энтропия Марковского процесса первого порядка для одного текста
    def count_markov_entropy(self):
        self.joint_probabilities_and_frequencies()
        joint_probabilities = self.joint_probabilities
        self.condition_probabilities()
        conditional_probabilities = self.condi_probabilities

        markov_entropy = 0
        for i in range(self.alphabet_len):
            for j in range(self.alphabet_len):
                if joint_probabilities[i][j] != 0 and conditional_probabilities[i][j] != 0:
                    markov_entropy -= joint_probabilities[i][j] * \
                        np.log2(conditional_probabilities[i][j])

        return markov_entropy

# Энтропия Марковского процесса для двух текстов
    def count_markov_entropy_with(self, other):
        joint_probabilities = self.calculate_joint_probabilities_with(other)
        conditional_probabilities = self.calculate_conditional_probabilities_with(
            other)

        markov_entropy = 0
        for i in range(self.alphabet_len):
            for j in range(other.alphabet_len):
                if joint_probabilities[i][j] != 0 and conditional_probabilities[i][j] != 0:
                    markov_entropy -= joint_probabilities[i][j] * \
                        np.log2(conditional_probabilities[i][j])

        return markov_entropy

# Вычисление совместной энтропии
    def count_joint_entropy_with(self, other):
        joint_probabilities = self.calculate_joint_probabilities_with(other)

        joint_entropy = 0
        for i in range(self.alphabet_len):
            for j in range(other.alphabet_len):
                if joint_probabilities[i][j] != 0:
                    joint_entropy -= joint_probabilities[i][j] * \
                        np.log2(joint_probabilities[i][j])

        return joint_entropy
