from enum import Enum
from typing import List

from src.isa.isa import Instruction, Register, Opcode, UInstruction, SInstruction, IInstruction, RInstruction, \
    BInstruction
from src.isa.memory_config import INTERRUPT_STORE_AREA_START_ADDR, INTERRUPT_VECTORS_START_ADDR
from src.machine.data_path import DataPath


class ProcessorState(str, Enum):
    NORMAL = 'NORMAL'
    INT_ENTER = 'INT_ENTER'
    INT_BODY = 'INT_BODY'
    INT_EXIT = 'INT_EXIT'

    def __str__(self):
        return self.value


class ControlUnit:
    instruction_memory = None

    data_path = None

    program_counter = None

    input_timetable = None

    _tick = None

    step = None

    state = None

    is_interrupt_request = None

    interrupt_vector_number = None

    is_interrupts_enabled = None

    def __init__(self, instruction_memory: List[Instruction], data_path: DataPath,
                 input_timetable: List[tuple[int, chr]], is_interrupts_enabled: bool):
        self.instruction_memory = instruction_memory
        self.data_path = data_path
        self.is_interrupts_enabled = is_interrupts_enabled
        self.input_timetable = dict(input_timetable)
        self.program_counter = 0
        self._tick = 0
        self.step = 0
        self.state = ProcessorState.NORMAL
        self.is_interrupt_request = False
        self.interrupt_vector_number = 0

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
        if self._tick in self.input_timetable:
            symbol = self.input_timetable[self._tick]
            print(f'Interrupt request on tick {self._tick} with symbol "{symbol}"')
            if not self.is_interrupts_enabled:
                print('Interrupts are disabled')
            elif self.state in [ProcessorState.INT_ENTER, ProcessorState.INT_BODY]:
                print('Interrupts inside of interrupts are not supported')
            else:
                self.is_interrupt_request = True
                self.data_path.input_buffer = symbol
                self.interrupt_vector_number = 0

        if self.is_interrupt_request and self.step == 0 and self.state == ProcessorState.NORMAL:
            self.state = ProcessorState.INT_ENTER
            self.is_interrupt_request = False

        if self.state is ProcessorState.INT_ENTER:
            if self.step == 0:
                self.data_path.signal_perform_alu_operation_imm(INTERRUPT_STORE_AREA_START_ADDR, Register.ZERO,
                                                                Register.RA, Opcode.ADD)
            elif self.step == 1:
                self.data_path.signal_latch_data_address(Register.RA)
            elif self.step == 2:
                self.data_path.signal_data_memory_store(Register.T0)
            elif self.step == 3:
                self.data_path.signal_perform_alu_operation_imm(1, Register.RA, Register.RA, Opcode.ADD)
            elif self.step == 4:
                self.data_path.signal_latch_data_address(Register.RA)
            elif self.step == 5:
                self.data_path.signal_data_memory_store(Register.T1)
            elif self.step == 6:
                self.data_path.signal_perform_alu_operation_imm(1, Register.RA, Register.RA, Opcode.ADD)
            elif self.step == 7:
                self.data_path.signal_latch_data_address(Register.RA)
            elif self.step == 8:
                self.data_path.signal_data_memory_store(Register.T2)
            elif self.step == 9:
                self.data_path.signal_perform_alu_operation_imm(1, Register.RA, Register.RA, Opcode.ADD)
            elif self.step == 10:
                self.data_path.signal_latch_data_address(Register.RA)
            elif self.step == 11:
                self.data_path.signal_data_memory_store(Register.T3)
            elif self.step == 12:
                self.data_path.signal_perform_alu_operation_imm(1, Register.RA, Register.RA, Opcode.ADD)
            elif self.step == 13:
                self.data_path.signal_latch_data_address(Register.RA)
            elif self.step == 14:
                self.data_path.signal_data_memory_store(Register.SP)
            elif self.step == 15:
                self.data_path.signal_store_pc(self.program_counter, Register.RA)
            elif self.step == 16:
                self.data_path.signal_perform_alu_operation_imm(
                    INTERRUPT_VECTORS_START_ADDR + self.interrupt_vector_number,
                    Register.ZERO,
                    Register.T0,
                    Opcode.ADD)
            elif self.step == 17:
                self.data_path.signal_latch_data_address(Register.T0)
            elif self.step == 18:
                self.data_path.signal_data_memory_load(Register.T0)
            elif self.step == 19:
                self.signal_latch_pc(0, Register.T0)
                self.state = ProcessorState.INT_BODY
                self.step = 0
                self.tick()
                return

            self.step += 1
            self.tick()
            return

        if self.state is ProcessorState.INT_EXIT:
            if self.step == 0:
                self.signal_latch_pc(0, Register.RA)
            elif self.step == 1:
                self.data_path.signal_perform_alu_operation_imm(INTERRUPT_STORE_AREA_START_ADDR, Register.ZERO,
                                                                Register.RA, Opcode.ADD)
            elif self.step == 2:
                self.data_path.signal_latch_data_address(Register.RA)
            elif self.step == 3:
                self.data_path.signal_data_memory_load(Register.T0)
            elif self.step == 4:
                self.data_path.signal_perform_alu_operation_imm(1, Register.RA, Register.RA, Opcode.ADD)
            elif self.step == 5:
                self.data_path.signal_latch_data_address(Register.RA)
            elif self.step == 6:
                self.data_path.signal_data_memory_load(Register.T1)
            elif self.step == 7:
                self.data_path.signal_perform_alu_operation_imm(1, Register.RA, Register.RA, Opcode.ADD)
            elif self.step == 8:
                self.data_path.signal_latch_data_address(Register.RA)
            elif self.step == 9:
                self.data_path.signal_data_memory_load(Register.T2)
            elif self.step == 10:
                self.data_path.signal_perform_alu_operation_imm(1, Register.RA, Register.RA, Opcode.ADD)
            elif self.step == 11:
                self.data_path.signal_latch_data_address(Register.RA)
            elif self.step == 12:
                self.data_path.signal_data_memory_load(Register.T3)
            elif self.step == 13:
                self.data_path.signal_perform_alu_operation_imm(1, Register.RA, Register.RA, Opcode.ADD)
            elif self.step == 14:
                self.data_path.signal_latch_data_address(Register.RA)
            elif self.step == 15:
                self.data_path.signal_data_memory_load(Register.SP)
                self.state = ProcessorState.NORMAL
                self.step = 0
                self.tick()
                return

            self.step += 1
            self.tick()
            return

        instr = self.instruction_memory[self.program_counter]

        if instr.opcode is Opcode.HALT:
            raise StopIteration()

        if instr.opcode is Opcode.RINT:
            self.state = ProcessorState.INT_EXIT
            self.tick()
            return

        if isinstance(instr, UInstruction):

            if instr.opcode is Opcode.LUI:
                self.data_path.signal_perform_alu_operation_u_imm(instr.u_imm, Register.ZERO, instr.rd, Opcode.ADD)
                self.signal_latch_pc()
                self.step = 0
                self.tick()
                return

            if instr.opcode is Opcode.JAL:
                if self.step == 0:
                    self.signal_latch_pc()
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
                    return

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
                    self.signal_latch_pc(instr.imm, instr.rs1)
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
        state_repr = "STATE: {}\tTICK: {:3} PC: {:3}/{} ADDR: {:3} MEM_OUT: {:3} T0: {:3} T1: {:3} T2: {:3} T3: {:3} RA {:3} SP: {:3}".format(
            self.state,
            self._tick,
            self.program_counter,
            self.step,
            self.data_path.data_address,
            self.data_path.data_memory[self.data_path.data_address],
            self.data_path.registers[Register.T0],
            self.data_path.registers[Register.T1],
            self.data_path.registers[Register.T2],
            self.data_path.registers[Register.T3],
            self.data_path.registers[Register.RA],
            self.data_path.registers[Register.SP],
        )

        instr = self.instruction_memory[self.program_counter]

        return "{} \t{}".format(state_repr, instr)
