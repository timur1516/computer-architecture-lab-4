from __future__ import annotations

"""Вспомогательные функции, не имеющие прямого отношения к функциональности модели"""


def int_to_char_or_int(value: int) -> str:
    """Преобразует выходящее число в:

    - ascii символ, если значение лежит в промежутке от 0 до 128

    - то же самое число, но в строковом представлении

    В результате всегда строка
    """

    return chr(value) if 0 <= value < 128 else str(value)


def int_to_char(value: int) -> chr:
    """Преобразует число в ascii символ

    В случае если число не попадает в требуемый диапазон (от 0 до 128),
    используется символ не из таблицы ascii: ``�`` (``\\uFFFD``)
    """
    return chr(value) if 0 <= value < 128 else "\uFFFD"


def int_list_to_str(data: list[int], do_new_line: bool = False) -> str:
    """Преобразует список чисел в строку

    В случае если значение является корректным ascii символом, оно преобразуется в него

    При этом символ переноса строки (ascii код 10) выводится как ``\\n``.
    Это можно изменить, если указать аргумент `do_new_line` как `True`

    Иначе используется символ не из таблицы ascii: ``�`` (``\\uFFFD``)
    """

    result = "".join(int_to_char(x) for x in data)

    if not do_new_line:
        result = result.replace("\n", "\\n")

    return result
