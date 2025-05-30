from __future__ import annotations

from src.constants import INSTRUCTION_MEMORY_SIZE, INTERRUPTS_HANDLER_ADDRESS
from src.isa.data import Data
from src.isa.instructions.instruction import Instruction
from src.isa.memory_config import DATA_AREA_START_ADDR
from src.isa.opcode_ import Opcode
from src.translator.ast_.ast_ import (
    Ast,
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
from src.translator.ast_.ast_node_visitor import AstNodeVisitor
from src.translator.code_generator.instruction_producers import (
    if_instructions_producer,
    operation_instructions_producer,
    push_extended_number_instructions_producer,
    push_number_instructions_producer,
    symbol_instructions_producer,
    while_instructions_producer,
)


class CodeGenerator(AstNodeVisitor):
    """Переводит AST-дерево в набор инструкций для процессора

    Также производит формирование массива данных, выделяя место под
    переменные и заполняя строковые литералы
    """

    tree = None
    "AST-дерево, c программой"

    symbol_table = None
    "Таблица символов"

    literals = None
    "Массив литералов"

    data = None
    """Массив данных.

    Инициализируется пустым.

    B процессе трансляции в него записываются переменные и строковые литералы
    """

    instructions = None
    "Массив инструкций. Инициализируется пустым"

    interrupts = None
    "Массив инструкций для обработчика прерываний. Инициализируется пустым"

    def __init__(self, tree: Ast, symbol_table: dict[str, int], literals: list[str]):
        self.tree = tree
        self.symbol_table = symbol_table
        self.literals = literals
        self.data: list[Data] = []
        self.instructions: list[Instruction] = []
        self.interrupts: list[Instruction] = []
        self.interrupt_handler_address = 0
        self.is_interrupts_enabled = False

    @staticmethod
    def do_link_instructions(instructions: list[Instruction], start_address: int, instruction_memory_size: int):
        """Проставляет адреса инструкций"""

        instruction_address = start_address

        for i in range(len(instructions)):
            assert instruction_address < instruction_memory_size, "Too many instructions"

            instructions[i].address = instruction_address
            instruction_address += 1

    @staticmethod
    def do_link_data(data: list[Data], start_address: int):
        """Проставляет адреса данных"""

        data_start_address = start_address

        for i in range(len(data)):
            data[i].address = data_start_address
            data_start_address += 1

    def translate(self) -> (list[Instruction], list[Data]):
        """Основная функция трансляции

        Выполняет следующие операции:

        - Получает массив инструкций и добавляет `HALT` в конец

        - Если в программе был блок обработки прерываний то устанавливается флаг наличия прерываний,
          записывается адрес обработчика прерываний и блок обработчика дописывается в основного конец массива инструкций
        """

        self.instructions = self.visit(self.tree)
        self.instructions.append(Instruction(Opcode.HALT))

        assert len(self.instructions) < INTERRUPTS_HANDLER_ADDRESS, "Main instructions overlap interrupts block"

        self.do_link_instructions(self.instructions, 0, INSTRUCTION_MEMORY_SIZE)
        self.do_link_instructions(self.interrupts, INTERRUPTS_HANDLER_ADDRESS, INSTRUCTION_MEMORY_SIZE)
        self.do_link_data(self.data, DATA_AREA_START_ADDR)

        return self.instructions + self.interrupts, self.data

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
        """Парсит блок в массив `interrupts` и дописывает инструкцию `RINT` в конец"""

        self.interrupts += self.visit_block(node.block)
        self.interrupts.append(Instruction(Opcode.RINT))
        return []

    def visit_symbol(self, node: AstSymbol) -> list[Instruction]:
        symbol_address = self.symbol_table[node.name]
        return symbol_instructions_producer(symbol_address)

    def visit_literal(self, node: AstLiteral) -> list[Instruction]:
        """Загружает значение из массива литералов, и записывает его в `data` в виде паскаль-строки"""
        value = self.literals[node.value_id]
        self.data.append(Data(len(value)))
        for c in value:
            self.data.append(Data(ord(c)))
        return []

    def visit_variable_declaration(self, node: AstVariableDeclaration) -> list[Instruction]:
        """Рассчитывает адрес переменной, записывает его в таблицу символов и добавляет ячейку в `data`"""

        address = DATA_AREA_START_ADDR + len(self.data)
        self.symbol_table[node.name] = address
        self.data.append(Data())
        return []

    def visit_d_variable_declaration(self, node: AstDVariableDeclaration) -> list[Instruction]:
        """Рассчитывает адрес переменной, записывает его в таблицу символов и добавляет две ячейки в `data`"""

        address = DATA_AREA_START_ADDR + len(self.data)
        self.symbol_table[node.name] = address
        self.data += [Data()] * 2
        return []

    def visit_string_declaration(self, node: AstStringDeclaration) -> list[Instruction]:
        """Рассчитывает адрес переменной, записывает его в таблицу символов и добавляет строку в `data`"""

        address = DATA_AREA_START_ADDR + len(self.data)
        self.symbol_table[node.name] = address
        self.visit(node.literal)
        return []

    def visit_memory_block_declaration(self, node: AstMemoryBlockDeclaration) -> list[Instruction]:
        """Рассчитывает адрес переменной, записывает его в таблицу символов и добавляет `size` количество ячеек в `data`"""

        address = DATA_AREA_START_ADDR + len(self.data)
        self.symbol_table[node.name] = address
        self.data += [Data()] * node.size
        return []

    def visit_if_statement(self, node: AstIfStatement) -> list[Instruction]:
        if_block_instructions = self.visit(node.if_block)
        else_block_instructions = [] if node.else_block is None else self.visit(node.else_block)
        return if_instructions_producer(if_block_instructions, else_block_instructions)

    def visit_while_statement(self, node: AstWhileStatement) -> list[Instruction]:
        while_block_instructions = self.visit(node.while_block)
        return while_instructions_producer(while_block_instructions)
