from __future__ import annotations

from src.translator.token.token_type import TokenType

"""Классы исключений при трансляции"""


class TranslationError(Exception):
    """Абстрактный класс исключение при трансляции"""

    pass


class UnexpectedTokenError(TranslationError):
    """Исключение возникающее при встрече неожидаемого токена во время парсинга

    Ожидаемый токен может быть указан в конструкторе, если он известен
    """

    def __init__(self, actual_token_type: TokenType, expected_token_type: TokenType | None = None):
        self.actual_token_type = actual_token_type
        self.expected_token_type = expected_token_type

        if expected_token_type is not None:
            super().__init__(f"Expected {self.expected_token_type} but got {self.actual_token_type}")
        else:
            super().__init__(f"Unexpected token: {self.actual_token_type}")


class UndefinedSymbolError(TranslationError):
    """Исключение возникающее при встрече неопределённого ранее символа в процессе парсинга"""

    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name
        super().__init__(f"Symbol >{symbol_name}< is not defined")


class NameIsAlreadyInUseError(TranslationError):
    """Исключение возникающее при попытке объявить переменную или пользовательский блок с именем, которое уже занято"""

    def __init__(self, name_: str):
        self.name_ = name_
        super().__init__(f"Name >{name_}< is already in use")
