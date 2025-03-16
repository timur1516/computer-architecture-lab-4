from enum import Enum, auto


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


class State(Enum):
    DEFAULT = auto()
    STATEMENT_NAME = auto()
    STATEMENT_BODY = auto()
    CONDITION_BODY = auto()
    CONDITION_ALT = auto()


class Interpreter:

    def __init__(self):
        self.stack = []
        self.basic_dict = {}
        self.extended_dict = {}
        self.condition_dict = {}
        self.add_default_lexemes()
        self.state = State.DEFAULT
        self.statement_body_buffer = []
        self.condition_body_buffer = []
        self.condition_alt_buffer = []
        self.statement_name = None

    def add_default_lexemes(self):
        self.basic_dict['+'] = self.add
        self.basic_dict['-'] = self.sub
        self.basic_dict['*'] = self.mul
        self.basic_dict['/'] = self.div
        self.basic_dict['dup'] = self.dup
        self.basic_dict['drop'] = self.drop
        self.basic_dict['swap'] = self.swap
        self.basic_dict[':'] = self.process_statement_start
        self.basic_dict[';'] = self.process_statement_end
        self.basic_dict['if'] = self.process_condition_start
        self.basic_dict['else'] = self.process_condition_alt_start
        self.basic_dict['then'] = self.process_condition_end

    def error(self, message):
        raise Exception(message)

    def pop(self):
        if len(self.stack) == 0:
            self.error('Stack is empty')
        return self.stack.pop()

    def push(self, word):
        self.stack.append(word)

    def add(self):
        self.push(self.pop() + self.pop())

    def mul(self):
        self.push(self.pop() * self.pop())

    def sub(self):
        self.push(self.pop() - self.pop())

    def div(self):
        self.push(self.pop() / self.pop())

    def dup(self):
        a = self.pop()
        self.push(a)
        self.push(a)

    def drop(self):
        self.pop()

    def swap(self):
        a = self.pop()
        b = self.pop()
        self.push(a)
        self.push(b)

    def process_statement_start(self):
        if self.state != State.DEFAULT:
            self.error('Unexpected statement')
        self.state = State.STATEMENT_NAME

    def process_statement_name(self, word):
        if word in self.basic_dict or word in self.extended_dict:
            self.error(f'Name "{word}" is already defined')

        self.statement_name = word
        self.state = State.STATEMENT_BODY

    def process_statement_body(self, word):
        if word == ';' or word == 'if':
            self.process_word(word)
        else:
            self.statement_body_buffer.append(word)

    def process_condition_start(self):
        if self.state != State.STATEMENT_BODY:
            self.error('Unexpected condition')
        self.state = State.CONDITION_BODY

    def process_condition_body(self, word):
        if word == 'then' or word == 'else':
            self.process_word(word)
        else:
            self.condition_body_buffer.append(word)

    def process_condition_alt_start(self):
        if self.state != State.CONDITION_BODY:
            self.error('Unexpected condition alt')
        self.state = State.CONDITION_ALT

    def process_condition_alt_body(self, word):
        if word == 'then':
            self.process_word(word)
        else:
            self.condition_alt_buffer.append(word)

    def process_condition_end(self):
        if self.state not in [State.CONDITION_ALT, State.CONDITION_BODY]:
            self.error('Unexpected condition end')

        self.condition_dict[self.statement_name] = [self.statement_body_buffer, self.condition_body_buffer,
                                                    self.condition_alt_buffer]

        self.condition_body_buffer = []
        self.condition_alt_buffer = []
        self.statement_body_buffer = []
        self.statement_name = None

        self.state = State.STATEMENT_BODY

    def process_statement_end(self):
        if self.state != State.STATEMENT_BODY:
            self.error('Unexpected statement end')

        if self.statement_name is not None:
            self.extended_dict[self.statement_name] = self.statement_body_buffer

            self.statement_body_buffer = []
            self.statement_name = None

        self.state = State.DEFAULT

    def process_word(self, word):
        if isinstance(word, int):
            self.push(word)

        elif word in self.basic_dict:
            self.basic_dict[word]()

        elif word in self.extended_dict:
            for w in self.extended_dict[word]:
                self.process_word(w)

        elif word in self.condition_dict:
            for w in self.condition_dict[word][0]:
                self.process_word(w)
            a = self.pop()
            if a != 0:
                for w in self.condition_dict[word][1]:
                    self.process_word(w)
            else:
                for w in self.condition_dict[word][2]:
                    self.process_word(w)

        else:
            self.error(f'Unknown word: {word}')

    def process_word_and_state(self, word):
        if self.state == State.DEFAULT:
            self.process_word(word)

        elif self.state == State.STATEMENT_NAME:
            self.process_statement_name(word)

        elif self.state == State.STATEMENT_BODY:
            self.process_statement_body(word)

        elif self.state == State.CONDITION_BODY:
            self.process_condition_body(word)

        elif self.state == State.CONDITION_ALT:
            self.process_condition_alt_body(word)

    def interpret(self, text):
        lexer = Lexer(text)
        word = lexer.get_next_word()
        while word is not None:
            self.process_word_and_state(word)
            word = lexer.get_next_word()
        if self.state == State.DEFAULT: print(f'Stack state: {self.stack}')


def main():
    interpreter = Interpreter()
    while True:
        text = input()
        try:
            interpreter.interpret(text)
        except Exception as e:
            print(f'Error: {e}')


if __name__ == '__main__':
    main()
