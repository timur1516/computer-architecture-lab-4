from src.translator.ast.__ast import AstBlock, AstNumber, AstOperation, AstSymbol, AstIfStatement, AstWhileStatement, \
    AstVariableDeclaration, AstDefinition, Ast, AstLiteral, AstInterrupt


class AstNodeVisitor:
    def visit(self, node: Ast):
        if isinstance(node, AstOperation):
            return self.visit_operation(node)
        if isinstance(node, AstNumber):
            return self.visit_number(node)
        if isinstance(node, AstBlock):
            return self.visit_block(node)
        if isinstance(node, AstInterrupt):
            return self.visit_interrupt(node)
        if isinstance(node, AstSymbol):
            return self.visit_symbol(node)
        if isinstance(node, AstLiteral):
            return self.visit_literal(node)
        if isinstance(node, AstIfStatement):
            return self.visit_if_statement(node)
        if isinstance(node, AstWhileStatement):
            return self.visit_while_statement(node)
        if isinstance(node, AstVariableDeclaration):
            return self.visit_variable_declaration(node)
        if isinstance(node, AstDefinition):
            return self.visit_definition(node)

    def visit_operation(self, node: AstOperation):
        pass

    def visit_number(self, node: AstNumber):
        pass

    def visit_block(self, node: AstBlock):
        pass

    def visit_interrupt(self, node: AstInterrupt):
        pass

    def visit_symbol(self, node: AstSymbol):
        pass

    def visit_literal(self, node: AstLiteral):
        pass

    def visit_if_statement(self, node: AstIfStatement):
        pass

    def visit_while_statement(self, node: AstWhileStatement):
        pass

    def visit_variable_declaration(self, node: AstVariableDeclaration):
        pass

    def visit_definition(self, node: AstDefinition):
        pass
