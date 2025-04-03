from src.translator.token.token_type import TokenType


class Token:
    def __init__(self, _type: TokenType, value: str):
        self.type = _type
        self.value = value

    def __str__(self):
        return self.value
