from grammar_start_tokens import *
from lexer import Lexer
from token_type import TokenType


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = lexer.get_next_token()

    def compare_and_next(self, expected_token_type):
        if self.current_token.type != expected_token_type:
            raise SyntaxError(f'Expected {expected_token_type} but got {self.current_token.type}')

        self.current_token = self.lexer.get_next_token()

    def parse(self):
        self.program()

    def program(self):
        while self.current_token.type in term_start_tokens:
            self.term()
        self.compare_and_next(TokenType.EOF)

    def term(self):
        token = self.current_token
        if token.type in word_start_tokens:
            self.word()
        elif token.type in statement_start_tokens:
            self.statement()

    def word(self):
        token = self.current_token
        if token.type == TokenType.NUMBER:
            self.compare_and_next(TokenType.NUMBER)
            print(token)
        elif token.type == TokenType.WORD:
            self.compare_and_next(TokenType.WORD)
            print(token)
        elif token.type in operation_start_tokens:
            self.operation()

    def statement(self):
        token = self.current_token
        if token.type == TokenType.IF:
            self.compare_and_next(TokenType.IF)
            self.if_statement()
        if token.type == TokenType.BEGIN:
            self.compare_and_next(TokenType.BEGIN)
            self.loop_statement()
        if token.type == TokenType.VAR:
            self.compare_and_next(TokenType.VAR)
            self.declaration_statement()
        if token.type == TokenType.COLON:
            self.compare_and_next(TokenType.COLON)
            self.definition_statement()

    def block(self):
        while self.current_token.type in word_start_tokens:
            self.word()

    def if_statement(self):
        print('IF')
        self.block()
        token = self.current_token
        if token.type == TokenType.ELSE:
            print('ELSE')
            self.compare_and_next(TokenType.ELSE)
            self.block()
        self.compare_and_next(TokenType.THEN)

    def loop_statement(self):
        print('LOOP')
        self.block()
        self.compare_and_next(TokenType.UNTIL)

    def declaration_statement(self):
        self.compare_and_next(TokenType.WORD)
        print(f'DECLARATION: {self.current_token}')

    def definition_statement(self):
        print(f'DEFINITION: {self.current_token}')
        self.compare_and_next(TokenType.WORD)
        self.block()
        self.compare_and_next(TokenType.SEMICOLON)

    def operation(self):
        token = self.current_token
        if token.type in operation_start_tokens:
            self.compare_and_next(token.type)
            print(f'OPERATION: {token}')
