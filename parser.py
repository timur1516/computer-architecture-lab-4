from grammar_start_tokens import *
from lexer import Lexer
from symbol import Symbol
from symbol_type import SymbolType
from token_type import TokenType


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = lexer.get_next_token()
        self.symbol_table = {}

    def compare_and_next(self, expected_token_type):
        if self.current_token.type != expected_token_type:
            raise SyntaxError(f'Expected {expected_token_type} but got {self.current_token.type}')

        self.current_token = self.lexer.get_next_token()

    def parse(self):
        return self.program()

    def program(self):
        terms = []
        while self.current_token.type in term_start_tokens:
            term = self.term()
            if term is not None:
                terms += term
        self.compare_and_next(TokenType.EOF)
        return terms

    def term(self):
        token = self.current_token
        if token.type in word_start_tokens:
            return self.word()
        elif token.type in statement_start_tokens:
            self.statement()

    def word(self):
        token = self.current_token
        if token.type == TokenType.NUMBER:
            return self.number()
        elif token.type == TokenType.SYMBOL:
            return self.symbol()
        elif token.type in operation_start_tokens:
            return self.operation()

    def number(self):
        token = self.current_token
        self.compare_and_next(TokenType.NUMBER)
        return [f'PUSH {token.value}']

    def symbol(self):
        word = self.current_token.value
        self.compare_and_next(TokenType.SYMBOL)

        if word not in self.symbol_table:
            raise SyntaxError(f'Unknown word >{word}<')

        symbol = self.symbol_table[word]

        if symbol.type == SymbolType.VARIABLE:
            return [f'PUSH {word}']
        elif symbol.type == SymbolType.DEFINITION:
            return symbol.content

    def statement(self):
        token = self.current_token
        if token.type == TokenType.VAR:
            self.compare_and_next(TokenType.VAR)
            self.declaration_statement()
        elif token.type == TokenType.COLON:
            self.compare_and_next(TokenType.COLON)
            self.definition_statement()

    def block(self):
        words = []
        while self.current_token.type in word_start_tokens:
            word = self.word()
            if word is not None:
                words += word
        return words

    def if_statement(self):
        statement = ['IF']
        statement += self.block()
        token = self.current_token
        if token.type == TokenType.ELSE:
            statement.append('ELSE')
            self.compare_and_next(TokenType.ELSE)
            statement += self.block()
        self.compare_and_next(TokenType.THEN)
        statement += ['ENDIF']
        return statement

    def loop_statement(self):
        statement = ['LOOP']
        statement += self.block()
        self.compare_and_next(TokenType.UNTIL)
        statement += ['ENDLOOP']
        return statement

    def declaration_statement(self):
        name = self.current_token.value
        if name in self.symbol_table:
            raise SyntaxError(f'Name >{name}< already declared')
        self.compare_and_next(TokenType.SYMBOL)
        self.symbol_table[name] = Symbol(name, SymbolType.VARIABLE)

    def definition_statement(self):
        name = self.current_token.value
        if name in self.symbol_table:
            raise SyntaxError(f'Name >{name}< already declared')
        self.compare_and_next(TokenType.SYMBOL)
        token = self.current_token
        content = []
        if token.type == TokenType.IF:
            self.compare_and_next(TokenType.IF)
            content = self.if_statement()
        elif token.type == TokenType.BEGIN:
            self.compare_and_next(TokenType.BEGIN)
            content = self.loop_statement()
        elif token.type in word_start_tokens:
            content = self.block()
        self.compare_and_next(TokenType.SEMICOLON)
        self.symbol_table[name] = Symbol(name, SymbolType.DEFINITION, content)

    def operation(self):
        token = self.current_token
        if token.type in operation_start_tokens:
            self.compare_and_next(token.type)
            return [f'OPERATION {token.type}']
