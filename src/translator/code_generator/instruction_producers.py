from __future__ import annotations

import copy

from src.isa.instructions.b_instruction import BInstruction
from src.isa.instructions.i_instruction import IInstruction
from src.isa.instructions.instruction import Instruction
from src.isa.instructions.j_instruction import JInstruction
from src.isa.instructions.r_instruction import RInstruction
from src.isa.instructions.s_instruction import SInstruction
from src.isa.instructions.u_instruction import UInstruction
from src.isa.memory_config import INPUT_ADDRESS, OUTPUT_ADDRESS
from src.isa.opcode_ import Opcode
from src.isa.register import Register
from src.isa.util.binary import binary_to_signed_int, is_correct_bin_size_signed
from src.translator.token.token_type import TokenType

# TODO: Добавить обработку "длинных переходов с использованием JR"
# TODO: Подумать над оптимизацией количества инструкций, за счёт упрощённого выполнения операций на стеке (без явного PUSH и POP)


def pop_to_register_instructions_producer(rd: Register) -> list[Instruction]:
    return [
        IInstruction(Opcode.LW, rd, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
    ]


def push_register_instructions_producer(rs: Register) -> list[Instruction]:
    return [
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
        SInstruction(Opcode.SW, Register.SP, rs),
    ]


def push_number_instructions_producer(value) -> list[Instruction]:
    if is_correct_bin_size_signed(value, 12):
        return [
            IInstruction(Opcode.ADDI, Register.T0, Register.ZERO, value),
            *push_register_instructions_producer(Register.T0),
        ]
    lower_value = binary_to_signed_int(value, 12)
    upper_value = binary_to_signed_int(((value - lower_value) >> 12), 20)
    return [
        UInstruction(Opcode.LUI, Register.T0, upper_value),
        IInstruction(Opcode.ADDI, Register.T0, Register.T0, lower_value),
        *push_register_instructions_producer(Register.T0),
    ]


def push_extended_number_instructions_producer(value) -> list[Instruction]:
    lower_value = binary_to_signed_int(value, 32)
    upper_value = binary_to_signed_int(value >> 32, 32)
    return [
        *push_number_instructions_producer(lower_value),
        *push_number_instructions_producer(upper_value),
    ]


def while_instructions_producer(while_block_instructions: list[Instruction]) -> list[Instruction]:
    return [
        *while_block_instructions,
        *pop_to_register_instructions_producer(Register.T0),
        BInstruction(Opcode.BNE, Register.T0, Register.ZERO, -len(while_block_instructions) - 2),
    ]


def if_instructions_producer(
    if_block_instructions: list[Instruction], else_block_instructions: list[Instruction]
) -> list[Instruction]:
    return [
        IInstruction(Opcode.LW, Register.T0, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
        BInstruction(Opcode.BEQ, Register.T0, Register.ZERO, len(if_block_instructions) + 2),
        *if_block_instructions,
        JInstruction(Opcode.J, len(else_block_instructions) + 1),
        *else_block_instructions,
    ]


def symbol_instructions_producer(symbol_address: int) -> list[Instruction]:
    return [
        IInstruction(Opcode.ADDI, Register.T0, Register.ZERO, symbol_address),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
        SInstruction(Opcode.SW, Register.SP, Register.T0),
    ]


def operation_instructions_producer(token_type: TokenType) -> list[Instruction]:
    assert token_type in OPERATION_TRANSLATION, "Unsupported operation"
    return copy.deepcopy(OPERATION_TRANSLATION[token_type])


OPERATION_TRANSLATION = {
    TokenType.PLUS: [
        *pop_to_register_instructions_producer(Register.T0),
        *pop_to_register_instructions_producer(Register.T1),
        RInstruction(Opcode.ADD, Register.T0, Register.T1, Register.T0),
        *push_register_instructions_producer(Register.T0),
    ],
    TokenType.MINUS: [
        *pop_to_register_instructions_producer(Register.T0),
        *pop_to_register_instructions_producer(Register.T1),
        RInstruction(Opcode.SUB, Register.T0, Register.T1, Register.T0),
        *push_register_instructions_producer(Register.T0),
    ],
    TokenType.MUL: [
        *pop_to_register_instructions_producer(Register.T0),
        *pop_to_register_instructions_producer(Register.T1),
        RInstruction(Opcode.MUL, Register.T0, Register.T1, Register.T0),
        *push_register_instructions_producer(Register.T0),
    ],
    TokenType.DIV: [
        *pop_to_register_instructions_producer(Register.T0),
        *pop_to_register_instructions_producer(Register.T1),
        RInstruction(Opcode.DIV, Register.T0, Register.T1, Register.T0),
        *push_register_instructions_producer(Register.T0),
    ],
    TokenType.D_PLUS: [
        *pop_to_register_instructions_producer(Register.T0),
        *pop_to_register_instructions_producer(Register.T1),
        *pop_to_register_instructions_producer(Register.T2),
        *pop_to_register_instructions_producer(Register.T3),
        RInstruction(Opcode.ADD, Register.T0, Register.T2, Register.T0),
        RInstruction(Opcode.ADC, Register.T2, Register.T3, Register.T1),
        RInstruction(Opcode.ADD, Register.T0, Register.T2, Register.T0),
        RInstruction(Opcode.ADD, Register.T1, Register.T3, Register.T1),
        *push_register_instructions_producer(Register.T1),
        *push_register_instructions_producer(Register.T0),
    ],
    TokenType.D_MUL: [
        *pop_to_register_instructions_producer(Register.T0),
        *pop_to_register_instructions_producer(Register.T1),
        RInstruction(Opcode.MUL, Register.T2, Register.T1, Register.T0),
        RInstruction(Opcode.MULH, Register.T3, Register.T1, Register.T0),
        *push_register_instructions_producer(Register.T2),
        *push_register_instructions_producer(Register.T3),
    ],
    TokenType.AND: [
        *pop_to_register_instructions_producer(Register.T0),
        *pop_to_register_instructions_producer(Register.T1),
        RInstruction(Opcode.AND, Register.T0, Register.T1, Register.T0),
        *push_register_instructions_producer(Register.T0),
    ],
    TokenType.OR: [
        *pop_to_register_instructions_producer(Register.T0),
        *pop_to_register_instructions_producer(Register.T1),
        RInstruction(Opcode.OR, Register.T0, Register.T1, Register.T0),
        *push_register_instructions_producer(Register.T0),
    ],
    TokenType.XOR: [
        *pop_to_register_instructions_producer(Register.T0),
        *pop_to_register_instructions_producer(Register.T1),
        RInstruction(Opcode.XOR, Register.T0, Register.T1, Register.T0),
        *push_register_instructions_producer(Register.T0),
    ],
    TokenType.NOT: [
        *pop_to_register_instructions_producer(Register.T0),
        IInstruction(Opcode.ADDI, Register.T1, Register.ZERO, -1),
        RInstruction(Opcode.XOR, Register.T0, Register.T1, Register.T0),
        *push_register_instructions_producer(Register.T0),
    ],
    TokenType.DUP: [
        IInstruction(Opcode.LW, Register.T0, Register.SP, 0),
        *push_register_instructions_producer(Register.T0),
    ],
    TokenType.DROP: [IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1)],
    TokenType.SWAP: [
        *pop_to_register_instructions_producer(Register.T0),
        *pop_to_register_instructions_producer(Register.T1),
        *push_register_instructions_producer(Register.T0),
        *push_register_instructions_producer(Register.T1),
    ],
    TokenType.EQUALS: [
        *pop_to_register_instructions_producer(Register.T0),
        *pop_to_register_instructions_producer(Register.T1),
        BInstruction(Opcode.BEQ, Register.T0, Register.T1, 3),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 0),
        JInstruction(Opcode.J, 2),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 1),
        *push_register_instructions_producer(Register.T3),
    ],
    TokenType.NOT_EQUALS: [
        *pop_to_register_instructions_producer(Register.T0),
        *pop_to_register_instructions_producer(Register.T1),
        BInstruction(Opcode.BNE, Register.T0, Register.T1, 3),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 0),
        JInstruction(Opcode.J, 2),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 1),
        *push_register_instructions_producer(Register.T3),
    ],
    TokenType.GREATER: [
        *pop_to_register_instructions_producer(Register.T1),
        *pop_to_register_instructions_producer(Register.T0),
        BInstruction(Opcode.BGT, Register.T0, Register.T1, 3),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 0),
        JInstruction(Opcode.J, 2),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 1),
        *push_register_instructions_producer(Register.T3),
    ],
    TokenType.LESS: [
        *pop_to_register_instructions_producer(Register.T1),
        *pop_to_register_instructions_producer(Register.T0),
        BInstruction(Opcode.BLT, Register.T0, Register.T1, 3),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 0),
        JInstruction(Opcode.J, 2),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 1),
        *push_register_instructions_producer(Register.T3),
    ],
    TokenType.GREATER_EQUAL: [
        *pop_to_register_instructions_producer(Register.T1),
        *pop_to_register_instructions_producer(Register.T0),
        BInstruction(Opcode.BGT, Register.T0, Register.T1, 4),
        BInstruction(Opcode.BEQ, Register.T0, Register.T1, 3),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 0),
        JInstruction(Opcode.J, 2),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 1),
        *push_register_instructions_producer(Register.T3),
    ],
    TokenType.LESS_EQUAL: [
        *pop_to_register_instructions_producer(Register.T1),
        *pop_to_register_instructions_producer(Register.T0),
        BInstruction(Opcode.BLT, Register.T0, Register.T1, 4),
        BInstruction(Opcode.BEQ, Register.T0, Register.T1, 3),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 0),
        JInstruction(Opcode.J, 2),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 1),
        *push_register_instructions_producer(Register.T3),
    ],
    TokenType.PRINT: [
        *pop_to_register_instructions_producer(Register.T0),
        IInstruction(Opcode.ADDI, Register.T1, Register.ZERO, OUTPUT_ADDRESS),
        SInstruction(Opcode.SW, Register.T1, Register.T0),
    ],
    TokenType.READ: [
        IInstruction(Opcode.ADDI, Register.T1, Register.ZERO, INPUT_ADDRESS),
        IInstruction(Opcode.LW, Register.T0, Register.T1, 0),
        *push_register_instructions_producer(Register.T0),
    ],
    TokenType.STORE: [
        *pop_to_register_instructions_producer(Register.T0),
        *pop_to_register_instructions_producer(Register.T1),
        SInstruction(Opcode.SW, Register.T1, Register.T0),
    ],
    TokenType.LOAD: [
        *pop_to_register_instructions_producer(Register.T0),
        IInstruction(Opcode.LW, Register.T0, Register.T0, 0),
        *push_register_instructions_producer(Register.T0),
    ],
    TokenType.ENABLE_INT: [Instruction(Opcode.EINT)],
    TokenType.DISABLE_INT: [Instruction(Opcode.DINT)],
}
