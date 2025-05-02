from __future__ import annotations

from src.translator.token.token_type import TokenType


class Ast:
    pass


class AstOperation(Ast):
    def __init__(self, token_type: TokenType):
        self.token_type = token_type


class AstNumber(Ast):
    def __init__(self, value: int):
        self.value = value


class AstExtendedNumber(Ast):
    def __init__(self, value: int):
        self.value = value


class AstSymbol(Ast):
    def __init__(self, name: str):
        self.name = name


class AstLiteral(Ast):
    def __init__(self, value_id: int):
        self.value_id = value_id


class AstBlock(Ast):
    def __init__(self, children: list[Ast]):
        self.children = children


class AstInterrupt(Ast):
    def __init__(self, block: AstBlock):
        self.block = block


class AstVariableDeclaration(Ast):
    def __init__(self, name: str):
        self.name = name


class AstDVariableDeclaration(Ast):
    def __init__(self, name: str):
        self.name = name


class AstStringDeclaration(Ast):
    def __init__(self, name: str, literal: AstLiteral):
        self.name = name
        self.literal = literal


class AstMemoryBlockDeclaration(Ast):
    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size


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
