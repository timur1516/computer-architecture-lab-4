from src.translator.token._token import Token
from src.translator.token.token_type import TokenType

COMMENT_START = "\\"


def is_simple_token_type(value: str) -> bool:
    try:
        token = TokenType(value)
    except ValueError:
        return False
    else:
        excluded = {TokenType.NUMBER, TokenType.SYMBOL, TokenType.EOF}
        return token not in excluded


def is_number(value: str) -> bool:
    try:
        int(value)
    except ValueError:
        return False
    else:
        return True


class Lexer:
    literal_mode = None

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if len(self.text) > 0 else None
        self.literal_mode = False
        self.comment_mode = False

    def shift_pos(self, shift):
        self.pos += shift
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def next_char(self):
        self.shift_pos(1)

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.next_char()

    def skip_comment(self):
        while self.current_char is not None and self.current_char != "\n":
            self.next_char()

    def parse_word(self):
        result = ""
        while self.current_char is not None and not self.current_char.isspace():
            result += self.current_char
            self.next_char()
        return result

    def watch_next_word(self):
        result = ""

        while self.current_char is not None and not self.current_char.isspace():
            result += self.current_char
            self.next_char()

        self.shift_pos(-len(result))

        return result

    def parse_literal(self):
        literal = ""
        while self.current_char is not None and self.current_char != TokenType.STR_LITERAL_SEP.value:
            literal += self.current_char
            self.next_char()
        return literal[1:-1]

    def get_next_token(self):  # noqa: C901 # На данный момент не проблема
        while self.current_char is not None:
            next_word = self.watch_next_word()
            if next_word == TokenType.STR_LITERAL_SEP.value:
                word = self.parse_word()
                self.literal_mode = not self.literal_mode
                return Token(TokenType(word), word)

            if self.literal_mode:
                value = self.parse_literal()
                return Token(TokenType.LITERAL, value)

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == COMMENT_START:
                self.skip_comment()
                continue

            word = self.parse_word()

            if is_simple_token_type(word):
                token = Token(TokenType(word), word)
            elif is_number(word):
                token = Token(TokenType.NUMBER, word)
            elif word[-1] == "." and is_number(word[:-1]):
                token = Token(TokenType.EXTENDED_NUMBER, word[:-1])
            else:
                token = Token(TokenType.SYMBOL, word)

            return token

        return Token(TokenType.EOF, "eof")
