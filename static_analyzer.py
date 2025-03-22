"""
Данный файл определяет методы для вычисления энтропии и вероятностей.
"""
import numpy as np


class StaticAnalyzer:
    def __init__(self):
        self.alphabet_number = 0
        self.alphabet_len = 35  # 34 +1
        self.alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя "
        self.alphabet_name = "rus_34"
        self.file_path = ""
        self.text_len = -1  # текс не был загружен
        self.text = []
        self.text_in_numbers = []
        self.text_in_alphabet = []
        self.prob = []
        self.frequencies = []
        self.joint_prob = []
        self.joint_frequencies = []
        self.condi_prob = []
        self.entropy = 0
        self.markov_entropy = 0

    def single_text_analyze(self):
        self.prob_and_frequencies()
        self.joint_prob_and_frequencies()
        self.condition_prob()
        self.count_entropy()
        self.count_markov_entropy()

    def set_alphabet(self, alphabet_name):
        rus_34 = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя "
        rus_32 = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
        lat_27 = "abcdefghijklmnopqrstuvwxyz "
        lat_25 = "abcdefghiklmnopqrstuvwxyz"
        self.alphabet_name = alphabet_name
        match alphabet_name:
            case "rus_34":
                self.alphabet = rus_34
            case "rus_32":
                self.alphabet = rus_32
            case "lat_27":
                self.alphabet = lat_27
            case "lat_25":
                self.alphabet = lat_25
        self.alphabet_len = len(self.alphabet)+1

    def clear_text_data(self):
        self.text_len = -1
        self.file_path = ""
        self.text = []
        self.text_in_numbers = []
        self.text_in_alphabet = []

    def process_text_forms(self, file_path, max_len=-1):
        self.clear_text_data()
        self.file_path = file_path
        self.text_in_numbers.append(0)  # начало файла
        self.text_len = 2  # добавляем два символа начало и конец файла
        with open(file_path, 'r', encoding='utf-8') as f:
            while (max_len == -1 or self.text_len < max_len) and (char := f.read(1)):
                self.text.append(char)
                char = char.lower()
                if char in self.alphabet:
                    self.text_in_alphabet.append(char)
                    self.text_in_numbers.append(self.alphabet.find(char)+1)
                    self.text_len += 1
            # если остался нерпочитанный символ и он пренадлежит алфавиту
            # то мы сообщим о том, что текст был урезан
            char = f.read(1)
            trimmed_to_max_len = bool(char in self.alphabet and char != "")
        self.text_in_numbers.append(0)  # конец файла
        return trimmed_to_max_len

#################################################################################
#                       Методы для вычисления вероятностей                      #
#################################################################################

# Для одного текста:

# Вычисление вероятностей и частот отдельных символов
    def prob_and_frequencies(self):
        frequencies = [0] * (self.alphabet_len)
        total = 0
        for i in self.text_in_numbers:
            frequencies[i] += 1
            total += 1
        prob = [freq / total if total !=
                0 else 0 for freq in frequencies]
        self.prob = prob
        self.frequencies = frequencies

# Вычисление совместных вероятностей и частот пар символов
    def joint_prob_and_frequencies(self):
        joint_frequencies = [
            [0 for _ in range(self.alphabet_len)] for _ in range(self.alphabet_len)]  # +1
        total_pairs = 1  # пары начала/конца и пара начало-конец
        text_len = len(self.text_in_numbers)
        for i in range(text_len-1):
            char_1 = self.text_in_numbers[i]
            char_2 = self.text_in_numbers[i+1]  # tab
            joint_frequencies[char_1][char_2] += 1
            total_pairs += 1
        joint_frequencies[0][0] = 1  # "Закольцовывание" начала и конца файла
        joint_prob = [
            [freq / total_pairs if total_pairs != 0 else 0 for freq in row]
            for row in joint_frequencies
        ]
        self.joint_prob = joint_prob
        self.joint_frequencies = joint_frequencies

# Вычисление условных вероятностей
    def condition_prob(self):
        alp_len = self.alphabet_len
        result = [[0 for _ in range(alp_len)] for _ in range(alp_len)]
        for i in range(alp_len):
            for j in range(alp_len):
                if self.prob[j] != 0:
                    result[i][j] = self.joint_prob[j][i] / \
                        self.prob[j]
        self.condi_prob = result

# Проверка корректности вычислений
    def check_prob(self):
        print("----ПРОВЕРКА КОРРЕКТНОСТИ ВЫЧИСЛЕНИЙ ВЕРОЯТНОСТЕЙ----")
        # Проверка безусловных вероятностей:
        total = sum(self.prob)
        print(f"Суммарное значение вероятностей: {total}")
        print(" — корректно" if abs(1. - total) < 1E-6 else " — некорректно")

        # Проверка совместных вероятностей:
        # Сумма всех элементов матрицы
        total_joint = sum(sum(row) for row in self.joint_prob)
        print(f"Суммарное значение совместных вероятностей: {total_joint}")
        print(" — корректно" if abs(1. - total_joint)
              < 1E-6 else " — некорректно")

        # Проверка условных вероятностей:
        total_cond = [sum(self.condi_prob[i][j] for i in range(
            self.alphabet_len)) for j in range(self.alphabet_len)]
        # Учитываем случай, когда сумма равна 0
        is_correct_cond = all(abs(1. - i) < 1E-6 or i == 0 for i in total_cond)
        print(f"Суммарное значение условных вероятностей: {total_cond}")
        print(" — корректно" if is_correct_cond else " — некорректно")


# Для пары текстов:

# Вычисление совместной вероятности для пары текстов

    def calculate_joint_prob_with(self, other):
        if self.alphabet_number != other.alphabet_number:
            raise ValueError("Тексты должны иметь одинаковый алфавит!.")
        alp_len = self.alphabet_len

        joint_frequencies = [
            [0 for _ in range(alp_len)] for _ in range(alp_len)]
        # Считаем частоты пар символов из обоих текстов
        minLen = min(self.text_len, other.text_len)
        total_pairs = 0
        for i in range(minLen):  # Для случаев двух текстов последний "нуль символ" не смотрится
            char_a = self.text_in_numbers[i]
            char_b = other.text_in_numbers[i]
            joint_frequencies[char_a][char_b] += 1
            total_pairs += 1

        # Преобразуем частоты в вероятности
        joint_prob = [
            [freq / total_pairs if total_pairs != 0 else 0 for freq in row]
            for row in joint_frequencies
        ]
        return joint_prob

# Вычисление условной вероятности для пары текстов
    def calculate_conditional_prob_with(self, other):
        if self.alphabet_number != other.alphabet_number:
            raise ValueError(
                "Тексты должны иметь одинаковый алфавит!.")
        alp_len = self.alphabet_len
        joint_prob = self.calculate_joint_prob_with(other)
        conditional_prob = [
            [0 for _ in range(alp_len)] for _ in range(alp_len)]

        for i in range(alp_len):
            for j in range(alp_len):
                if other.prob[j] != 0:
                    conditional_prob[i][j] = joint_prob[i][j] / \
                        other.prob[j]

        return conditional_prob

#################################################################################
#                       Методы для вычисления энтропии                          #
#################################################################################

# Вычисление энтропии
    def count_entropy(self):
        self.entropy = 0
        for i in self.prob:
            if i != 0:
                self.entropy += i*np.log2(1.0/i)
        return self.entropy

# Энтропия Марковского процесса первого порядка для одного текста
    def count_markov_entropy(self):
        self.joint_prob_and_frequencies()
        joint_prob = self.joint_prob
        self.condition_prob()
        conditional_prob = self.condi_prob

        markov_entropy = 0
        for i in range(self.alphabet_len):
            for j in range(self.alphabet_len):
                if joint_prob[i][j] != 0 and conditional_prob[i][j] != 0:
                    markov_entropy -= joint_prob[i][j] * \
                        np.log2(conditional_prob[i][j])
        self.markov_entropy = markov_entropy
        return self.markov_entropy

# Энтропия Марковского процесса для двух текстов
    def markov_entropy_with(self, other):
        joint_prob = self.calculate_joint_prob_with(other)
        conditional_prob = self.calculate_conditional_prob_with(
            other)

        markov_entropy = 0
        for i in range(self.alphabet_len):
            for j in range(other.alphabet_len):
                if joint_prob[i][j] != 0 and conditional_prob[i][j] != 0:
                    markov_entropy -= joint_prob[i][j] * \
                        np.log2(conditional_prob[i][j])

        return markov_entropy

# Вычисление совместной энтропии
    def joint_entropy_with(self, other):
        joint_prob = self.calculate_joint_prob_with(other)

        joint_entropy = 0
        for i in range(self.alphabet_len):
            for j in range(other.alphabet_len):
                if joint_prob[i][j] != 0:
                    joint_entropy -= joint_prob[i][j] * \
                        np.log2(joint_prob[i][j])

        return joint_entropy
