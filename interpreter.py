from interpreter_state import State
from lexer import Lexer


class Interpreter:
    # --------------------------------------------------------------------------
    def __init__(self):
        self.stack = []
        self.memory = [0 for _ in range(256)]
        self.memory_ptr = 0

        self.basic_dict = {}
        self.extended_dict = {}
        self.condition_dict = {}
        self.loop_dict = {}
        self.variable_dict = {}

        self.add_default_lexemes()

        self.state = State.DEFAULT
        self.statement_name = None
        self.statement_body_buffer = []
        self.condition_body_buffer = []
        self.loop_body_buffer = []
        self.condition_alt_buffer = []
        self.loop_index = 0

    # --------------------------------------------------------------------------
    def add_default_lexemes(self):
        # Arithmetics
        self.basic_dict['+'] = self.add
        self.basic_dict['-'] = self.sub
        self.basic_dict['*'] = self.mul
        self.basic_dict['/'] = self.div

        # Comparisons
        self.basic_dict['='] = self.equal
        self.basic_dict['!='] = self.not_equal
        self.basic_dict['>'] = self.greater
        self.basic_dict['>='] = self.greater_or_equal
        self.basic_dict['<'] = self.less
        self.basic_dict['<='] = self.less_or_equal

        # Data stack manipulation
        self.basic_dict['dup'] = self.dup
        self.basic_dict['drop'] = self.drop
        self.basic_dict['swap'] = self.swap

        # IO
        self.basic_dict['.'] = self.print_stack_top_as_int
        self.basic_dict['emit'] = self.print_stack_top_as_char
        self.basic_dict[','] = self.read_symbol

        # Statements
        self.basic_dict[':'] = self.process_statement_start
        self.basic_dict[';'] = self.process_statement_end

        # Conditions
        self.basic_dict['if'] = self.process_condition_start
        self.basic_dict['else'] = self.process_condition_alt_start
        self.basic_dict['then'] = self.process_condition_end

        # Loop
        self.basic_dict['do'] = self.process_loop_start
        self.basic_dict['loop'] = self.process_loop_end
        self.basic_dict['i'] = self.push_loop_index

        # Variables
        self.basic_dict['var'] = self.process_variable_start

        # Memory
        self.basic_dict['!'] = self.store
        self.basic_dict['@'] = self.load

    # --------------------------------------------------------------------------
    def error(self, message):
        self.state = State.DEFAULT
        self.statement_name = None
        self.statement_body_buffer = []
        self.condition_body_buffer = []
        self.loop_body_buffer = []
        self.condition_alt_buffer = []
        self.loop_index = 0

        raise Exception(message)

    # --------------------------------------------------------------------------
    def pop(self):
        if len(self.stack) == 0:
            self.error('Stack is empty')
        return self.stack.pop()

    def push(self, word):
        self.stack.append(word)

    def print_int(self, n):
        print(f'> {n}')

    def print_char(self, code):
        print(f'> {chr(code)}')

    def read(self):
        return ord(input('< ')[0])

    def allocate_memory(self):
        self.memory_ptr += 1
        return self.memory_ptr - 1

    def store_by_address(self, address, n):
        self.memory[address] = n

    def load_by_address(self, address):
        return self.memory[address]

    # --------------------------------------------------------------------------
    def add(self):
        self.push(self.pop() + self.pop())

    def mul(self):
        self.push(self.pop() * self.pop())

    def sub(self):
        self.push(self.pop() - self.pop())

    def div(self):
        self.push(self.pop() / self.pop())

    def equal(self):
        self.push(self.pop() == self.pop())

    def not_equal(self):
        self.push(self.pop() != self.pop())

    def greater(self):
        self.push(self.pop() > self.pop())

    def greater_or_equal(self):
        self.push(self.pop() > self.pop())

    def less(self):
        self.push(self.pop() < self.pop())

    def less_or_equal(self):
        self.push(self.pop() < self.pop())

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

    def print_stack_top_as_int(self):
        self.print_int(self.pop())

    def print_stack_top_as_char(self):
        self.print_char(self.pop())

    def read_symbol(self):
        self.push(self.read())

    def store(self):
        self.store_by_address(self.pop(), self.pop())

    def load(self):
        self.push(self.load_by_address(self.pop()))

    # --------------------------------------------------------------------------
    def process_variable_start(self):
        if self.state != State.DEFAULT:
            self.error('Unexpected variable declaration')
        self.state = State.VARIABLE_NAME

    def process_variable_name(self, word):
        if word in self.variable_dict:
            self.error(f'Variable >{word}< is already defined')
        if word in self.basic_dict or word in self.extended_dict or word in self.condition_dict:
            self.error(f'Name >{word}< is already defined')

        self.variable_dict[word] = self.allocate_memory()
        self.state = State.DEFAULT

    def process_statement_start(self):
        if self.state != State.DEFAULT:
            self.error('Unexpected statement begin')
        self.state = State.STATEMENT_NAME

    def process_statement_name(self, word):
        if word in self.basic_dict or word in self.extended_dict or word in self.condition_dict or word in self.variable_dict:
            self.error(f'Name >{word}< is already defined')

        self.statement_name = word
        self.state = State.STATEMENT_BODY

    def process_statement_body(self, word):
        if word == ';' or word == 'if' or word == 'do':
            self.process_word(word)
        else:
            self.statement_body_buffer.append(word)

    def process_loop_start(self):
        if self.state != State.STATEMENT_BODY:
            self.error('Unexpected loop begin')
        self.state = State.LOOP_BODY

    def process_loop_body(self, word):
        if word == 'loop':
            self.process_word(word)
        else:
            self.loop_body_buffer.append(word)

    def process_loop_end(self):
        if self.state != State.LOOP_BODY:
            self.error('Unexpected loop end')

        self.loop_dict[self.statement_name] = [self.statement_body_buffer, self.loop_body_buffer]

        self.loop_body_buffer = []
        self.statement_body_buffer = []
        self.statement_name = None

        self.state = State.STATEMENT_BODY

    def push_loop_index(self):
        if self.state == State.LOOP_EXECUTION:
            self.push(self.loop_index)

    def process_condition_start(self):
        if self.state != State.STATEMENT_BODY:
            self.error('Unexpected condition begin')
        self.state = State.CONDITION_BODY

    def process_condition_body(self, word):
        if word == 'then' or word == 'else':
            self.process_word(word)
        else:
            self.condition_body_buffer.append(word)

    def process_condition_alt_start(self):
        if self.state != State.CONDITION_BODY:
            self.error('Unexpected condition alt begin')
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

    # --------------------------------------------------------------------------
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

        elif word in self.variable_dict:
            self.push(self.variable_dict[word])

        elif word in self.loop_dict:
            for w in self.loop_dict[word][0]:
                self.process_word(w)
            self.loop_index = self.pop()
            end = self.pop()
            self.state = State.LOOP_EXECUTION
            while self.loop_index < end:
                for w in self.loop_dict[word][1]:
                    self.process_word(w)
                self.loop_index += 1
            self.state = State.DEFAULT

        else:
            self.error(f'Unknown word >{word}<')

    # --------------------------------------------------------------------------
    def process_word_and_state(self, word):
        if self.state == State.DEFAULT:
            self.process_word(word)

        elif self.state == State.VARIABLE_NAME:
            self.process_variable_name(word)

        elif self.state == State.STATEMENT_NAME:
            self.process_statement_name(word)

        elif self.state == State.STATEMENT_BODY:
            self.process_statement_body(word)

        elif self.state == State.LOOP_BODY:
            self.process_loop_body(word)

        elif self.state == State.CONDITION_BODY:
            self.process_condition_body(word)

        elif self.state == State.CONDITION_ALT:
            self.process_condition_alt_body(word)

    # --------------------------------------------------------------------------
    def interpret(self, text):
        lexer = Lexer(text)
        word = lexer.get_next_word()
        while word is not None:
            self.process_word_and_state(word)
            word = lexer.get_next_word()
        if self.state == State.DEFAULT:
            print(f'Stack state: {self.stack}')
            print(f'Memory state: {self.memory}')
