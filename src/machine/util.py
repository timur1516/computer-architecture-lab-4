from __future__ import annotations

"""Вспомогательные функции, не имеющие прямого отношения к функциональности модели"""


def int_to_char(value: int, allow_control_chars: bool = False) -> str:
    """Преобразует число в ascii символ

    В случае если число не попадает в требуемый диапазон (от 0 до 128)
    или попадает в диапазон управляющих символов (0-31, кроме ``\\t``, ``\\n``, ``\\r``),
    используется символ не из таблицы ascii: ``�`` (``\\uFFFD``)

    Если `allow_control_chars` равно False, то ``\\t``, ``\\n``, ``\\r``
    заменяются на строковые представления ``"\\t"``, ``"\\n"``, ``"\\r"``.
    """
    if 32 <= value <= 126:
        return chr(value)

    if 0 <= value < 32:
        char = chr(value)
        if allow_control_chars and char in ("\t", "\n", "\r"):
            return char
        if not allow_control_chars and char == "\t":
            return "\\t"
        if not allow_control_chars and char == "\n":
            return "\\n"
        if not allow_control_chars and char == "\r":
            return "\\r"

    return "\uFFFD"


def int_list_to_str(data: list[int], allow_control_chars: bool = False) -> str:
    """Преобразует список чисел в строку

    В случае если число не попадает в требуемый диапазон (от 0 до 128)
    или попадает в диапазон управляющих символов (0-31, кроме ``\\t``, ``\\n``, ``\\r``),
    используется символ не из таблицы ascii: ``�`` (``\\uFFFD``)

    Если `allow_control_chars` равно False, то ``\\t``, ``\\n``, ``\\r``
    заменяются на строковые представления ``"\\t"``, ``"\\n"``, ``"\\r"``.
    """

    return "".join(int_to_char(x, allow_control_chars) for x in data)
