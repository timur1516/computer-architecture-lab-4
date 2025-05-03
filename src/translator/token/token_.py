from src.translator.token.token_type import TokenType


class Token:
    """Токен, используемый во время парсинга"""

    type = None
    "Тип токена"

    value = None
    "Значение токена"

    def __init__(self, type_: TokenType, value: str):
        self.type = type_
        self.value = value

    def __str__(self):
        return self.value
