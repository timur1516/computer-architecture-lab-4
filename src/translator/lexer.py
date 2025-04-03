from src.translator.token._token import Token
from src.translator.token.token_type import TokenType


def is_simple_token_type(value: str) -> bool:
    try:
        token = TokenType(value)
        excluded = {TokenType.NUMBER, TokenType.SYMBOL, TokenType.EOF}
        return token not in excluded
    except ValueError:
        return False


def is_number(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False


class Lexer:
    literal_mode = None

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if len(self.text) > 0 else None
        self.literal_mode = False

    def next_char(self):
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.next_char()

    def parse_word(self):
        result = ''
        while self.current_char is not None and not self.current_char.isspace():
            result += self.current_char
            self.next_char()
        return result

    def parse_literal(self):
        literal = ''
        while self.current_char is not None and self.current_char != '"':
            literal += self.current_char
            self.next_char()
        return literal[1:-1]

    def get_next_token(self):
        while self.current_char is not None:

            if self.literal_mode:
                value = self.parse_literal()
                self.literal_mode = False
                return Token(TokenType.LITERAL, value)

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            word = self.parse_word()

            if word == '."':
                self.literal_mode = True

            if is_simple_token_type(word):
                return Token(TokenType(word), word)

            if is_number(word):
                return Token(TokenType.NUMBER, word)

            return Token(TokenType.SYMBOL, word)

        return Token(TokenType.EOF, 'eof')
