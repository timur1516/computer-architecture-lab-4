from src.isa.isa import Register, Opcode

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
    Opcode.XOR: lambda left, right: left ^ right
}


class DataPath:
    data_memory_size = None

    data_memory = None

    data_address = None

    registers = {r: None for r in Register}

    zero_flag = None

    negative_flag = None

    def __init__(self, data_memory_size: int) -> None:
        self.data_memory_size = data_memory_size
        self.data_memory = [0] * data_memory_size
        self.data_address = 0
        self.registers = {r: 0 for r in Register}
        self.registers[Register.SP] = self.data_memory_size
        self.zero_flag = False
        self.negative_flag = False

    def signal_latch_data_address(self, rs1: Register):
        self.data_address = self.registers[rs1]

        assert 0 <= self.data_address < self.data_memory_size, 'out of memory: {}'.format(self.data_address)

    def signal_data_memory_store(self, rs2: Register):
        self.data_memory[self.data_address] = self.registers[rs2]

    def signal_data_memory_load(self, rd: Register):
        value = self.data_memory[self.data_address]
        self._write_to_reg(rd, value)

    def signal_perform_alu_operation_reg(self, rs1: Register, rs2: Register, rd: Register, opcode: Opcode):
        result_val = self._perform_alu_operation(self.registers[rs1], self.registers[rs2], opcode)
        self._write_to_reg(rd, result_val)

    def signal_perform_alu_operation_imm(self, imm: int, rs2: Register, rd: Register, opcode: Opcode):
        result_val = self._perform_alu_operation(imm, self.registers[rs2], opcode)
        self._write_to_reg(rd, result_val)

    def signal_perform_alu_operation_u_imm(self, imm: int, rs2: Register, rd: Register, opcode: Opcode):
        self.signal_perform_alu_operation_imm(imm << 12, rs2, rd, opcode)

    def signal_store_pc_plus_1(self, old_pc: int, rd: Register):
        new_pc = old_pc + 1
        self._write_to_reg(rd, new_pc)

    def signal_update_pc_inc(self, old_pc: int) -> int:
        new_pc = old_pc + 1
        return new_pc

    def signal_update_pc_imm(self, old_pc: int, imm: int) -> int:
        new_pc = old_pc + imm
        return new_pc

    def signal_update_pc_reg(self, imm: int, rs1: Register) -> int:
        new_pc = imm + self.registers[rs1]
        return new_pc

    def _write_to_reg(self, rd: Register, value: int):
        if rd is not Register.ZERO:
            self.registers[rd] = value

    def _perform_alu_operation(self, op1: int, op2: int, opcode: Opcode) -> int:
        assert opcode in ALU_OPCODE_OPERATORS, 'unknown alu opcode: {}'.format(opcode)

        result_val = ALU_OPCODE_OPERATORS[opcode](op1, op2)

        # TODO: handle overflow

        if result_val == 0:
            self.zero_flag = True
        if result_val < 0:
            self.negative_flag = True

        return result_val
