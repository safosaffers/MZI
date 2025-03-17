# pip install pytest
# pip install pytest-cov
import pytest
from staticAnalyzer import StaticAnalyzer
import os

rus_34 = list("абвгдежзийклмнопрстуфхцчшщъыьэюяё ")
rus_32 = list("абвгдежзийклмнопрстуфхцчшщъыьэюя")
lat_27 = list("abcdefghijklmnopqrstuvwxyz ")
lat_25 = list("abcdefghiklmnopqrstuvwxyz")


@pytest.fixture
def analyzer():
    dir = os.path.dirname(__file__)
    filename = os.path.join(dir, 'E:\\workHARD\\MZI\\test_texts\\easy.txt')
    alphabet = rus_34
    analyzer = StaticAnalyzer(filename, alphabet)
    analyzer.text_into_numbers()
    return analyzer


def test_numbers_conversion():


def test_text_length(analyzer):
    assert analyzer.text_len == 4


def test_probabilities(analyzer):
    analyzer.probabilities_and_frequencies()
    for i in range(len(analyzer.probabilities)):
        if i == 0 or i == 1:
            assert analyzer.probabilities[i] == 0.5
        else:
            assert analyzer.probabilities[i] == 0.0
