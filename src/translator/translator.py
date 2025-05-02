from __future__ import annotations

import os
import sys

from src.isa.instructions.instruction import Instruction
from src.isa.memory_config import DATA_AREA_START_ADDR
from src.isa.opcode_ import Opcode
from src.isa.util.data_translators import to_bytes, to_hex, write_json
from src.translator.ast.__ast import (
    AstDVariableDeclaration,
    AstExtendedNumber,
    AstInterrupt,
    AstLiteral,
    AstMemoryBlockDeclaration,
    AstStringDeclaration,
)
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
from src.translator.traslator_instruction_producers import (
    if_instructions_producer,
    operation_instructions_producer,
    push_extended_number_instructions_producer,
    push_number_instructions_producer,
    symbol_instructions_producer,
    while_instructions_producer,
)


class Translator(AstNodeVisitor):
    tree = None
    symbol_table = None
    literals = None
    data = None
    instructions = None
    interrupts = None
    interrupt_handler_address = None
    is_interrupts_enabled = None

    def __init__(self, tree: Ast, symbol_table: dict, literals: list[str]):
        self.tree = tree
        self.symbol_table = symbol_table
        self.literals = literals
        self.data = []
        self.instructions = []
        self.interrupts = []
        self.interrupt_handler_address = 0
        self.is_interrupts_enabled = False

    def translate(self) -> list[Instruction]:
        self.instructions = self.visit(self.tree)
        self.instructions.append(Instruction(Opcode.HALT))

        if len(self.interrupts) > 0:
            self.is_interrupts_enabled = True
            self.interrupt_handler_address = len(self.instructions)
            self.instructions += self.interrupts

        return self.instructions

    def visit_operation(self, node: AstOperation) -> list[Instruction]:
        return operation_instructions_producer(node.token_type)

    def visit_number(self, node: AstNumber) -> list[Instruction]:
        return push_number_instructions_producer(node.value)

    def visit_extended_number(self, node: AstExtendedNumber) -> list[Instruction]:
        return push_extended_number_instructions_producer(node.value)

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
        symbol_address = self.symbol_table[node.name]
        return symbol_instructions_producer(symbol_address)

    def visit_literal(self, node: AstLiteral) -> list[Instruction]:
        value = self.literals[node.value_id]
        self.data.append(len(value))
        for c in value:
            self.data.append(ord(c))
        return []

    def visit_variable_declaration(self, node: AstVariableDeclaration) -> list[Instruction]:
        address = DATA_AREA_START_ADDR + len(self.data)
        self.symbol_table[node.name] = address
        self.data.append(0)
        return []

    def visit_d_variable_declaration(self, node: AstDVariableDeclaration) -> list[Instruction]:
        address = DATA_AREA_START_ADDR + len(self.data)
        self.symbol_table[node.name] = address
        self.data += [0] * 2
        return []

    def visit_string_declaration(self, node: AstStringDeclaration) -> list[Instruction]:
        address = DATA_AREA_START_ADDR + len(self.data)
        self.symbol_table[node.name] = address
        self.visit(node.literal)
        return []

    def visit_memory_block_declaration(self, node: AstMemoryBlockDeclaration) -> list[Instruction]:
        address = DATA_AREA_START_ADDR + len(self.data)
        self.symbol_table[node.name] = address
        self.data += [0] * node.size
        return []

    def visit_if_statement(self, node: AstIfStatement) -> list[Instruction]:
        if_block_instructions = self.visit(node.if_block)
        else_block_instructions = [] if node.else_block is None else self.visit(node.else_block)
        return if_instructions_producer(if_block_instructions, else_block_instructions)

    def visit_while_statement(self, node: AstWhileStatement) -> list[Instruction]:
        while_block_instructions = self.visit(node.while_block)
        return while_instructions_producer(while_block_instructions)

    def visit_definition(self, node: AstDefinition) -> list[Instruction]:
        return []


def translate(text: str) -> (list[Instruction], list[int], list[int], bool):
    ast_printer = AstPrinter()
    parser = Parser(Lexer(text))

    tree = parser.parse()
    ast_printer.print(tree)
    print(f"SYMBOL TABLE: {parser.symbol_table}")
    print(f"LITERALS: {parser.literals}")

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
