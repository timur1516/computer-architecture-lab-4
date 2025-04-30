from src.translator.ast.__ast import (
    Ast,
    AstBlock,
    AstDefinition,
    AstIfStatement,
    AstInterrupt,
    AstLiteral,
    AstNumber,
    AstOperation,
    AstSymbol,
    AstVariableDeclaration,
    AstWhileStatement,
)
from src.translator.ast.ast_node_visitor import AstNodeVisitor


class AstPrinter(AstNodeVisitor):
    tab = None

    def print(self, tree: Ast):
        self.tab = 0
        self.visit(tree)

    def visit_operation(self, node: AstOperation):
        self._print(f"OPERATION: {node.token_type}")

    def visit_number(self, node: AstNumber):
        self._print(f"NUMBER: {node.value}")

    def visit_block(self, node: AstBlock):
        for block in node.children:
            self.visit(block)

    def visit_interrupt(self, node: AstInterrupt):
        self._print("INTERRUPT")
        self.tab += 1
        self.visit_block(node.block)
        self.tab -= 1
        self._print("END INTERRUPT")

    def visit_symbol(self, node: AstSymbol):
        self._print(f"SYMBOL: {node.name}")

    def visit_literal(self, node: AstLiteral):
        self._print(f"LITERAL: {node.value_id}")

    def visit_if_statement(self, node: AstIfStatement):
        self._print("IF STATEMENT")
        self.tab += 1
        self.visit(node.if_block)
        self.tab -= 1
        if node.else_block is not None:
            self._print("ELSE STATEMENT")
            self.tab += 1
            self.visit(node.else_block)
            self.tab -= 1
        self._print("END IF STATEMENT")

    def visit_while_statement(self, node: AstWhileStatement):
        self._print("WHILE STATEMENT")
        self.tab += 1
        self.visit(node.while_block)
        self.tab -= 1
        self._print("END WHILE STATEMENT")

    def visit_variable_declaration(self, node: AstVariableDeclaration):
        self._print(f"VARIABLE: {node.name}")

    def visit_definition(self, node: AstDefinition):
        self._print(f"DEFINITION: {node.name}")
        self.tab += 1
        self.visit(node.block)
        self.tab -= 1
        self._print("END DEFINITION")

    def _print(self, data: str):
        print("\t" * self.tab + data)
