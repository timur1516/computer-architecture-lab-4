from __future__ import annotations

from src.translator.token.token_type import TokenType


class TranslationError(Exception):
    pass


class UnexpectedTokenError(TranslationError):
    def __init__(self, actual_token_type: TokenType, expected_token_type: TokenType | None = None):
        self.actual_token_type = actual_token_type
        self.expected_token_type = expected_token_type

        if expected_token_type is not None:
            super().__init__(f"Expected {self.expected_token_type} but got {self.actual_token_type}")
        else:
            super().__init__(f"Unexpected token: {self.actual_token_type}")


class UndefinedSymbolError(TranslationError):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name
        super().__init__(f"Symbol >{symbol_name}< is not defined")


class NameIsAlreadyInUseError(TranslationError):
    def __init__(self, name_: str):
        self.name_ = name_
        super().__init__(f"Name >{name_}< is already in use")
