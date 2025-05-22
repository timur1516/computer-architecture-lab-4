from __future__ import annotations

import logging
from enum import Enum

from src.isa.instructions.b_instruction import BInstruction
from src.isa.instructions.i_instruction import IInstruction
from src.isa.instructions.instruction import Instruction
from src.isa.instructions.j_instruction import JInstruction
from src.isa.instructions.jr_instruction import JRInstruction
from src.isa.instructions.r_instruction import RInstruction
from src.isa.instructions.s_instruction import SInstruction
from src.isa.instructions.u_instruction import UInstruction
from src.isa.opcode_ import Opcode
from src.isa.register import Register
from src.machine.data_path import DataPath
from src.machine.util import int_to_char


# TODO: Выделить память в отдельный модуль?
# TODO: Подумать над необходимостью состояний
class ProcessorState(str, Enum):
    """Вспомогательный класс для хранения состояния процессора"""

    NORMAL = "NORMAL"
    INT_ENTER = "INT_ENTER"
    INT_BODY = "INT_BODY"
    INT_EXIT = "INT_EXIT"

    def __str__(self):
        return self.value


class ControlUnit:
    """Блок управления процессора. Выполняет декодирование инструкций и
    управляет состоянием модели процессора, включая обработку данных (DataPath).
    """

    instruction_memory_size = None
    "Размер памяти инструкций"

    instruction_memory = None
    "Память инструкций"

    data_path = None
    "Блок обработки данных"

    program_counter = None
    "Счётчик команд. Инициализируется нулём"

    input_timetable = None
    "Расписание ввода, для обработки прерываний"

    _tick = None
    "Текущее модельное время процессора (в тактах). Инициализируется нулём."

    step = None
    "Номер шага для выполнения много тактовых инструкций"

    state = None
    "Текущее состояние процессора"

    is_interrupt_request = None
    "Флаг наличия запроса прерывания"

    interrupt_handler_address = None
    "Адрес обработчика прерываний"

    pc_interrupt_buffer = None
    "Буфер для сохранения счётчика команд при прерывании"

    is_interrupts_enabled = None
    "Флаг разрешение прерываний. Инициализируется значением `False`"

    def __init__(
        self,
        instructions: list[Instruction],
        instruction_memory_size: int,
        data_path: DataPath,
        input_timetable: dict[int, int],
        interrupt_handler_address: int,
    ):
        self.instruction_memory_size = instruction_memory_size
        self.instruction_memory: list[Instruction] = [
            IInstruction(Opcode.ADDI, Register.ZERO, Register.ZERO, 0)
        ] * instruction_memory_size
        self.init_instruction_memory(instructions)
        self.data_path = data_path
        self.input_timetable = input_timetable
        self.interrupt_handler_address = interrupt_handler_address

        self.program_counter = 0
        self._tick = 0
        self.step = 0
        self.state = ProcessorState.NORMAL
        self.is_interrupts_enabled = False
        self.is_interrupt_request = False
        self.pc_interrupt_buffer = 0

    def init_instruction_memory(self, program: list[Instruction]):
        """Выполняет заполнение размещение программы в памяти инструкций"""

        for instr in program:
            assert 0 <= instr.address <= self.instruction_memory_size, "instruction memory overflow"
            self.instruction_memory[instr.address] = instr

    def tick(self):
        """Продвинуть модельное время процессора вперёд на один такт."""
        self._tick += 1

    def get_tick(self):
        """Получить текущее модельное время процессора (в тактах)."""
        return self._tick

    def _signal_latch_pc(self, next_pc: int):
        """Защёлкнуть новое значение счётчика команд"""

        self.program_counter = next_pc

        assert self.program_counter < len(self.instruction_memory), "out of instruction memory: {}".format(
            self.program_counter
        )

    def signal_latch_pc_seq(self):
        """Защёлкнуть значение счётчика команд, увеличенное на единицу"""

        next_pc = self.program_counter + 1
        self._signal_latch_pc(next_pc)

    def signal_latch_pc_imm(self, imm: int):
        """Защёлкнуть значение счётчика команд, смещённое относительно текущего на значение `imm`"""

        next_pc = self.data_path.signal_next_pc_imm(self.program_counter, imm)
        self._signal_latch_pc(next_pc)

    def signal_latch_pc_reg(self, rs2: Register, imm: int = 0):
        """Защёлкнуть значение счётчика команд, смещённое относительно
        значения в регистре `rs2` на значение `imm`"""

        next_pc = self.data_path.signal_next_pc_reg(imm, rs2)
        self._signal_latch_pc(next_pc)

    def signal_latch_pc_buf(self):
        """Защёлкнуть значение счётчика команд из буфера счётчика команд"""

        next_pc = self.pc_interrupt_buffer
        self._signal_latch_pc(next_pc)

    def signal_latch_pc_interrupt(self):
        """Защёлкнуть значение счётчика команд адресом прерывания"""

        next_pc = self.interrupt_handler_address
        self._signal_latch_pc(next_pc)

    def signal_latch_pc_interrupt_buffer(self):
        """Защёлкнуть буфер счётчика команд текущим значением счётчика"""

        self.pc_interrupt_buffer = self.program_counter

    def process_next_tick(self):  # noqa: C901 # код хорошо структурирован, по этому не проблема.
        """Основной цикл процессора. Декодирует и выполняет инструкцию."""

        if self._tick in self.input_timetable:
            value = self.input_timetable[self._tick]
            logging.debug('Interrupt request on tick %s with value "%s" | %s', self._tick, int_to_char(value), value)
            if not self.is_interrupts_enabled:
                logging.debug("Interrupts are disabled")
            elif self.state in [ProcessorState.INT_ENTER, ProcessorState.INT_BODY]:
                logging.debug("Interrupts inside of interrupts are not supported")
            else:
                self.is_interrupt_request = True
                self.data_path.input_buffer.append(value)

        if self.is_interrupt_request and self.step == 0 and self.state == ProcessorState.NORMAL:
            self.state = ProcessorState.INT_ENTER
            self.is_interrupt_request = False

        if self.state is ProcessorState.INT_ENTER:
            if self.step == 0:
                self.data_path.signal_store_registers()
                self.signal_latch_pc_interrupt_buffer()
                self.step = 1
                self.tick()
                return

            if self.step == 1:
                self.signal_latch_pc_interrupt()
                self.step = 0
                self.state = ProcessorState.INT_BODY
                self.tick()
                return

        if self.state is ProcessorState.INT_EXIT:
            self.data_path.signal_restore_registers()
            self.signal_latch_pc_buf()
            self.step = 0
            self.state = ProcessorState.NORMAL
            self.tick()
            return

        instr = self.instruction_memory[self.program_counter]

        if instr.opcode is Opcode.HALT:
            raise StopIteration()

        if instr.opcode is Opcode.RINT:
            self.state = ProcessorState.INT_EXIT
            return

        if instr.opcode is Opcode.EINT:
            self.is_interrupts_enabled = True
            self.signal_latch_pc_seq()
            self.step = 0
            self.tick()
            return

        if instr.opcode is Opcode.DINT:
            self.is_interrupts_enabled = False
            self.signal_latch_pc_seq()
            self.step = 0
            self.tick()
            return

        if isinstance(instr, UInstruction):
            if instr.opcode is Opcode.LUI:
                self.data_path.signal_perform_alu_operation_u_imm(instr.u_imm, Register.ZERO, instr.rd, Opcode.ADD)
                self.signal_latch_pc_seq()
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
                    self.signal_latch_pc_seq()
                    self.step = 0
                    self.tick()
                    return

        if isinstance(instr, IInstruction):
            if instr.opcode is Opcode.ADDI:
                self.data_path.signal_perform_alu_operation_imm(instr.imm, instr.rs1, instr.rd, Opcode.ADD)
                self.signal_latch_pc_seq()
                self.step = 0
                self.tick()
                return
            # TODO: Подумать над загрузкой со смещением
            if instr.opcode is Opcode.LW:
                if self.step == 0:
                    self.data_path.signal_latch_data_address(instr.rs1)
                    self.step = 1
                    self.tick()
                    return

                if self.step == 1:
                    self.data_path.signal_data_memory_load(instr.rd)
                    self.signal_latch_pc_seq()
                    self.step = 0
                    self.tick()
                    return

        if isinstance(instr, RInstruction):
            self.data_path.signal_perform_alu_operation_reg(instr.rs1, instr.rs2, instr.rd, instr.opcode)
            self.signal_latch_pc_seq()
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
                        self.signal_latch_pc_imm(instr.imm)
                    else:
                        self.signal_latch_pc_seq()
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
                        self.signal_latch_pc_imm(instr.imm)
                    else:
                        self.signal_latch_pc_seq()
                    self.step = 0
                    self.tick()
                    return

            if instr.opcode is Opcode.BGT:
                if self.step == 0:
                    self.data_path.signal_perform_alu_operation_reg(instr.rs1, instr.rs2, Register.ZERO, Opcode.SUB)
                    self.step = 1
                    self.tick()
                    return

                if self.step == 1:
                    if self.data_path.zero_flag == 0 and self.data_path.negative_flag == self.data_path.overflow_flag:
                        self.signal_latch_pc_imm(instr.imm)
                    else:
                        self.signal_latch_pc_seq()
                    self.step = 0
                    self.tick()
                    return

            if instr.opcode is Opcode.BLT:
                if self.step == 0:
                    self.data_path.signal_perform_alu_operation_reg(instr.rs1, instr.rs2, Register.ZERO, Opcode.SUB)
                    self.step = 1
                    self.tick()
                    return

                if self.step == 1:
                    if self.data_path.negative_flag != self.data_path.overflow_flag:
                        self.signal_latch_pc_imm(instr.imm)
                    else:
                        self.signal_latch_pc_seq()
                    self.step = 0
                    self.tick()
                    return

        if isinstance(instr, JInstruction):
            if instr.opcode is Opcode.J:
                if self.step == 0:
                    self.signal_latch_pc_imm(instr.imm)
                    self.step = 0
                    self.tick()
                    return

        if isinstance(instr, JRInstruction):
            if instr.opcode is Opcode.JR:
                if self.step == 0:
                    self.signal_latch_pc_reg(instr.rs1, instr.imm)
                    self.step = 0
                    self.tick()
                    return

    def __repr__(self):
        state_repr = "STATE: {}\tTICK: {:3} PC: {:3}/{} ADDR: {:3} MEM_OUT: {:3} T0: {:3} T1: {:3} T2: {:3} T3: {:3} SP: {:3}".format(
            self.state,
            self._tick,
            self.program_counter,
            self.step,
            self.data_path.data_address,
            self.data_path.data_memory[self.data_path.data_address].value,
            self.data_path.registers_file[Register.T0],
            self.data_path.registers_file[Register.T1],
            self.data_path.registers_file[Register.T2],
            self.data_path.registers_file[Register.T3],
            self.data_path.registers_file[Register.SP],
        )

        instr = self.instruction_memory[self.program_counter]

        return "{} \t{}".format(state_repr, instr)
