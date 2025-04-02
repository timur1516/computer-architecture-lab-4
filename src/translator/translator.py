import os
import sys
from typing import List

from src.isa.isa import Instruction, RInstruction, SInstruction, Register, Opcode, IInstruction, BInstruction
from src.isa.isa import to_bytes, to_hex, write_json
from src.isa.memory_config import DATA_AREA_START_ADDR, INPUT_ADDRESS, OUTPUT_ADDRESS
from src.translator.ast.ast_node_visitor import AstBlock, AstNumber, AstOperation, AstSymbol, AstIfStatement, \
    AstWhileStatement, AstVariableDeclaration, AstDefinition, Ast, AstNodeVisitor
from src.translator.ast.ast_printer import AstPrinter
from src.translator.lexer import Lexer
from src.translator.parser import Parser
from src.translator.token.token_type import TokenType

OPERATION_TRANSLATION = {
    TokenType.PLUS: [
        SInstruction(Opcode.LW, Register.T0, Register.SP, None),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        SInstruction(Opcode.LW, Register.T1, Register.SP, None),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        RInstruction(Opcode.ADD, Register.T0, Register.T1, Register.T0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
        SInstruction(Opcode.SW, None, Register.SP, Register.T0)
    ],
    TokenType.PRINT: [
        SInstruction(Opcode.LW, Register.T0, Register.SP, None),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        IInstruction(Opcode.ADDI, Register.T1, Register.ZERO, OUTPUT_ADDRESS),
        SInstruction(Opcode.SW, None, Register.T1, Register.T0)
    ],
    TokenType.READ: [
        IInstruction(Opcode.ADDI, Register.T1, Register.ZERO, INPUT_ADDRESS),
        SInstruction(Opcode.LW, Register.T0, Register.T1, None),
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
        symbol_address = DATA_AREA_START_ADDR + self.symbol_table.index(node.name)
        return [
            IInstruction(Opcode.ADDI, Register.T0, Register.ZERO, symbol_address),
            IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
            SInstruction(Opcode.SW, None, Register.SP, Register.T0)
        ]

    def visit_if_statement(self, node: AstIfStatement) -> List[Instruction]:
        if_block_instructions = self.visit(node.if_block)
        else_block_instructions = [] if node.else_block is None else self.visit(node.else_block)

        branch_logic_instructions = [
            SInstruction(Opcode.LW, Register.T0, Register.SP, None),
            IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
            BInstruction(Opcode.BEQ, Register.T0, Register.ZERO, len(if_block_instructions) + 1)
        ]

        return branch_logic_instructions + if_block_instructions + else_block_instructions

    def visit_while_statement(self, node: AstWhileStatement) -> List[Instruction]:
        while_block_instructions = self.visit(node.while_block)

        while_logic_instructions = [
            SInstruction(Opcode.LW, Register.T0, Register.SP, None),
            IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
            BInstruction(Opcode.BEQ, Register.T0, Register.ZERO, -len(while_block_instructions))
        ]

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


def main(source: str, target: str):
    with open(source, encoding="utf-8") as f:
        source = f.read()

    code = translate(source)
    binary_code = to_bytes(code)
    hex_code = to_hex(code)

    os.makedirs(os.path.dirname(os.path.abspath(target)) or ".", exist_ok=True)

    if target.endswith(".bin"):
        with open(target, "wb") as f:
            f.write(binary_code)
        with open(target + ".hex", "w") as f:
            f.write(hex_code)
    else:
        write_json(target, code)

    print("source LoC:", len(source.split("\n")), "code instr:", len(code))


if __name__ == '__main__':
    assert len(sys.argv) == 3, "Wrong arguments: translator.py <input_file> <target_file>"
    _, source, target = sys.argv
    main(source, target)
