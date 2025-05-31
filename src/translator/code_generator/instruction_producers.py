from __future__ import annotations

import copy

from src.isa.instructions.b_instruction import BInstruction
from src.isa.instructions.i_instruction import IInstruction
from src.isa.instructions.instruction import Instruction
from src.isa.instructions.j_instruction import JInstruction
from src.isa.instructions.jr_instruction import JRInstruction
from src.isa.instructions.r_instruction import RInstruction
from src.isa.instructions.u_instruction import UInstruction
from src.isa.memory_config import INPUT_ADDRESS, OUTPUT_ADDRESS
from src.isa.opcode_ import Opcode
from src.isa.register import Register
from src.isa.util.binary import binary_to_signed_int, is_correct_bin_size_signed
from src.translator.code_generator.stubs import BranchStub, JumpStub, LabelStub
from src.translator.token.token_type import TokenType


def pop_to_register_instructions_producer(rd: Register) -> list[Instruction]:
    return [
        IInstruction(Opcode.LW, rd, Register.SP, 0),
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 1),
    ]


def push_register_instructions_producer(rs: Register) -> list[Instruction]:
    return [
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, -1),
        BInstruction(Opcode.SW, Register.SP, rs, 0),
    ]


def push_number_instructions_producer(value) -> list[Instruction]:
    if is_correct_bin_size_signed(value, 15):
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
    upper_value = binary_to_signed_int(value >> 32, 64)
    return [
        *push_number_instructions_producer(lower_value),
        *push_number_instructions_producer(upper_value),
    ]


def while_instructions_producer(while_block_instructions: list[Instruction]) -> list[Instruction]:
    label = LabelStub()
    return [
        label,
        *while_block_instructions,
        *pop_to_register_instructions_producer(Register.T0),
        BranchStub(Opcode.BNE, Register.T0, Register.ZERO, label),
    ]


def if_instructions_producer(
    if_block_instructions: list[Instruction], else_block_instructions: list[Instruction]
) -> list[Instruction]:
    else_label = LabelStub()
    if_label = LabelStub()
    return [
        *pop_to_register_instructions_producer(Register.T0),
        BranchStub(Opcode.BEQ, Register.T0, Register.ZERO, else_label),
        *if_block_instructions,
        JumpStub(if_label),
        else_label,
        *else_block_instructions,
        if_label,
    ]


def label_stub_instructions_producer(stub: LabelStub) -> list[Instruction]:
    return []


def branch_stub_instructions_producer(stub: BranchStub) -> list[Instruction]:
    label_address = stub.label.address
    offset = label_address - stub.address
    if is_correct_bin_size_signed(offset, 15):
        return [BInstruction(stub.opcode, stub.rs1, stub.rs2, offset)]
    if is_correct_bin_size_signed(offset - 2, 25):
        return [
            BInstruction(stub.opcode, stub.rs1, stub.rs2, 2),
            JInstruction(Opcode.J, 2),
            JInstruction(Opcode.J, offset - 2),
        ]
    lower_value = binary_to_signed_int(label_address, 12)
    upper_value = binary_to_signed_int(((label_address - lower_value) >> 12), 20)
    return [
        BInstruction(stub.opcode, stub.rs1, stub.rs2, 2),
        JInstruction(Opcode.J, 4),
        UInstruction(Opcode.LUI, Register.T0, upper_value),
        IInstruction(Opcode.ADDI, Register.T0, Register.T0, lower_value),
        JRInstruction(Opcode.JR, 0, Register.T0),
    ]


def jump_stub_instructions_producer(stub: JumpStub) -> list[Instruction]:
    label_address = stub.label.address
    offset = label_address - stub.address
    if is_correct_bin_size_signed(offset, 25):
        return [JInstruction(Opcode.J, offset)]
    lower_value = binary_to_signed_int(label_address, 12)
    upper_value = binary_to_signed_int(((label_address - lower_value) >> 12), 20)
    return [
        UInstruction(Opcode.LUI, Register.T0, upper_value),
        IInstruction(Opcode.ADDI, Register.T0, Register.T0, lower_value),
        JRInstruction(Opcode.JR, 0, Register.T0),
    ]


def symbol_instructions_producer(symbol_address: int) -> list[Instruction]:
    return [
        IInstruction(Opcode.ADDI, Register.T0, Register.ZERO, symbol_address),
        *push_register_instructions_producer(Register.T0),
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
    TokenType.MOD: [
        *pop_to_register_instructions_producer(Register.T0),
        *pop_to_register_instructions_producer(Register.T1),
        RInstruction(Opcode.REM, Register.T0, Register.T1, Register.T0),
        *push_register_instructions_producer(Register.T0),
    ],
    TokenType.NEG: [
        *pop_to_register_instructions_producer(Register.T0),
        IInstruction(Opcode.ADDI, Register.T1, Register.ZERO, -1),
        RInstruction(Opcode.XOR, Register.T0, Register.T1, Register.T0),
        IInstruction(Opcode.ADDI, Register.T0, Register.T0, 1),
        *push_register_instructions_producer(Register.T0),
    ],
    TokenType.ABS: [
        *pop_to_register_instructions_producer(Register.T0),
        BInstruction(Opcode.BGT, Register.T0, Register.ZERO, 5),
        BInstruction(Opcode.BEQ, Register.T0, Register.ZERO, 4),
        IInstruction(Opcode.ADDI, Register.T1, Register.ZERO, -1),
        RInstruction(Opcode.XOR, Register.T0, Register.T1, Register.T0),
        IInstruction(Opcode.ADDI, Register.T0, Register.T0, 1),
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
    TokenType.D_MINUS: [
        *pop_to_register_instructions_producer(Register.T0),
        *pop_to_register_instructions_producer(Register.T1),
        IInstruction(Opcode.ADDI, Register.T2, Register.ZERO, -1),
        RInstruction(Opcode.XOR, Register.T0, Register.T2, Register.T0),
        RInstruction(Opcode.XOR, Register.T1, Register.T2, Register.T1),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 1),
        RInstruction(Opcode.ADC, Register.T2, Register.T3, Register.T1),
        RInstruction(Opcode.ADD, Register.T0, Register.T2, Register.T0),
        RInstruction(Opcode.ADD, Register.T1, Register.T3, Register.T1),
        *pop_to_register_instructions_producer(Register.T2),
        *pop_to_register_instructions_producer(Register.T3),
        RInstruction(Opcode.ADD, Register.T0, Register.T2, Register.T0),
        RInstruction(Opcode.ADC, Register.T2, Register.T3, Register.T1),
        RInstruction(Opcode.ADD, Register.T0, Register.T2, Register.T0),
        RInstruction(Opcode.ADD, Register.T1, Register.T3, Register.T1),
        *push_register_instructions_producer(Register.T1),
        *push_register_instructions_producer(Register.T0),
    ],
    TokenType.D_NEG: [
        *pop_to_register_instructions_producer(Register.T0),
        *pop_to_register_instructions_producer(Register.T1),
        IInstruction(Opcode.ADDI, Register.T2, Register.ZERO, -1),
        RInstruction(Opcode.XOR, Register.T0, Register.T2, Register.T0),
        RInstruction(Opcode.XOR, Register.T1, Register.T2, Register.T1),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 1),
        RInstruction(Opcode.ADC, Register.T2, Register.T3, Register.T1),
        RInstruction(Opcode.ADD, Register.T0, Register.T2, Register.T0),
        RInstruction(Opcode.ADD, Register.T1, Register.T3, Register.T1),
        *push_register_instructions_producer(Register.T1),
        *push_register_instructions_producer(Register.T0),
    ],
    TokenType.D_ABS: [
        *pop_to_register_instructions_producer(Register.T0),
        BInstruction(Opcode.BGT, Register.T0, Register.ZERO, 13),
        BInstruction(Opcode.BEQ, Register.T0, Register.ZERO, 12),
        *pop_to_register_instructions_producer(Register.T1),
        IInstruction(Opcode.ADDI, Register.T2, Register.ZERO, -1),
        RInstruction(Opcode.XOR, Register.T0, Register.T2, Register.T0),
        RInstruction(Opcode.XOR, Register.T1, Register.T2, Register.T1),
        IInstruction(Opcode.ADDI, Register.T3, Register.ZERO, 1),
        RInstruction(Opcode.ADC, Register.T2, Register.T3, Register.T1),
        RInstruction(Opcode.ADD, Register.T0, Register.T2, Register.T0),
        RInstruction(Opcode.ADD, Register.T1, Register.T3, Register.T1),
        *push_register_instructions_producer(Register.T1),
        *push_register_instructions_producer(Register.T0),
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
    TokenType.OVER: [
        IInstruction(Opcode.LW, Register.T0, Register.SP, 1),
        *push_register_instructions_producer(Register.T0),
    ],
    TokenType.D_DUP: [
        IInstruction(Opcode.LW, Register.T0, Register.SP, 0),
        IInstruction(Opcode.LW, Register.T1, Register.SP, 1),
        *push_register_instructions_producer(Register.T1),
        *push_register_instructions_producer(Register.T0),
    ],
    TokenType.D_DROP: [
        IInstruction(Opcode.ADDI, Register.SP, Register.SP, 2),
    ],
    TokenType.D_SWAP: [
        *pop_to_register_instructions_producer(Register.T0),
        *pop_to_register_instructions_producer(Register.T1),
        *pop_to_register_instructions_producer(Register.T2),
        *pop_to_register_instructions_producer(Register.T3),
        *push_register_instructions_producer(Register.T3),
        *push_register_instructions_producer(Register.T2),
        *push_register_instructions_producer(Register.T1),
        *push_register_instructions_producer(Register.T0),
    ],
    TokenType.D_OVER: [
        IInstruction(Opcode.LW, Register.T0, Register.SP, 2),
        IInstruction(Opcode.LW, Register.T1, Register.SP, 3),
        *push_register_instructions_producer(Register.T1),
        *push_register_instructions_producer(Register.T0),
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
        BInstruction(Opcode.SW, Register.T1, Register.T0, 0),
    ],
    TokenType.READ: [
        IInstruction(Opcode.ADDI, Register.T1, Register.ZERO, INPUT_ADDRESS),
        IInstruction(Opcode.LW, Register.T0, Register.T1, 0),
        *push_register_instructions_producer(Register.T0),
    ],
    TokenType.STORE: [
        *pop_to_register_instructions_producer(Register.T0),
        *pop_to_register_instructions_producer(Register.T1),
        BInstruction(Opcode.SW, Register.T1, Register.T0, 0),
    ],
    TokenType.LOAD: [
        *pop_to_register_instructions_producer(Register.T0),
        IInstruction(Opcode.LW, Register.T0, Register.T0, 0),
        *push_register_instructions_producer(Register.T0),
    ],
    TokenType.D_STORE: [
        *pop_to_register_instructions_producer(Register.T0),
        *pop_to_register_instructions_producer(Register.T1),
        *pop_to_register_instructions_producer(Register.T2),
        BInstruction(Opcode.SW, Register.T2, Register.T0, 0),
        IInstruction(Opcode.ADDI, Register.T2, Register.T2, 1),
        BInstruction(Opcode.SW, Register.T2, Register.T1, 0),
    ],
    TokenType.D_LOAD: [
        *pop_to_register_instructions_producer(Register.T2),
        IInstruction(Opcode.LW, Register.T0, Register.T2, 0),
        IInstruction(Opcode.ADDI, Register.T2, Register.T2, 1),
        IInstruction(Opcode.LW, Register.T1, Register.T2, 0),
        *push_register_instructions_producer(Register.T1),
        *push_register_instructions_producer(Register.T0),
    ],
    TokenType.ENABLE_INT: [Instruction(Opcode.EINT)],
    TokenType.DISABLE_INT: [Instruction(Opcode.DINT)],
}
