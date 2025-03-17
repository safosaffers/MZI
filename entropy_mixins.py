import numpy as np


class EntropyMixin:
    def count_entropy(self):
        self.entropy = 0
        for i in self.probabilities:
            if i != 0:
                self.entropy += i*np.log2(1.0/i)
        return self.entropy

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

    def count_joint_entropy_with(self, other):
        joint_probabilities = self.calculate_joint_probabilities_with(other)

        joint_entropy = 0
        for i in range(self.alphabet_len):
            for j in range(other.alphabet_len):
                if joint_probabilities[i][j] != 0:
                    joint_entropy -= joint_probabilities[i][j] * \
                        np.log2(joint_probabilities[i][j])

        return joint_entropy
