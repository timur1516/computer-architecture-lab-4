class Lexer:

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

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

    def parse_integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.next_char()
        return int(result)

    def get_next_word(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return self.parse_integer()

            return self.parse_word()

        return None
