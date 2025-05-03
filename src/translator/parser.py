from __future__ import annotations

from src.translator.ast_.ast_ import (
    AstBlock,
    AstDVariableDeclaration,
    AstExtendedNumber,
    AstIfStatement,
    AstInterrupt,
    AstLiteral,
    AstMemoryBlockDeclaration,
    AstNumber,
    AstOperation,
    AstStringDeclaration,
    AstSymbol,
    AstVariableDeclaration,
    AstWhileStatement,
)
from src.translator.exceptions.exceptions import NameIsAlreadyInUseError, UndefinedSymbolError, UnexpectedTokenError
from src.translator.lexer import Lexer
from src.translator.token.grammar_start_tokens import (
    declaration_start_tokens,
    operation_start_tokens,
    statement_body_start_tokens,
    statement_start_tokens,
    term_start_tokens,
    word_start_tokens,
)
from src.translator.token.token_type import TokenType


class Parser:
    """Выполняет преобразование набора токенов, полученных от лексера в AST-дерево

    Также создаёт таблицу символов, массив литералов и словарь определений

    В ходе обработки выполняет проверку грамматической корректности кода
    """

    lexer = None
    "Объект лексера. Предполагается что в в него уже загружен текст программы"

    current_token = None
    "Текущий токен"

    symbol_table = None
    """Таблица символов

    Под символами понимаются имена переменных

    Хранит соответствие между именем символа и ero адресов в памяти

    Адреса определяются на этапе трансляции, поэтому изначально они устанавливаются в значение `-1`

    Данная таблица также используется для определения ситуаций использования необъявленной переменной
    или использования имени, занятого под переменную
    """

    literals = None
    "Массив строковых литералов"

    definitions = None
    """Словарь пользовательских объявлений

    Хранит соответствие между именем объявления и блоком операций

    Используется для разыменования объявлений в процессе парсинга

    Также используется для определения ситуаций пере использования имён
    """

    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = lexer.get_next_token()
        self.symbol_table: dict[str, int] = {}
        self.definitions: dict[str, AstBlock] = {}
        self.literals: list[str] = []

    def compare_and_next(self, expected_token_type: TokenType):
        """Сравнивает текущий символ с ожидаемым и переходит к следующему при совпадении

        При несовпадении выбрасывается исключение
        """
        if self.current_token.type != expected_token_type:
            raise UnexpectedTokenError(self.current_token.type, expected_token_type)

        self.current_token = self.lexer.get_next_token()

    def parse(self) -> AstBlock:
        """Входная точка парсинга"""

        return self.program()

    def program(self) -> AstBlock:
        program = self.term()
        self.compare_and_next(TokenType.EOF)
        return program

    def term(self) -> AstBlock:
        children = []
        while self.current_token.type in term_start_tokens:
            token = self.current_token
            term = None
            if token.type in word_start_tokens:
                term = self.word()
            elif token.type in statement_start_tokens:
                term = self.statement()
            if term is not None:
                children.append(term)
        return AstBlock(children)

    def word(self) -> AstNumber | AstExtendedNumber | AstSymbol | AstOperation:
        token = self.current_token
        if token.type is TokenType.SYMBOL:
            return self.symbol()
        if token.type is TokenType.NUMBER:
            return self.number()
        if token.type is TokenType.EXTENDED_NUMBER:
            return self.extended_number()
        if token.type in operation_start_tokens:
            return self.operation()
        raise UnexpectedTokenError(token.type)

    def statement(
        self,
    ) -> (
        AstIfStatement
        | AstWhileStatement
        | AstVariableDeclaration
        | AstDVariableDeclaration
        | AstStringDeclaration
        | AstMemoryBlockDeclaration
        | AstInterrupt
        | None
    ):
        token = self.current_token
        if token.type == TokenType.COLON:
            return self.definition_statement()
        if token.type in declaration_start_tokens:
            return self.declaration_statement()
        if token.type is TokenType.BEGIN_INT:
            return self.interrupt_statement()
        raise UnexpectedTokenError(token.type)

    def symbol(self) -> AstSymbol | AstBlock:
        word = self.current_token.value
        self.compare_and_next(TokenType.SYMBOL)
        if word in self.definitions:
            return self.definitions[word]
        if word in self.symbol_table:
            return AstSymbol(word)
        raise UndefinedSymbolError(word)

    def number(self) -> AstNumber:
        token = self.current_token
        self.compare_and_next(TokenType.NUMBER)
        value = int(token.value)
        # TODO: Добавить проверку корректности значения value на ОДЗ
        return AstNumber(value)

    def extended_number(self) -> AstExtendedNumber:
        token = self.current_token
        self.compare_and_next(TokenType.EXTENDED_NUMBER)
        value = int(token.value)
        # TODO: Добавить проверку корректности значения value на ОДЗ
        return AstExtendedNumber(value)

    def operation(self) -> AstOperation:
        token = self.current_token
        if token.type in operation_start_tokens:
            self.compare_and_next(token.type)
            return AstOperation(token.type)
        raise UnexpectedTokenError(token.type)

    def definition_statement(self):
        self.compare_and_next(TokenType.COLON)

        name = self.current_token.value
        self.compare_and_next(TokenType.SYMBOL)
        if name in self.definitions or name in self.symbol_table:
            raise NameIsAlreadyInUseError(name)

        definition_body = self.statement_body()

        self.compare_and_next(TokenType.SEMICOLON)

        self.definitions[name] = definition_body

    def declaration_statement(
        self,
    ) -> AstVariableDeclaration | AstDVariableDeclaration | AstStringDeclaration | AstMemoryBlockDeclaration:
        token = self.current_token
        if token.type in TokenType.VAR:
            return self.variable_declaration()
        if token.type == TokenType.D_VAR:
            return self.d_variable_declaration()
        if token.type == TokenType.STR:
            return self.string_declaration()
        if token.type == TokenType.ALLOC:
            return self.memory_block_declaration()
        raise UnexpectedTokenError(token.type)

    def interrupt_statement(self) -> AstInterrupt:
        self.compare_and_next(TokenType.BEGIN_INT)
        block = self.block()
        self.compare_and_next(TokenType.END_INT)
        return AstInterrupt(block)

    def statement_body(self) -> AstBlock:
        children = []
        while self.current_token.type in statement_body_start_tokens:
            token = self.current_token
            if token.type in word_start_tokens:
                children.append(self.block())
            if token.type is TokenType.IF:
                children.append(self.if_statement())
            if token.type is TokenType.BEGIN:
                children.append(self.loop_statement())
        return AstBlock(children)

    def variable_declaration(self) -> AstVariableDeclaration:
        self.compare_and_next(TokenType.VAR)

        name = self.current_token.value
        self.compare_and_next(TokenType.SYMBOL)
        if name in self.definitions or name in self.symbol_table:
            raise NameIsAlreadyInUseError(name)
        self.symbol_table[name] = -1

        return AstVariableDeclaration(name)

    def d_variable_declaration(self) -> AstDVariableDeclaration:
        self.compare_and_next(TokenType.D_VAR)

        name = self.current_token.value
        self.compare_and_next(TokenType.SYMBOL)
        if name in self.definitions or name in self.symbol_table:
            raise NameIsAlreadyInUseError(name)
        self.symbol_table[name] = -1

        return AstDVariableDeclaration(name)

    def string_declaration(self) -> AstStringDeclaration:
        self.compare_and_next(TokenType.STR)

        name = self.current_token.value
        self.compare_and_next(TokenType.SYMBOL)
        if name in self.definitions or name in self.symbol_table:
            raise NameIsAlreadyInUseError(name)
        self.symbol_table[name] = -1

        literal = self.literal()

        return AstStringDeclaration(name, literal)

    def memory_block_declaration(self) -> AstMemoryBlockDeclaration:
        self.compare_and_next(TokenType.ALLOC)

        name = self.current_token.value
        self.compare_and_next(TokenType.SYMBOL)
        if name in self.definitions or name in self.symbol_table:
            raise NameIsAlreadyInUseError(name)
        self.symbol_table[name] = -1

        token = self.current_token
        self.compare_and_next(TokenType.NUMBER)
        size = int(token.value)

        # TODO: Добавить проверку на корректность значения size

        return AstMemoryBlockDeclaration(name, size)

    def block(self) -> AstBlock:
        children = []
        while self.current_token.type in word_start_tokens:
            children.append(self.word())
        return AstBlock(children)

    def if_statement(self) -> AstIfStatement:
        self.compare_and_next(TokenType.IF)
        if_body = self.statement_body()
        else_body = None
        token = self.current_token
        if token.type == TokenType.ELSE:
            self.compare_and_next(TokenType.ELSE)
            else_body = self.statement_body()
        self.compare_and_next(TokenType.THEN)
        return AstIfStatement(if_body, else_body)

    def loop_statement(self) -> AstWhileStatement:
        self.compare_and_next(TokenType.BEGIN)
        while_body = self.statement_body()
        self.compare_and_next(TokenType.UNTIL)
        return AstWhileStatement(while_body)

    def literal(self) -> AstLiteral:
        self.compare_and_next(TokenType.STR_LITERAL_SEP)
        value = self.current_token.value
        self.compare_and_next(TokenType.LITERAL)
        self.literals.append(value)
        return AstLiteral(len(self.literals) - 1)
