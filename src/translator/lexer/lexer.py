from src.translator.token.token_ import Token
from src.translator.token.token_type import TokenType


class Lexer:
    """Выполняет преобразование текстового кода в поток токенов"""

    is_literal_mode = None
    "Флаг режима чтения литерала. Инициализируется значением `False`"

    text = None
    "Текстовая программа для обработки"

    pos = None
    "Текущая позиция в тексте. Инициализируется значением `0`"

    current_char = None
    """Символ на который указывает `pos`. Инициализируется вместе c `pos`.

    B случае если строка изначально пуста инициализируется значением `None`
    """

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if len(self.text) > 0 else None
        self.is_literal_mode = False

    @staticmethod
    def is_simple_token_type(value: str) -> bool:
        """Определяет, является ли строковое значение простым токеном

        Для проверки производится попытка создать объект токена по значению

        При этом не простые токены:

        - NUMBER

        - EXTENDED_NUMBER

        - SYMBOL

        - LITERAL

        - EOF

        исключаются из рассмотрения
        """
        try:
            token = TokenType(value)
        except ValueError:
            return False
        else:
            excluded = {TokenType.NUMBER, TokenType.EXTENDED_NUMBER, TokenType.SYMBOL, TokenType.LITERAL, TokenType.EOF}
            return token not in excluded

    @staticmethod
    def is_number(value: str) -> bool:
        """Проверяет, является ли строковое значение целым числом

        Для проверки выполняется попытка конвертации в `int`
        """

        try:
            int(value)
        except ValueError:
            return False
        else:
            return True

    def shift_pos(self, shift):
        """Выполняет смещение текущей позиции на `shift`

        Также обновляет `current_char`

        В случае если достигнут конец текста, в `current_char` записывается `None`
        """

        self.pos += shift
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def next_char(self):
        """Выполняет смещение на 1 символ вправо"""

        self.shift_pos(1)

    def skip_whitespace(self):
        """Выполняет пропуск пробельных символов"""

        while self.current_char is not None and self.current_char.isspace():
            self.next_char()

    def skip_comment(self):
        """Выполняет пропуск комментария

        Фактически пропускает всё до первого перевода строки
        """

        while self.current_char is not None and self.current_char != "\n":
            self.next_char()

    def parse_word(self):
        """Парсит отдельное слово

        Разделителем между словами является пробел
        """

        result = ""
        while self.current_char is not None and not self.current_char.isspace():
            result += self.current_char
            self.next_char()
        return result

    def parse_literal(self):
        """Парсит строковый литерал

        Предполагается, что литерал имеет вид ``" <literal>"`` и текущий указатель находится
        сразу после первого символа ``"``

        В начале происходит пропуск пробельного символа, после чего парится всё до первого символа ``"``

        В конце происходит пропуск символа ``"``
        """

        self.next_char()
        literal = ""
        while self.current_char is not None and self.current_char != TokenType.STR_LITERAL_SEP.value:
            literal += self.current_char
            self.next_char()
        self.next_char()
        return literal

    def get_next_token(self):  # noqa: C901 # На данный момент не проблема4
        """Возвращает очередной токен"""

        while self.current_char is not None:
            if self.is_literal_mode:
                value = self.parse_literal()
                self.is_literal_mode = False
                return Token(TokenType.LITERAL, value)

            if self.current_char == TokenType.COMMENT_START.value:
                self.skip_comment()
                continue

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            word = self.parse_word()

            if self.is_simple_token_type(word):
                token = Token(TokenType(word), word)
            elif self.is_number(word):
                token = Token(TokenType.NUMBER, word)
            elif word[-1] == "." and self.is_number(word[:-1]):
                token = Token(TokenType.EXTENDED_NUMBER, word[:-1])
            else:
                token = Token(TokenType.SYMBOL, word)

            if token.type == TokenType.STR_LITERAL_SEP:
                self.is_literal_mode = True

            return token

        return Token(TokenType.EOF, "eof")
