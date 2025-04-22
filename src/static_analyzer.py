"""
Класс StaticAnalyzer определяет методы для вычисления частот,
вероятностей и энтропий как одного текста, так и пары текстов.
Реализация включает обработку текстовых данных, подсчёт частот
символов и биграмм, а также расчёт различных видов энтропии
(источника, марковской, условной и совместной).
"""
import numpy as np
import sys
sys.path.append('../')
USE_START_AND_EOF_SYMBOL = False
USE_SHORT_ALPHABET_FOR_DEBUG = False


class StaticAnalyzer:
    def __init__(self):
        self.alphabet_number = 0
        if USE_SHORT_ALPHABET_FOR_DEBUG:
            if USE_START_AND_EOF_SYMBOL:
                self.alphabet_len = 4
                self.alphabet = "Øаб "
            else:
                self.alphabet_len = 3
                self.alphabet = "аб "
        else:
            if USE_START_AND_EOF_SYMBOL:
                self.alphabet_len = 35
                self.alphabet = "Øабвгдеёжзийклмнопрстуфхцчшщъыьэюя "
            else:
                self.alphabet_len = 34
                self.alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя "
        self.alphabet_name = "rus_34"
        self.file_path = ""
        # text_len - длина текста в алфавите,
        # ==-1 если текст не был загружен
        self.text_len = -1
        self.text = []
        self.text_in_alphabet_numbers = []
        self.text_in_alphabet = []
        self.prob = []
        self.frequencies = []
        self.joint_prob = []
        self.joint_frequencies = []
        self.cond_prob = []
        self.entropy = 0
        self.markov_entropy = 0

    def single_text_analyze(self):
        self.prob_and_frequencies()
        self.joint_prob_and_frequencies()
        self.condition_prob()
        self.count_entropy()
        self.count_markov_entropy()

    def set_alphabet(self, alphabet_name):
        if USE_START_AND_EOF_SYMBOL:
            rus_34 = "Øабвгдеёжзийклмнопрстуфхцчшщъыьэюя "
            rus_32 = "Øабвгдежзийклмнопрстуфхцчшщъыьэюя"
            lat_27 = "Øabcdefghijklmnopqrstuvwxyz "
            lat_25 = "Øabcdefghiklmnopqrstuvwxyz"
        else:
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
        self.alphabet_len = len(self.alphabet)

    def clear_text_data(self):
        self.text_len = -1
        self.file_path = ""
        self.text = []
        self.text_in_alphabet_numbers = []
        self.text_in_alphabet = []

    def read_text_from_file(self, file_path):
        self.clear_text_data()
        self.file_path = file_path
        self.text = []
        with open(file_path, 'r', encoding='utf-8') as f:
            while (char := f.read(1)):
                self.text.append(char)

    def process_text_forms(self, max_len=-1):
        self.text_in_alphabet = []
        self.text_in_alphabet_numbers = []
        self.text_len = 0

        # Добавляем формальный символ начала файла
        if USE_START_AND_EOF_SYMBOL:
            self.text_in_alphabet_numbers.append(0)  # Начало файла
            self.text_in_alphabet.append('Ø')
            self.text_len = 2  # Учитываем начало и конец файла

        # Обрабатываем текст
        n = 0
        for n in range(len(self.text)):
            if max_len != -1 and self.text_len >= max_len:
                break
            char = (self.text[n]).lower()
            if (char in self.alphabet):
                self.text_in_alphabet.append(char)
                self.text_in_alphabet_numbers.append(self.alphabet.find(char))
                self.text_len += 1
        else:
            n = n+1
        print(f"text_len = {self.text_len}")
        if USE_START_AND_EOF_SYMBOL:
            self.text_in_alphabet_numbers.append(0)  # Конец файла
            self.text_in_alphabet.append('Ø')

        self.trimmed_to_max_len = False
        _len = len(self.text)
        for i in range(n, _len):
            if self.text[i] in self.alphabet:
                self.trimmed_to_max_len = True
                break

        return self.trimmed_to_max_len

    def trimm_text_to_n(self, n):
        if USE_START_AND_EOF_SYMBOL:
            self.text_in_alphabet = self.text_in_alphabet[:(n-1)]+['Ø']
            self.text_in_alphabet_numbers = self.text_in_alphabet_numbers[:(
                n-1)]+[0]
        else:
            self.text_in_alphabet = self.text_in_alphabet[:n]
            self.text_in_alphabet_numbers = self.text_in_alphabet_numbers[:n]

############################################################
#            Методы для вычисления вероятностей            #
############################################################

# Для одного текста:

# Вычисление вероятностей и частот отдельных символов
    def prob_and_frequencies(self):
        frequencies = [0] * (self.alphabet_len)
        total = 0
        for i in self.text_in_alphabet_numbers:
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
        total_pairs = 0
        if USE_START_AND_EOF_SYMBOL:
            total_pairs = 1  # пара начало-конец
        text_len = len(self.text_in_alphabet_numbers)
        for i in range(0, text_len-1, 2):
            char_1 = self.text_in_alphabet_numbers[i]
            char_2 = self.text_in_alphabet_numbers[i+1]
            joint_frequencies[char_1][char_2] += 1
            total_pairs += 1
        if USE_START_AND_EOF_SYMBOL:
            # "Закольцовывание" начала и конца файла
            joint_frequencies[0][0] = 1
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
        self.cond_prob = result

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
        total_cond = [sum(self.cond_prob[i][j] for i in range(
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
        for i in range(minLen):
            char_a = self.text_in_alphabet_numbers[i]
            char_b = other.text_in_alphabet_numbers[i]
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
                    conditional_prob[i][j] = joint_prob[j][i] / \
                        other.prob[j]

        return conditional_prob

############################################################
#              Методы для вычисления энтропии              #
############################################################

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
        conditional_prob = self.cond_prob

        markov_entropy = 0
        for i in range(self.alphabet_len):
            for j in range(self.alphabet_len):
                if conditional_prob[i][j] != 0:
                    markov_entropy += self.prob[j]*conditional_prob[i][j] * \
                        np.log2(1.0/conditional_prob[i][j])
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
                if conditional_prob[i][j] != 0:
                    markov_entropy += joint_prob[j][i] * np.log2(1.0/conditional_prob[i][j])

        return markov_entropy

# Вычисление совместной энтропии
    def joint_entropy_with(self, other):
        joint_prob = self.calculate_joint_prob_with(other)
        cond_prob = self.calculate_conditional_prob_with(
            other)
        joint_entropy = 0
        for i in range(self.alphabet_len):
            for j in range(other.alphabet_len):
                # print(
                #     f"p(i,j)={joint_prob[i][j]}=p(i)*p(j|i)={self.prob[i]*cond_prob[j][i]}")
                if (joint_prob[i][j]) != 0:
                    joint_entropy += joint_prob[i][j] * \
                        np.log2(1.0/(joint_prob[i][j]))

        return joint_entropy
