import os
import sys
from typing import List

from __ast import AstBlock, AstNumber, AstOperation, AstSymbol, AstIfStatement, AstWhileStatement, \
    AstVariableDeclaration, AstDefinition, Ast
from ast_node_visitor import AstNodeVisitor
from lexer import Lexer
from parser import Parser
from src.isa.isa import Instruction, RInstruction, SInstruction, Register, Opcode, IInstruction, BInstruction, to_hex, \
    write_json, to_bytes
from src.translator.ast_printer import AstPrinter
from token_type import TokenType

OPERATION_TRANSLATION = {
    TokenType.PLUS: [SInstruction(Opcode.LW, Register.T0, Register.SP, None),
                     IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
                     SInstruction(Opcode.LW, Register.T1, Register.SP, None),
                     IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
                     RInstruction(Opcode.ADD, Register.T0, Register.T1, Register.T0),
                     IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
                     SInstruction(Opcode.SW, None, Register.SP, Register.T0)
                     ]
}


class Translator(AstNodeVisitor):
    tree = None
    symbol_table = None

    def __init__(self, tree: Ast, symbol_table: List[str]):
        self.tree = tree
        self.symbol_table = symbol_table

    def translate(self):
        return self.visit(self.tree) + [Instruction(Opcode.HALT)]

    def visit_operation(self, node: AstOperation) -> List[Instruction]:
        assert node.token_type in OPERATION_TRANSLATION, 'unsupported operation'

        return OPERATION_TRANSLATION[node.token_type]

    def visit_number(self, node: AstNumber) -> List[Instruction]:
        return [
            IInstruction(Opcode.ADDI, Register.T0, Register.ZERO, node.value),
            IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
            SInstruction(Opcode.SW, None, Register.SP, Register.T0)
        ]

    def visit_block(self, node: AstBlock) -> List[Instruction]:
        result = []
        for block in node.children:
            result += self.visit(block)
        return result

    def visit_symbol(self, node: AstSymbol) -> List[Instruction]:
        return [
            IInstruction(Opcode.ADDI, Register.T0, Register.ZERO, self.symbol_table.index(node.name)),
            IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
            SInstruction(Opcode.SW, None, Register.SP, Register.T0)
        ]

    def visit_if_statement(self, node: AstIfStatement) -> List[Instruction]:
        if_block_instructions = self.visit(node.if_block)
        else_block_instructions = [] if node.else_block is None else self.visit(node.else_block)
        branch_logic_instructions = \
            [SInstruction(Opcode.LW, Register.T0, Register.SP, None),
             IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
             BInstruction(Opcode.BEQ, Register.T0, Register.ZERO, len(if_block_instructions) + 1)]
        return branch_logic_instructions + if_block_instructions + else_block_instructions

    def visit_while_statement(self, node: AstWhileStatement) -> List[Instruction]:
        while_block_instructions = self.visit(node.while_block)
        while_logic_instructions = \
            [SInstruction(Opcode.LW, Register.T0, Register.SP, None),
             IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
             BInstruction(Opcode.BEQ, Register.T0, Register.ZERO, -len(while_block_instructions))]
        return while_block_instructions + while_logic_instructions

    def visit_variable_declaration(self, node: AstVariableDeclaration) -> List[Instruction]:
        return []

    def visit_definition(self, node: AstDefinition) -> List[Instruction]:
        return []


def translate(text: str) -> List[Instruction]:
    ast_printer = AstPrinter()
    parser = Parser(Lexer(text))
    tree = parser.parse()
    ast_printer.print(tree)
    print(parser.symbol_table)
    translator = Translator(tree, parser.symbol_table)
    return translator.translate()


def main(_source, _target):
    with open(_source, encoding="utf-8") as f:
        _source = f.read()

    code = translate(_source)
    binary_code = to_bytes(code)
    hex_code = to_hex(code)

    os.makedirs(os.path.dirname(os.path.abspath(_target)) or ".", exist_ok=True)

    if _target.endswith(".bin"):
        with open(_target, "wb") as f:
            f.write(binary_code)
        with open(_target + ".hex", "w") as f:
            f.write(hex_code)
    else:
        write_json(_target, code)

    print("source LoC:", len(_source.split("\n")), "code instr:", len(code))


if __name__ == '__main__':
    assert len(sys.argv) == 3, "Wrong arguments: translator.py <input_file> <target_file>"
    _, source, target = sys.argv
    main(source, target)
