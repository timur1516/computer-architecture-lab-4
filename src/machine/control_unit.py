from typing import List

from src.isa.isa import Instruction, Register, Opcode, UInstruction, SInstruction, IInstruction, RInstruction, \
    BInstruction
from src.machine.data_path import DataPath


class ControlUnit:
    instruction_memory = None

    data_path = None

    program_counter = None

    _tick = None

    step = None

    def __init__(self, instruction_memory: List[Instruction], data_path: DataPath):
        self.instruction_memory = instruction_memory
        self.data_path = data_path
        self.program_counter = 0
        self._tick = 0
        self.step = 0

    def tick(self):
        self._tick += 1

    def get_tick(self):
        return self._tick

    def signal_latch_pc(self, imm: int = None, rs1: Register = None):
        if imm is None and rs1 is None:
            pc_new = self.data_path.signal_update_pc_inc(self.program_counter)
        elif imm is not None and rs1 is None:
            pc_new = self.data_path.signal_update_pc_imm(self.program_counter, imm)
        elif imm is not None and rs1 is not None:
            pc_new = self.data_path.signal_update_pc_reg(imm, rs1)
        else:
            raise RuntimeError('Unexpected signal_latch_pc combination')

        self.program_counter = pc_new

        assert self.program_counter < len(
            self.instruction_memory), 'out of instruction memory: {}'.format(self.program_counter)

    def process_next_tick(self):
        instr = self.instruction_memory[self.program_counter]

        if instr.opcode is Opcode.HALT:
            raise StopIteration()

        if isinstance(instr, UInstruction):

            if instr.opcode is Opcode.LUI:
                self.data_path.signal_perform_alu_operation_u_imm(instr.u_imm, Register.ZERO, instr.rd, Opcode.ADD)
                self.signal_latch_pc()
                self.step = 0
                self.tick()
                return

            if instr.opcode is Opcode.JAL:
                if self.step == 0:
                    self.data_path.signal_store_pc_plus_1(self.program_counter, instr.rd)
                    self.step = 1
                    self.tick()
                    return
                if self.step == 1:
                    self.signal_latch_pc(instr.u_imm)
                    self.step = 0
                    self.tick()
                    return

        if isinstance(instr, SInstruction):

            if instr.opcode is Opcode.SW:
                if self.step == 0:
                    self.data_path.signal_latch_data_address(instr.rs1)
                    self.step = 1
                    self.tick()
                    return
                if self.step == 1:
                    self.data_path.signal_data_memory_store(instr.rs2)
                    self.signal_latch_pc()
                    self.step = 0
                    self.tick()
                    return

            if instr.opcode is Opcode.LW:
                if self.step == 0:
                    self.data_path.signal_latch_data_address(instr.rs1)
                    self.step = 1
                    self.tick()
                    return
                if self.step == 1:
                    self.data_path.signal_data_memory_load(instr.rd)
                    self.signal_latch_pc()
                    self.step = 0
                    self.tick()

        if isinstance(instr, IInstruction):

            if instr.opcode is Opcode.ADDI:
                self.data_path.signal_perform_alu_operation_imm(instr.imm, instr.rs1, instr.rd, Opcode.ADD)
                self.signal_latch_pc()
                self.step = 0
                self.tick()
                return

            if instr.opcode is Opcode.JALR:
                if self.step == 0:
                    self.data_path.signal_store_pc_plus_1(self.program_counter, instr.rd)
                    self.step = 1
                    self.tick()
                    return
                if self.step == 1:
                    self.signal_latch_pc(instr.imm)
                    self.step = 0
                    self.tick()
                    return

        if isinstance(instr, RInstruction):
            self.data_path.signal_perform_alu_operation_reg(instr.rs1, instr.rs2, instr.rd, instr.opcode)
            self.signal_latch_pc()
            self.step = 0
            self.tick()
            return

        if isinstance(instr, BInstruction):

            if instr.opcode is Opcode.BEQ:
                if self.step == 0:
                    self.data_path.signal_perform_alu_operation_reg(instr.rs1, instr.rs2, Register.ZERO, Opcode.SUB)
                    self.step = 1
                    self.tick()
                    return
                if self.step == 1:
                    if self.data_path.zero_flag:
                        self.signal_latch_pc(instr.imm)
                    else:
                        self.signal_latch_pc()
                    self.step = 0
                    self.tick()
                    return

            if instr.opcode is Opcode.BNE:
                if self.step == 0:
                    self.data_path.signal_perform_alu_operation_reg(instr.rs1, instr.rs2, Register.ZERO, Opcode.SUB)
                    self.step = 1
                    self.tick()
                    return
                if self.step == 1:
                    if not self.data_path.zero_flag:
                        self.signal_latch_pc(instr.imm)
                    else:
                        self.signal_latch_pc()
                    self.step = 0
                    self.tick()
                    return

    def __repr__(self):
        state_repr = "TICK: {:3} PC: {:3}/{} ADDR: {:3} MEM_OUT: {} T0: {} T1: {} T2: {} SP: {}".format(
            self._tick,
            self.program_counter,
            self.step,
            self.data_path.data_address,
            self.data_path.data_memory[self.data_path.data_address],
            self.data_path.registers[Register.T0],
            self.data_path.registers[Register.T1],
            self.data_path.registers[Register.T2],
            self.data_path.registers[Register.SP],
        )

        instr = self.instruction_memory[self.program_counter]

        return "{} \t{}".format(state_repr, instr.opcode)
