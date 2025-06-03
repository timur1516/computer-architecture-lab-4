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
    branch_stub_instructions_producer,
    if_instructions_producer,
    jump_stub_instructions_producer,
    label_stub_instructions_producer,
    operation_instructions_producer,
    push_extended_number_instructions_producer,
    push_number_instructions_producer,
    symbol_instructions_producer,
    while_instructions_producer,
)
from src.translator.code_generator.stubs import BranchStub, JumpStub, LabelStub, Stub


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

    @staticmethod
    def link(items: list[Instruction | Data], start_address: int):
        """Проставляет адреса инструкций или данных"""

        address = start_address
        for item in items:
            item.address = address
            if not isinstance(item, LabelStub):
                address += 1

    @staticmethod
    def shift_instructions(shift: int, instructions: list[Instruction]):
        """Выполняет сдвиг адресов инструкций на определенное значение `shift`"""

        for instr in instructions:
            instr.address += shift

    @staticmethod
    def get_stub_replace(stub) -> list[Instruction]:
        if isinstance(stub, LabelStub):
            return label_stub_instructions_producer(stub)
        if isinstance(stub, BranchStub):
            return branch_stub_instructions_producer(stub)
        if isinstance(stub, JumpStub):
            return jump_stub_instructions_producer(stub)
        raise NotImplementedError()

    def resolve_branches(self, instructions: list[Instruction]) -> list[Instruction]:
        """Разрешает переходы, удаляя заглушки меток и заменяя заглушки переходов на реальные инструкции

        В начале происходит вычисление итогового размера каждого перехода, что сопровождается сдвигом адресов инструкций

        После чего происходит сама замена заглушек на блоки инструкций
        """

        is_shift_finished = False
        while not is_shift_finished:
            is_shift_finished = True
            for i, instr in enumerate(instructions):
                if isinstance(instr, Stub):
                    replace = self.get_stub_replace(instr)
                    if instr.size != len(replace):
                        is_shift_finished = False
                        self.shift_instructions(len(replace) - instr.size, instructions[i + 1 :])
                        instr.size = len(replace)
                        break

        result = []
        for i, instr in enumerate(instructions):
            if isinstance(instr, Stub):
                replace = self.get_stub_replace(instr)
                self.link(replace, instr.address)
                result += replace
            else:
                result.append(instr)

        return result

    def translate(self) -> (list[Instruction], list[Data]):
        """Основная функция трансляции

        Выполняет следующие операции:

        - Получает массив инструкций и добавляет `HALT` в конец

        - Если в программе был блок обработки прерываний то устанавливается флаг наличия прерываний,
          записывается адрес обработчика прерываний и блок обработчика дописывается в основного конец массива инструкций

        - Далее выполняется простановка адресов инструкций и данных

        - После чего выполняется заменя заглушек инструкций переходов
        """

        self.instructions = self.visit(self.tree)
        self.instructions.append(Instruction(Opcode.HALT))

        self.link(self.instructions, 0)
        self.instructions = self.resolve_branches(self.instructions)
        assert (
            max([instr.address for instr in self.instructions]) < INTERRUPTS_HANDLER_ADDRESS
        ), "Main instructions overlap interrupts block"

        self.link(self.interrupts, INTERRUPTS_HANDLER_ADDRESS)
        self.interrupts = self.resolve_branches(self.interrupts)

        self.link(self.data, DATA_AREA_START_ADDR)

        program = self.instructions + self.interrupts
        assert max([instr.address for instr in program]) < INSTRUCTION_MEMORY_SIZE, "Too many instructions"

        return program, self.data

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
