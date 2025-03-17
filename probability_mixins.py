class ProbabilityMixin:
    def text_into_numbers(self):
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

    def condition_probabilities(self):
        alp_len = self.alphabet_len
        result = [[0 for _ in range(alp_len)] for _ in range(alp_len)]
        for i in range(alp_len):
            for j in range(alp_len):
                if self.probabilities[j] != 0:
                    result[i][j] = self.joint_probabilities[j][i] / \
                        self.probabilities[j]
        self.condi_probabilities = result

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
