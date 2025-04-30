from __future__ import annotations

import logging

from src.constants import MAX_NUMBER, MIN_NUMBER
from src.isa.memory_config import DATA_AREA_START_ADDR, INPUT_ADDRESS, OUTPUT_ADDRESS
from src.isa.opcode_ import Opcode
from src.isa.register import Register
from src.machine.exceptions.exceptions import (
    EmptyInputBufferError,
    ReadingFromOutputAddressError,
    WritingToInputAddressError,
)

ALU_OPCODE_OPERATORS = {
    Opcode.ADD: lambda left, right: left + right,
    Opcode.SUB: lambda left, right: left - right,
    Opcode.MUL: lambda left, right: left * right,
    Opcode.DIV: lambda left, right: left // right,
    Opcode.REM: lambda left, right: left % right,
    Opcode.SLL: lambda left, right: left << right,
    Opcode.SRL: lambda left, right: left >> right,
    Opcode.AND: lambda left, right: left & right,
    Opcode.OR: lambda left, right: left | right,
    Opcode.XOR: lambda left, right: left ^ right,
}


class DataPath:
    data_memory_size = None

    data_memory = None

    data_address = None

    input_buffer = None

    output_buffer = None

    registers_file: dict[Register, int]

    shadow_register_file: dict[Register, int]

    zero_flag = None

    negative_flag = None

    overflow_flag = None

    carry_flag = None

    def __init__(self, data_memory_size: int, init_data_memory: list[int]) -> None:
        self.data_memory_size = data_memory_size
        self.data_memory = (
            [0] * DATA_AREA_START_ADDR + init_data_memory + [0] * (data_memory_size - len(init_data_memory))
        )
        self.data_address = 0

        self.input_buffer = ""
        self.output_buffer = []

        self.registers_file = {r: 0 for r in Register}
        self.registers_file[Register.SP] = self.data_memory_size

        self.shadow_register_file = {r: 0 for r in Register if r is not Register.ZERO}

        self.zero_flag = False
        self.negative_flag = False
        self.overflow_flag = False

    def signal_latch_data_address(self, rs1: Register):
        self.data_address = self.registers_file[rs1]

        assert 0 <= self.data_address < self.data_memory_size, "out of memory: {}".format(self.data_address)

    def signal_store_registers(self):
        self.shadow_register_file = {r: self.registers_file[r] for r in Register if r is not Register.ZERO}

    def signal_restore_registers(self):
        self.registers_file.update(self.shadow_register_file)

    def signal_data_memory_store(self, rs2: Register):
        if self.data_address == INPUT_ADDRESS:
            raise WritingToInputAddressError()
        if self.data_address == OUTPUT_ADDRESS:
            symbol = chr(self.registers_file[rs2])
            logging.debug("output: %s << %s", repr("".join(self.output_buffer)), repr(symbol))
            self.output_buffer.append(symbol)
        else:
            self.data_memory[self.data_address] = self.registers_file[rs2]

    def signal_data_memory_load(self, rd: Register):
        if self.data_address == OUTPUT_ADDRESS:
            raise ReadingFromOutputAddressError()
        if self.data_address == INPUT_ADDRESS:
            if self.input_buffer == "":
                raise EmptyInputBufferError()
            value = ord(self.input_buffer)
            logging.debug("input: %s", repr(value))

        else:
            value = self.data_memory[self.data_address]
        self._write_to_reg(rd, value)

    def signal_perform_alu_operation_reg(self, rs1: Register, rs2: Register, rd: Register, opcode: Opcode):
        result_val = self._perform_alu_operation(self.registers_file[rs1], self.registers_file[rs2], opcode)
        self._write_to_reg(rd, result_val)

    def signal_perform_alu_operation_imm(self, imm: int, rs2: Register, rd: Register, opcode: Opcode):
        result_val = self._perform_alu_operation(imm, self.registers_file[rs2], opcode)
        self._write_to_reg(rd, result_val)

    def signal_perform_alu_operation_u_imm(self, imm: int, rs2: Register, rd: Register, opcode: Opcode):
        self.signal_perform_alu_operation_imm(imm << 12, rs2, rd, opcode)

    def signal_store_pc(self, old_pc: int, rd: Register):
        self._write_to_reg(rd, old_pc)

    def signal_next_pc_imm(self, pc: int, imm: int) -> int:
        return self._perform_alu_operation(imm, pc, Opcode.ADD)

    def signal_next_pc_reg(self, imm: int, rs2: Register) -> int:
        return self._perform_alu_operation(imm, self.registers_file[rs2], Opcode.ADD)

    def _write_to_reg(self, rd: Register, value: int):
        if rd is not Register.ZERO:
            self.registers_file[rd] = value

    def _perform_alu_operation(self, op1: int, op2: int, opcode: Opcode) -> int:
        assert opcode in ALU_OPCODE_OPERATORS, "unknown alu opcode: {}".format(opcode)

        result_val = ALU_OPCODE_OPERATORS[opcode](op1, op2)

        self.zero_flag = result_val == 0
        self.negative_flag = result_val < 0

        if result_val > MAX_NUMBER:
            self.overflow_flag = True
            result_val %= MAX_NUMBER
        elif result_val < MIN_NUMBER:
            self.overflow_flag = True
            result_val %= abs(MIN_NUMBER)
        else:
            self.overflow_flag = False

        return result_val
