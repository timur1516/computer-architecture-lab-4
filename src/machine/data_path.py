from __future__ import annotations

import logging

from src.constants import MAX_NUMBER, MIN_NUMBER, WORD_SIZE
from src.isa.data import Data
from src.isa.memory_config import INPUT_ADDRESS, OUTPUT_ADDRESS
from src.isa.opcode_ import Opcode
from src.isa.register import Register
from src.isa.util.binary import binary_to_signed_int
from src.machine.exceptions.exceptions import (
    EmptyInputBufferError,
    ReadingFromOutputAddressError,
    WritingToInputAddressError,
)
from src.machine.util import int_list_to_str, int_to_char

ALU_OPCODE_OPERATORS = {
    Opcode.ADD: lambda left, right: left + right,
    Opcode.ADC: lambda left, right: (((left & ((1 << WORD_SIZE) - 1)) + (right & ((1 << WORD_SIZE) - 1))) >> WORD_SIZE)
    & 1,
    Opcode.SUB: lambda left, right: left - right,
    Opcode.MUL: lambda left, right: left * right,
    Opcode.MULH: lambda left, right: (left * right) >> WORD_SIZE,
    Opcode.DIV: lambda left, right: left // right,
    Opcode.REM: lambda left, right: left % right,
    Opcode.SLL: lambda left, right: left << right,
    Opcode.SRL: lambda left, right: left >> right,
    Opcode.AND: lambda left, right: left & right,
    Opcode.OR: lambda left, right: left | right,
    Opcode.XOR: lambda left, right: left ^ right,
}
"Вспомогательный словарь для хранения lambda-выражение операций alu"


class DataPath:
    """Тракт данных (пассивный), включая: ввод/вывод, память и арифметику."""

    data_memory_size = None
    "Размер памяти данных."

    data_memory = None
    "Память данных. Инициализируется нулевыми значениями."

    data_address = None
    "Адрес в памяти данных. Инициализируется нулём."

    input_buffer = None
    "Буфер входных данных."

    output_buffer = None
    "Буфер выходных данных."

    registers_file = None
    "Основной набор регистров процессора"

    shadow_register_file = None
    "Дополнительный набор регистров процессора. Нужен для сохранения значений регистров при прерываниях"

    zero_flag = None
    "Флаг нуля. Инициализируется значением `False`"

    negative_flag = None
    "Флаг отрицательного значения. Инициализируется значением `False`"

    overflow_flag = None
    "Флаг переполнения. Инициализируется значением `False`"

    def __init__(self, data_memory_size: int, data: list[Data]):
        self.data_memory_size = data_memory_size
        self.data_memory: list[Data] = [Data()] * data_memory_size
        self.init_data_memory(data)
        self.data_address = 0

        self.input_buffer = []
        self.output_buffer = []

        self.registers_file = {r: 0 for r in Register}
        self.registers_file[Register.SP] = self.data_memory_size

        self.shadow_register_file = {r: 0 for r in Register if r is not Register.ZERO}

        self.zero_flag = False
        self.negative_flag = False
        self.overflow_flag = False

    def init_data_memory(self, data: list[Data]):
        """Выполняет заполнение памяти данных входными значениями"""

        for element in data:
            assert 0 <= element.address <= self.data_memory_size, "data memory overflow"
            self.data_memory[element.address] = element

    def signal_latch_data_address(self, address: int):
        """Защёлкнуть адрес в памяти данных"""

        assert 0 <= address < self.data_memory_size, "out of memory: {}".format(address)

        self.data_address = address

    def signal_store_registers(self):
        """Защёлкнуть резервный блок регистров"""

        self.shadow_register_file = {r: self.registers_file[r] for r in Register if r is not Register.ZERO}

    def signal_restore_registers(self):
        """Защёлкнуть основной блок регистров"""
        self.registers_file.update(self.shadow_register_file)

    def signal_data_memory_store(self, data_in: int):
        """Записать значение `data_in` в память.

        Адрес должен быть предварительно задан в `data_address`

        В случае если адрес установлен на устройство вывода, выполняется запись значения в буфер вывода
        """

        if self.data_address == INPUT_ADDRESS:
            raise WritingToInputAddressError()
        if self.data_address == OUTPUT_ADDRESS:
            logging.debug(
                'output: "%s" << "%s" | %s << %s',
                int_list_to_str(self.output_buffer),
                int_to_char(data_in),
                self.output_buffer,
                data_in,
            )
            self.output_buffer.append(data_in)
        else:
            self.data_memory[self.data_address] = Data(data_in, self.data_address)

    def signal_data_memory_load(self) -> int:
        """Чтение значение из памяти.

        Адрес должен быть предварительно задан в `data_address`

        В случае если адрес установлен на устройство ввода, выполняется чтение значения из буфера ввода
        """

        if self.data_address == OUTPUT_ADDRESS:
            raise ReadingFromOutputAddressError()
        if self.data_address == INPUT_ADDRESS:
            if len(self.input_buffer) == 0:
                raise EmptyInputBufferError()
            data_out = self.input_buffer.pop()
            logging.debug('input: "%s" | %s', int_to_char(data_out), data_out)

        else:
            data_out = self.data_memory[self.data_address].value
        return data_out

    def signal_perform_alu_operation_reg_reg(self, rs1: Register, rs2: Register, opcode: Opcode):
        """Выполнение операции АЛУ с операндами из регистров"""

        return self._perform_alu_operation(self.registers_file[rs1], self.registers_file[rs2], opcode)

    def signal_perform_alu_operation_reg_imm(self, rs1: Register, imm: int, opcode: Opcode):
        """Выполнение операции АЛУ с операндами из регистра и непосредственного значения"""

        return self._perform_alu_operation(self.registers_file[rs1], imm, opcode)

    def signal_perform_alu_operation_reg_u_imm(self, rs1: Register, imm: int, opcode: Opcode):
        """Выполнение операции АЛУ с операндами из регистра и расширенного непосредственного значения"""

        return self._perform_alu_operation(self.registers_file[rs1], imm << 8, opcode)

    def signal_perform_alu_operation_pc_imm(self, pc: int, imm: int, opcode: Opcode):
        """Выполнение операции АЛУ со значением счётчика команд и непосредственного значения"""

        return self._perform_alu_operation(pc, imm, opcode)

    def signal_write_to_reg(self, rd: Register, value: int):
        """Метод для записи значения в регистр

        Если запись происходит в регистр `ZERO`, то его значение не изменяется
        """

        if rd is not Register.ZERO:
            self.registers_file[rd] = value

    def _perform_alu_operation(self, op1: int, op2: int, opcode: Opcode) -> int:
        """Вспомогательный внутренний метода для выполнения операции АЛУ

        Нужен чтобы не зависеть от источника операндов

        Выполняет установку флагов
        """

        assert opcode in ALU_OPCODE_OPERATORS, "unknown alu opcode: {}".format(opcode)

        result_val = ALU_OPCODE_OPERATORS[opcode](op1, op2)

        self.zero_flag = result_val == 0
        self.negative_flag = result_val < 0

        if not MIN_NUMBER <= result_val <= MAX_NUMBER:
            self.overflow_flag = True
            result_val = binary_to_signed_int(result_val, WORD_SIZE)
        else:
            self.overflow_flag = False

        return result_val
