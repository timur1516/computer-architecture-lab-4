from __future__ import annotations

"""Вспомогательные функции для работы c бинарными данными
"""


def extract_bits(binary: int, n: int) -> int:
    """Извлечение младших `n` бит из числа.

    Выполняется при помощи маски
    """
    mask = (1 << n) - 1
    return binary & mask


def binary_to_signed_int(binary: int, n: int) -> int:
    """Выполняет преобразование бинарного представления числа целое знаковое число

    Учитывает ожидаемый размер числа в битах, извлекая только `n` младших битов

    Нужно для корректной обработки отрицательных чисел
    """
    value = extract_bits(binary, n)
    if value & (1 << (n - 1)):
        value -= 1 << n
    return value


def is_correct_bin_size_signed(binary: int, n: int) -> bool:
    """Проверка того, что бинарное представление знакового числа вмещается в `n` бит"""
    return -(1 << (n - 1)) <= binary < 1 << (n - 1)


def int_to_bin_word(binary: int) -> tuple[int, int, int, int]:
    """Преобразование целого числа в машинное слово (4 байта)"""
    return (binary >> 24) & 0xFF, (binary >> 16) & 0xFF, (binary >> 8) & 0xFF, binary & 0xFF


def bytes_to_int_array(binary: bytes) -> list[int]:
    """Преобразование массива байт в массив машинных слов (одно слово = одно int число)"""
    result = []
    for i in range(0, len(binary), 4):
        if i + 3 >= len(binary):
            break

        word = int.from_bytes(binary[i : i + 4], "big")

        result.append(word)

    return result
