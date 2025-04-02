from typing import List

from token_type import TokenType


class Ast:
    pass


class AstOperation(Ast):
    def __init__(self, token_type: TokenType):
        self.token_type = token_type


class AstNumber(Ast):
    def __init__(self, value: int):
        self.value = value


class AstSymbol(Ast):
    def __init__(self, name: str):
        self.name = name


class AstBlock(Ast):
    def __init__(self, children: List[Ast]):
        self.children = children


class AstVariableDeclaration(Ast):
    def __init__(self, name: str):
        self.name = name


class AstDefinition(Ast):
    def __init__(self, name: str, block: AstBlock):
        self.name = name
        self.block = block


class AstIfStatement(Ast):
    def __init__(self, if_block: AstBlock, else_block: AstBlock = None):
        self.if_block = if_block
        self.else_block = else_block


class AstWhileStatement(Ast):
    def __init__(self, while_block: AstBlock):
        self.while_block = while_block
