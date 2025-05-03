from __future__ import annotations

from src.translator.token.token_type import TokenType

"""Классы для хранения AST дерева"""


class Ast:
    """Абстрактный узел AST-дерева"""

    pass


class AstOperation(Ast):
    """Операция"""

    token_type = None
    "Тип токена операции"

    def __init__(self, token_type: TokenType):
        self.token_type = token_type


class AstNumber(Ast):
    """Число"""

    value = None
    "Значение числа. От `-2^31` до `2^31 - 1`"

    def __init__(self, value: int):
        self.value = value


class AstExtendedNumber(Ast):
    """Число двойной точности"""

    value = None
    "Значение числа двойной точности. От `-2^63` до `2^63 - 1`"

    def __init__(self, value: int):
        self.value = value


class AstSymbol(Ast):
    """Символ - имя пользовательской переменной или конструкции"""

    name = None
    "Имя символа"

    def __init__(self, name: str):
        self.name = name


class AstLiteral(Ast):
    """Строковый литерал"""

    value_id = None
    "Индекс в массиве литералов"

    def __init__(self, value_id: int):
        self.value_id = value_id


class AstBlock(Ast):
    """Блок AST-вершин"""

    children = None
    "Список AST-вершин"

    def __init__(self, children: list[Ast]):
        self.children = children


class AstInterrupt(Ast):
    """Блок прерывания

    Хранит блок обработчика
    """

    def __init__(self, block: AstBlock):
        self.block = block


class AstVariableDeclaration(Ast):
    """Объявление переменной"""

    name = None
    "Имя переменной"

    def __init__(self, name: str):
        self.name = name


class AstDVariableDeclaration(Ast):
    """Объявление переменной двойной точности"""

    name = None
    "Имя переменной двойной точности"

    def __init__(self, name: str):
        self.name = name


class AstStringDeclaration(Ast):
    """Объявление строковой переменной"""

    name = None
    "Имя строки"

    def __init__(self, name: str, literal: AstLiteral):
        self.name = name
        self.literal = literal


class AstMemoryBlockDeclaration(Ast):
    """Объявление блока памяти"""

    name = None
    "Имя блока памяти"

    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size


class AstIfStatement(Ast):
    """Объявление условной конструкции"""

    if_block = None
    "Блок основного исполнения"

    else_block = None
    "Блок альтернативного исполнения"

    def __init__(self, if_block: AstBlock, else_block: AstBlock = None):
        self.if_block = if_block
        self.else_block = else_block


class AstWhileStatement(Ast):
    """Объявление цикла"""

    while_block = None
    "Блок тела цикла"

    def __init__(self, while_block: AstBlock):
        self.while_block = while_block
