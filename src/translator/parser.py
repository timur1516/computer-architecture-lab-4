from __ast import AstBlock, AstNumber, Ast, AstOperation, AstSymbol, AstIfStatement, AstWhileStatement, \
    AstVariableDeclaration, \
    AstDefinition
from grammar_start_tokens import *
from lexer import Lexer
from token_type import TokenType


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = lexer.get_next_token()
        self.symbol_table = []
        self.definitions = {}

    def compare_and_next(self, expected_token_type: TokenType):
        if self.current_token.type != expected_token_type:
            raise SyntaxError(f'Expected {expected_token_type} but got {self.current_token.type}')

        self.current_token = self.lexer.get_next_token()

    def parse(self) -> AstBlock:
        return self.program()

    def program(self) -> AstBlock:
        children = []
        while self.current_token.type in term_start_tokens:
            term = self.term()
            if term is not None: children.append(term)
        self.compare_and_next(TokenType.EOF)
        return AstBlock(children)

    def term(self) -> Ast:
        token = self.current_token
        if token.type in word_start_tokens:
            return self.word()
        if token.type in statement_start_tokens:
            return self.statement()
        raise SyntaxError(f'Unexpected token: {token}')

    def word(self) -> AstNumber | AstSymbol | AstOperation:
        token = self.current_token
        if token.type == TokenType.NUMBER:
            return self.number()
        if token.type == TokenType.SYMBOL:
            return self.symbol()
        if token.type in operation_start_tokens:
            return self.operation()
        raise SyntaxError(f'Unexpected token: {token}')

    def number(self) -> AstNumber:
        token = self.current_token
        self.compare_and_next(TokenType.NUMBER)
        return AstNumber(int(token.value))

    def symbol(self) -> AstSymbol:
        word = self.current_token.value
        self.compare_and_next(TokenType.SYMBOL)

        if word in self.definitions:
            return self.definitions[word]
        if word in self.symbol_table:
            return AstSymbol(word)
        raise SyntaxError(f'Symbol >{word}< is not defined')

    def statement(self) -> AstIfStatement | AstWhileStatement | AstVariableDeclaration | AstDefinition:
        token = self.current_token
        if token.type == TokenType.VAR:
            self.compare_and_next(TokenType.VAR)
            return self.declaration_statement()
        if token.type == TokenType.COLON:
            self.compare_and_next(TokenType.COLON)
            return self.definition_statement()
        raise SyntaxError(f'Unexpected token: {token}')

    def block(self) -> AstBlock:
        children = []
        while self.current_token.type in word_start_tokens:
            children.append(self.word())
        return AstBlock(children)

    def if_statement(self) -> AstIfStatement:
        if_block = self.block()
        else_block = None
        token = self.current_token
        if token.type == TokenType.ELSE:
            self.compare_and_next(TokenType.ELSE)
            else_block = self.block()
        self.compare_and_next(TokenType.THEN)
        return AstIfStatement(if_block, else_block)

    def loop_statement(self) -> AstWhileStatement:
        while_block = self.block()
        self.compare_and_next(TokenType.UNTIL)
        return AstWhileStatement(while_block)

    def declaration_statement(self) -> AstVariableDeclaration:
        name = self.current_token.value
        self.compare_and_next(TokenType.SYMBOL)

        if name in self.definitions or name in self.symbol_table:
            raise SyntaxError(f'Name >{name}< is already in use')
        self.symbol_table.append(name)

        return AstVariableDeclaration(name)

    def definition_statement(self):
        name = self.current_token.value
        self.compare_and_next(TokenType.SYMBOL)

        if name in self.symbol_table:
            raise SyntaxError(f'Name >{name}< is already in use')

        token = self.current_token
        block = AstBlock([])
        if token.type == TokenType.IF:
            self.compare_and_next(TokenType.IF)
            block = self.if_statement()
        elif token.type == TokenType.BEGIN:
            self.compare_and_next(TokenType.BEGIN)
            block = self.loop_statement()
        elif token.type in word_start_tokens:
            block = self.block()
        self.compare_and_next(TokenType.SEMICOLON)

        self.definitions[name] = block

        # return AstDefinition(name, block)

    def operation(self):
        token = self.current_token
        if token.type in operation_start_tokens:
            self.compare_and_next(token.type)
            return AstOperation(token.type)
        raise SyntaxError(f'Unexpected token: {token}')
