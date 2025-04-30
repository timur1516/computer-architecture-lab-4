from __future__ import annotations

import os
import sys

from src.isa.instructions.b_instruction import BInstruction
from src.isa.instructions.i_instruction import IInstruction
from src.isa.instructions.instruction import Instruction
from src.isa.instructions.j_instruction import JInstruction
from src.isa.instructions.r_instruction import RInstruction
from src.isa.instructions.s_instruction import SInstruction
from src.isa.instructions.u_instruction import UInstruction
from src.isa.memory_config import DATA_AREA_START_ADDR, INPUT_ADDRESS, OUTPUT_ADDRESS
from src.isa.opcode_ import Opcode
from src.isa.register import Register
from src.isa.util.binary import extract_bits, is_correct_bin_size_signed
from src.isa.util.data_translators import to_bytes, to_hex, write_json
from src.translator.ast.__ast import AstInterrupt, AstLiteral
from src.translator.ast.ast_node_visitor import (
    Ast,
    AstBlock,
    AstDefinition,
    AstIfStatement,
    AstNodeVisitor,
    AstNumber,
    AstOperation,
    AstSymbol,
    AstVariableDeclaration,
    AstWhileStatement,
)
from src.translator.ast.ast_printer import AstPrinter
from src.translator.lexer import Lexer
from src.translator.parser import Parser
from src.translator.token.token_type import TokenType

OPERATION_TRANSLATION = {
    TokenType.PLUS: [
        IInstruction(Opcode.LW, Register.T0, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        IInstruction(Opcode.LW, Register.T1, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        RInstruction(Opcode.ADD, Register.T0, Register.T1, Register.T0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
        SInstruction(Opcode.SW, Register.SP, Register.T0),
    ],
    TokenType.MINUS: [
        IInstruction(Opcode.LW, Register.T0, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        IInstruction(Opcode.LW, Register.T1, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        RInstruction(Opcode.SUB, Register.T0, Register.T1, Register.T0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
        SInstruction(Opcode.SW, Register.SP, Register.T0),
    ],
    TokenType.MUL: [
        IInstruction(Opcode.LW, Register.T0, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        IInstruction(Opcode.LW, Register.T1, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        RInstruction(Opcode.MUL, Register.T0, Register.T1, Register.T0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
        SInstruction(Opcode.SW, Register.SP, Register.T0),
    ],
    TokenType.DIV: [
        IInstruction(Opcode.LW, Register.T0, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        IInstruction(Opcode.LW, Register.T1, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        RInstruction(Opcode.DIV, Register.T0, Register.T1, Register.T0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
        SInstruction(Opcode.SW, Register.SP, Register.T0),
    ],
    TokenType.DUP: [
        IInstruction(Opcode.LW, Register.T0, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
        SInstruction(Opcode.SW, Register.SP, Register.T0),
    ],
    TokenType.DROP: [IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1)],
    TokenType.SWAP: [
        IInstruction(Opcode.LW, Register.T0, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        IInstruction(Opcode.LW, Register.T1, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
        SInstruction(Opcode.SW, Register.SP, Register.T0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
        SInstruction(Opcode.SW, Register.SP, Register.T1),
    ],
    TokenType.EQUALS: [
        IInstruction(Opcode.LW, Register.T0, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        IInstruction(Opcode.LW, Register.T1, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        BInstruction(Opcode.BEQ, Register.T0, Register.T1, 3),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 0),
        JInstruction(Opcode.J, 2),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 1),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
        SInstruction(Opcode.SW, Register.SP, Register.T3),
    ],
    TokenType.NOT_EQUALS: [
        IInstruction(Opcode.LW, Register.T0, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        IInstruction(Opcode.LW, Register.T1, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        BInstruction(Opcode.BNE, Register.T0, Register.T1, 3),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 0),
        JInstruction(Opcode.J, 2),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 1),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
        SInstruction(Opcode.SW, Register.SP, Register.T3),
    ],
    TokenType.GREATER: [
        IInstruction(Opcode.LW, Register.T1, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        IInstruction(Opcode.LW, Register.T0, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        BInstruction(Opcode.BGT, Register.T0, Register.T1, 3),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 0),
        JInstruction(Opcode.J, 2),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 1),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
        SInstruction(Opcode.SW, Register.SP, Register.T3),
    ],
    TokenType.LESS: [
        IInstruction(Opcode.LW, Register.T1, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        IInstruction(Opcode.LW, Register.T0, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        BInstruction(Opcode.BLT, Register.T0, Register.T1, 3),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 0),
        JInstruction(Opcode.J, 2),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 1),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
        SInstruction(Opcode.SW, Register.SP, Register.T3),
    ],
    TokenType.GREATER_EQUAL: [
        IInstruction(Opcode.LW, Register.T1, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        IInstruction(Opcode.LW, Register.T0, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        BInstruction(Opcode.BGT, Register.T0, Register.T1, 4),
        BInstruction(Opcode.BEQ, Register.T0, Register.T1, 3),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 0),
        JInstruction(Opcode.J, 2),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 1),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
        SInstruction(Opcode.SW, Register.SP, Register.T3),
    ],
    TokenType.LESS_EQUAL: [
        IInstruction(Opcode.LW, Register.T1, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        IInstruction(Opcode.LW, Register.T0, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        BInstruction(Opcode.BLT, Register.T0, Register.T1, 4),
        BInstruction(Opcode.BEQ, Register.T0, Register.T1, 3),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 0),
        JInstruction(Opcode.J, 2),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 1),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
        SInstruction(Opcode.SW, Register.SP, Register.T3),
    ],
    TokenType.PRINT: [
        IInstruction(Opcode.LW, Register.T0, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        IInstruction(Opcode.ADDI, Register.T1, Register.ZERO, OUTPUT_ADDRESS),
        SInstruction(Opcode.SW, Register.T1, Register.T0),
    ],
    TokenType.READ: [
        IInstruction(Opcode.ADDI, Register.T1, Register.ZERO, INPUT_ADDRESS),
        IInstruction(Opcode.LW, Register.T0, Register.T1, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
        SInstruction(Opcode.SW, Register.SP, Register.T0),
    ],
    TokenType.STORE: [
        IInstruction(Opcode.LW, Register.T0, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        IInstruction(Opcode.LW, Register.T1, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        SInstruction(Opcode.SW, Register.T1, Register.T0),
    ],
    TokenType.LOAD: [
        IInstruction(Opcode.LW, Register.T0, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        IInstruction(Opcode.LW, Register.T0, Register.T0, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
        SInstruction(Opcode.SW, Register.SP, Register.T0),
    ],
}


class Translator(AstNodeVisitor):
    tree = None
    symbol_table = None
    literals = None
    data = None
    instructions = None
    interrupts = None
    interrupt_handler_address = None
    is_interrupts_enabled = None

    def __init__(self, tree: Ast, symbol_table: list[str], literals: list[str]):
        self.tree = tree
        self.symbol_table = symbol_table
        self.literals = literals
        self.data = [0] * len(symbol_table)
        self.instructions = []
        self.interrupts = []
        self.interrupt_handler_address = 0
        self.is_interrupts_enabled = False

    def translate(self):
        self.instructions = self.visit(self.tree)
        self.instructions.append(Instruction(Opcode.HALT))

        if len(self.interrupts) > 0:
            self.is_interrupts_enabled = True
            self.interrupt_handler_address = len(self.instructions)
            self.instructions += self.interrupts

        return self.instructions

    def visit_operation(self, node: AstOperation) -> list[Instruction]:
        assert node.token_type in OPERATION_TRANSLATION, "unsupported operation"

        return OPERATION_TRANSLATION[node.token_type]

    def visit_number(self, node: AstNumber) -> list[Instruction]:
        value = node.value
        if is_correct_bin_size_signed(value, 12):
            return [
                IInstruction(Opcode.ADDI, Register.T0, Register.ZERO, node.value),
                IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
                SInstruction(Opcode.SW, Register.SP, Register.T0),
            ]
        lower_value = extract_bits(value, 12)
        upper_value = value >> 12
        return [
            UInstruction(Opcode.LUI, Register.T0, upper_value),
            IInstruction(Opcode.ADDI, Register.T0, Register.T0, lower_value),
            IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
            SInstruction(Opcode.SW, Register.SP, Register.T0),
        ]

    def visit_block(self, node: AstBlock) -> list[Instruction]:
        result = []

        for block in node.children:
            result += self.visit(block)

        return result

    def visit_interrupt(self, node: AstInterrupt) -> list[Instruction]:
        self.interrupts += self.visit_block(node.block)
        self.interrupts.append(Instruction(Opcode.RINT))
        return []

    def visit_symbol(self, node: AstSymbol) -> list[Instruction]:
        symbol_address = DATA_AREA_START_ADDR + self.symbol_table.index(node.name)
        return [
            IInstruction(Opcode.ADDI, Register.T0, Register.ZERO, symbol_address),
            IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
            SInstruction(Opcode.SW, Register.SP, Register.T0),
        ]

    def visit_literal(self, node: AstLiteral) -> list[Instruction]:
        value = self.literals[node.value_id]
        address = DATA_AREA_START_ADDR + len(self.data)

        self.data.append(len(value))
        for c in value:
            self.data.append(ord(c))

        return [
            IInstruction(Opcode.ADDI, Register.T0, Register.ZERO, address),
            IInstruction(Opcode.LW, Register.T1, Register.T0, 0),
            IInstruction(Opcode.ADDI, Register.T0, Register.T0, 1),
            IInstruction(Opcode.LW, Register.T3, Register.T0, 0),
            IInstruction(Opcode.ADDI, Register.T2, Register.ZERO, OUTPUT_ADDRESS),
            SInstruction(Opcode.SW, Register.T2, Register.T3),
            IInstruction(Opcode.ADDI, Register.T1, Register.T1, -1),
            BInstruction(Opcode.BNE, Register.T1, Register.ZERO, -5),
        ]

    def visit_if_statement(self, node: AstIfStatement) -> list[Instruction]:
        if_block_instructions = self.visit(node.if_block)
        else_block_instructions = [] if node.else_block is None else self.visit(node.else_block)

        branch_logic_instructions = [
            IInstruction(Opcode.LW, Register.T0, Register.SP, 0),
            IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
            BInstruction(Opcode.BEQ, Register.T0, Register.ZERO, len(if_block_instructions) + 2),
        ]

        return (
            branch_logic_instructions
            + if_block_instructions
            + [JInstruction(Opcode.J, len(else_block_instructions) + 1)]
            + else_block_instructions
        )

    def visit_while_statement(self, node: AstWhileStatement) -> list[Instruction]:
        while_block_instructions = self.visit(node.while_block)

        while_logic_instructions = [
            IInstruction(Opcode.LW, Register.T0, Register.SP, 0),
            BInstruction(Opcode.BNE, Register.T0, Register.ZERO, -len(while_block_instructions) - 2),
        ]

        return while_block_instructions + while_logic_instructions

    def visit_variable_declaration(self, node: AstVariableDeclaration) -> list[Instruction]:
        return []

    def visit_definition(self, node: AstDefinition) -> list[Instruction]:
        return []


def translate(text: str) -> (list[Instruction], list[int], list[int], bool):
    ast_printer = AstPrinter()
    parser = Parser(Lexer(text))

    tree = parser.parse()
    ast_printer.print(tree)
    print(parser.symbol_table)
    print(parser.literals)

    translator = Translator(tree, parser.symbol_table, parser.literals)
    program = translator.translate()

    return program, translator.data, translator.interrupt_handler_address, translator.is_interrupts_enabled


def main(source: str, target: str):
    with open(source, encoding="utf-8") as f:
        source = f.read()

    code, data, interrupt_handler_address, is_interrupts_enabled = translate(source)

    binary_code = to_bytes(code, data, is_interrupts_enabled, interrupt_handler_address)
    hex_code = to_hex(binary_code)

    os.makedirs(os.path.dirname(os.path.abspath(target)) or ".", exist_ok=True)

    if target.endswith(".bin"):
        with open(target, "wb") as f:
            f.write(binary_code)
        with open(target + ".hex", "w") as f:
            f.write(hex_code)
    else:
        write_json(target, code, data, is_interrupts_enabled, interrupt_handler_address)

    print("source LoC:", len(source.split("\n")), "code instr:", len(code))


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: translator.py <input_file> <target_file>"
    _, source, target = sys.argv
    main(source, target)
