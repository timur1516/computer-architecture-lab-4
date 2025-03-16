from token_type import TokenType


class Token:
    def __init__(self, _type : TokenType, value : str | int = None):
        self.type = _type
        self.value = value

    def __str__(self):
        if self.value is not None: return f'Token({self.type}, {self.value})'
        return f'Token({self.type})'

