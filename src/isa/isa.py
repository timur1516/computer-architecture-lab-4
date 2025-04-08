import json
from enum import Enum
from typing import List

from src.isa.bin_utils import extract_bits, binary_to_signed_int, is_correct_bin_size_signed, int_to_bin_word, \
    bytes_to_int_array
from src.isa.memory_config import DATA_AREA_START_ADDR, INTERRUPT_VECTORS_NUMBER


class Opcode(str, Enum):
    LUI = 'lui'
    JAL = 'jal'

    SW = 'sw'
    LW = 'lw'

    ADDI = 'addi'
    JALR = 'jalr'

    ADD = 'add'
    SUB = 'sub'
    MUL = 'mul'
    # MULH = 'mulh'
    DIV = 'div'
    REM = 'rem'
    SLL = 'sll'
    SRL = 'srl'
    # SRA = 'sra'
    AND = 'and'
    OR = 'or'
    XOR = 'xor'

    BEQ = 'beq'
    BNE = 'bne'
    # BGT = 'bgt'
    # BLE = 'ble'

    HALT = 'halt'
    RINT = 'rint'

    def __str__(self) -> str:
        return self.value


class Register(str, Enum):
    T0 = 't0'
    T1 = 't1'
    T2 = 't2'
    T3 = 't3'
    SP = 'sp'
    RA = 'ra'
    ZERO = 'zero'

    def __str__(self) -> str:
        return self.value


class Instruction:
    opcode = None

    def __init__(self, opcode: Opcode):
        self.opcode = opcode

    def to_binary(self) -> int:
        return opcode_to_binary[self.opcode]

    @staticmethod
    def from_binary(binary: int) -> 'Instruction':
        opcode_bin = extract_bits(binary, 7)
        opcode = binary_to_opcode[opcode_bin]

        return Instruction(opcode)

    def to_json(self) -> dict:
        return {'opcode': str(self.opcode)}

    def __str__(self) -> str:
        return str(self.opcode)


class UInstruction(Instruction):
    rd = None
    u_imm = None

    def __init__(self, opcode: Opcode, rd: Register, u_imm: int):
        assert is_correct_bin_size_signed(u_imm, 20), 'u_imm size in UInstruction must be 20 bits'

        super().__init__(opcode)
        self.rd = rd
        self.u_imm = u_imm

    def to_binary(self) -> int:
        return (self.u_imm << 12 |
                register_to_binary[self.rd] << 7 |
                opcode_to_binary[self.opcode])

    @staticmethod
    def from_binary(binary: int) -> 'UInstruction':
        opcode_bin = extract_bits(binary, 7)
        opcode = binary_to_opcode[opcode_bin]

        rd_bin = extract_bits(binary >> 7, 5)
        rd = binary_to_register[rd_bin]

        u_imm = binary_to_signed_int(binary >> 12, 20)

        return UInstruction(opcode, rd, u_imm)

    def to_json(self) -> dict:
        return {'opcode': str(self.opcode), 'rd': str(self.rd), 'u_imm': self.u_imm}

    def __str__(self) -> str:
        return f'{str(self.opcode)} {str(self.rd)}, {str(self.u_imm)}'


class SInstruction(Instruction):
    rd = None
    rs1 = None
    rs2 = None

    def __init__(self, opcode: Opcode, rd: Register | None, rs1: Register, rs2: Register | None):
        assert rd is not None or rs2 is not None, 'rd and rs2 cant be None in the same time for SInstruction'

        super().__init__(opcode)
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2

    def to_binary(self) -> int:
        if self.rd is None:
            return (register_to_binary[self.rs2] << 17 |
                    register_to_binary[self.rs1] << 12 |
                    0x0 << 7 |
                    opcode_to_binary[self.opcode])

        return (register_to_binary[self.rs1] << 12 |
                register_to_binary[self.rd] << 7 |
                opcode_to_binary[self.opcode])

    @staticmethod
    def from_binary(binary: int) -> 'SInstruction':
        opcode_bin = extract_bits(binary, 7)
        opcode = binary_to_opcode[opcode_bin]

        rd_bin = extract_bits(binary >> 7, 5)
        rd = binary_to_register[rd_bin]

        rs1_bin = extract_bits(binary >> 12, 5)
        rs1 = binary_to_register[rs1_bin]

        rs2_bin = extract_bits(binary >> 17, 5)
        rs2 = binary_to_register[rs2_bin]

        return SInstruction(opcode, rd, rs1, rs2)

    def to_json(self) -> dict:
        return {'opcode': str(self.opcode), 'rd': str(self.rd), 'rs1': str(self.rs1), 'rs2': str(self.rs2)}

    def __str__(self) -> str:
        if self.rd is None:
            return f'{str(self.opcode)} {str(self.rs2)}, {str(self.rs1)}'
        return f'{str(self.opcode)} {str(self.rd)}, {str(self.rs1)}'


class IInstruction(Instruction):
    rd = None
    rs1 = None
    imm = None

    def __init__(self, opcode: Opcode, rd: Register, rs1: Register, imm: int):
        assert is_correct_bin_size_signed(imm, 12), 'imm size in IInstruction must be 12 bits'

        super().__init__(opcode)
        self.rd = rd
        self.rs1 = rs1
        self.imm = imm

    def to_binary(self) -> int:
        return (self.imm << 17 |
                register_to_binary[self.rs1] << 12 |
                register_to_binary[self.rd] << 7 |
                opcode_to_binary[self.opcode])

    @staticmethod
    def from_binary(binary: int) -> 'IInstruction':
        opcode_bin = extract_bits(binary, 7)
        opcode = binary_to_opcode[opcode_bin]

        rd_bin = extract_bits(binary >> 7, 5)
        rd = binary_to_register[rd_bin]

        rs1_bin = extract_bits(binary >> 12, 5)
        rs1 = binary_to_register[rs1_bin]

        imm = binary_to_signed_int(binary >> 17, 12)

        return IInstruction(opcode, rd, rs1, imm)

    def to_json(self) -> dict:
        return {'opcode': str(self.opcode), 'rd': str(self.rd), 'rs1': str(self.rs1), 'imm': self.imm}

    def __str__(self) -> str:
        return f'{str(self.opcode)} {str(self.rd)}, {str(self.rs1)}, {str(self.imm)}'


class RInstruction(Instruction):
    rd = None
    rs1 = None
    rs2 = None

    def __init__(self, opcode: Opcode, rd: Register, rs1: Register, rs2: Register):
        super().__init__(opcode)
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2

    def to_binary(self) -> int:
        return (register_to_binary[self.rs2] << 17 |
                register_to_binary[self.rs1] << 12 |
                register_to_binary[self.rd] << 7 |
                opcode_to_binary[self.opcode])

    @staticmethod
    def from_binary(binary: int) -> 'RInstruction':
        opcode_bin = extract_bits(binary, 7)
        opcode = binary_to_opcode[opcode_bin]

        rd_bin = extract_bits(binary >> 7, 5)
        rd = binary_to_register[rd_bin]

        rs1_bin = extract_bits(binary >> 12, 5)
        rs1 = binary_to_register[rs1_bin]

        rs2_bin = extract_bits(binary >> 17, 5)
        rs2 = binary_to_register[rs2_bin]

        return RInstruction(opcode, rd, rs1, rs2)

    def to_json(self) -> dict:
        return {'opcode': str(self.opcode), 'rd': str(self.rd), 'rs1': str(self.rs1), 'rs2': str(self.rs2)}

    def __str__(self) -> str:
        return f'{str(self.opcode)} {str(self.rd)}, {str(self.rs1)}, {str(self.rs2)}'


class BInstruction(Instruction):
    rs1 = None
    rs2 = None
    imm = None

    def __init__(self, opcode: Opcode, rs1: Register, rs2: Register, imm: int):
        assert is_correct_bin_size_signed(imm, 15), 'imm size in BInstruction must be 15 bits'

        super().__init__(opcode)
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = imm

    def to_binary(self) -> int:
        imm_lower = extract_bits(self.imm, 5)
        imm_upper = self.imm >> 5

        return (imm_upper << 22 |
                register_to_binary[self.rs2] << 17 |
                register_to_binary[self.rs1] << 12 |
                imm_lower << 7 |
                opcode_to_binary[self.opcode])

    @staticmethod
    def from_binary(binary: int) -> 'BInstruction':
        opcode_bin = extract_bits(binary, 7)
        opcode = binary_to_opcode[opcode_bin]

        imm_lower = extract_bits(binary >> 7, 5)
        imm_upper = extract_bits(binary >> 22, 10)
        imm_bin = (imm_upper << 5) | imm_lower
        imm = binary_to_signed_int(imm_bin, 15)

        rs1_bin = extract_bits(binary >> 12, 5)
        rs1 = binary_to_register[rs1_bin]

        rs2_bin = extract_bits(binary >> 17, 5)
        rs2 = binary_to_register[rs2_bin]

        return BInstruction(opcode, rs1, rs2, imm)

    def to_json(self) -> dict:
        return {'opcode': str(self.opcode), 'rs1': str(self.rs1), 'rs2': str(self.rs2), 'imm': self.imm}

    def __str__(self) -> str:
        return f'{str(self.opcode)} {str(self.rs1)}, {str(self.rs2)}, {str(self.imm)}'


opcode_to_binary = {
    Opcode.LUI: 0x1,
    Opcode.JAL: 0x2,
    Opcode.SW: 0x3,
    Opcode.LW: 0x4,
    Opcode.ADDI: 0x5,
    Opcode.JALR: 0x6,
    Opcode.ADD: 0x7,
    Opcode.SUB: 0x8,
    Opcode.MUL: 0x9,
    Opcode.DIV: 0xA,
    Opcode.REM: 0xB,
    Opcode.SLL: 0xC,
    Opcode.SRL: 0xD,
    Opcode.AND: 0xE,
    Opcode.XOR: 0xF,
    Opcode.BEQ: 0x10,
    Opcode.BNE: 0x11,
    Opcode.HALT: 0x12,
    Opcode.RINT: 0x13,
}

binary_to_opcode = {
    0x1: Opcode.LUI,
    0x2: Opcode.JAL,
    0x3: Opcode.SW,
    0x4: Opcode.LW,
    0x5: Opcode.ADDI,
    0x6: Opcode.JALR,
    0x7: Opcode.ADD,
    0x8: Opcode.SUB,
    0x9: Opcode.MUL,
    0xA: Opcode.DIV,
    0xB: Opcode.REM,
    0xC: Opcode.SLL,
    0xD: Opcode.SRL,
    0xE: Opcode.AND,
    0xF: Opcode.XOR,
    0x10: Opcode.BEQ,
    0x11: Opcode.BNE,
    0x12: Opcode.HALT,
    0x13: Opcode.RINT,
}

register_to_binary = {
    Register.T0: 0x1,
    Register.T1: 0x2,
    Register.T2: 0x3,
    Register.T3: 0x4,
    Register.SP: 0x5,
    Register.RA: 0x6,
    Register.ZERO: 0x7
}

binary_to_register = {
    0x0: None,
    0x1: Register.T0,
    0x2: Register.T1,
    0x3: Register.T2,
    0x4: Register.T3,
    0x5: Register.SP,
    0x6: Register.RA,
    0x7: Register.ZERO
}

opcode_to_instruction_type = {
    Opcode.LUI: UInstruction,
    Opcode.JAL: UInstruction,

    Opcode.SW: SInstruction,
    Opcode.LW: SInstruction,

    Opcode.ADDI: IInstruction,
    Opcode.JALR: IInstruction,

    Opcode.ADD: RInstruction,
    Opcode.SUB: RInstruction,
    Opcode.MUL: RInstruction,
    Opcode.DIV: RInstruction,
    Opcode.REM: RInstruction,
    Opcode.SLL: RInstruction,
    Opcode.SRL: RInstruction,
    Opcode.AND: RInstruction,
    Opcode.XOR: RInstruction,

    Opcode.BEQ: BInstruction,
    Opcode.BNE: BInstruction,

    Opcode.HALT: Instruction,
    Opcode.RINT: Instruction
}


def to_bytes(code: List[Instruction], data: List[int], interrupt_vectors: List[int], is_interrupts_enabled) -> bytes:
    binary_code = bytearray()

    binary_code.extend(int_to_bin_word(int(is_interrupts_enabled)))

    for vector in interrupt_vectors:
        binary_code.extend(int_to_bin_word(vector))

    data_len = len(data)
    binary_code.extend(int_to_bin_word(data_len))

    for word in data:
        binary_code.extend(int_to_bin_word(word))

    for instr in code:
        binary_instr = instr.to_binary()
        binary_code.extend(int_to_bin_word(binary_instr))

    return bytes(binary_code)


def to_hex(binary_code: bytes) -> str:
    result = []
    data_address = DATA_AREA_START_ADDR
    instruction_address = 0

    word_list = bytes_to_int_array(binary_code)

    is_interrupts_enabled = bool(word_list[0])

    result.append(f'is interrupts enabled: {is_interrupts_enabled}')

    interrupt_vectors = word_list[1:1 + INTERRUPT_VECTORS_NUMBER]

    result.append('interrupt vectors:')
    for vector in interrupt_vectors:
        result.append(f'{vector:08X} - {vector:032b}')

    data_len = word_list[1 + INTERRUPT_VECTORS_NUMBER]

    result.append(f'data')

    for word in word_list[2 + INTERRUPT_VECTORS_NUMBER:data_len + 2 + INTERRUPT_VECTORS_NUMBER]:
        hex_word = f'{word:08X}'
        bin_word = f'{word:032b}'
        line = f'{data_address:3} - {hex_word} - {bin_word}'

        result.append(line)
        data_address += 1

    result.append(f'instructions')

    for word in word_list[data_len + 2 + INTERRUPT_VECTORS_NUMBER:]:
        opcode_bin = extract_bits(word, 7)
        opcode = binary_to_opcode[opcode_bin]

        instruction_type = opcode_to_instruction_type[opcode]
        instruction = instruction_type.from_binary(word)

        hex_word = f'{word:08X}'
        bin_word = f'{word:032b}'
        line = f'{instruction_address:3} - {hex_word} - {bin_word} - {str(instruction)}'

        result.append(line)
        instruction_address += 1

    return "\n".join(result)


def from_bytes(binary_code) -> (List[Instruction], List[int], List[int]):
    instructions = []
    data = []
    interrupt_vectors = []

    word_list = bytes_to_int_array(binary_code)

    is_interrupts_enabled = bool(word_list[0])

    interrupt_vectors = word_list[1:1 + INTERRUPT_VECTORS_NUMBER]

    data_len = word_list[1 + INTERRUPT_VECTORS_NUMBER]

    for word in word_list[2 + INTERRUPT_VECTORS_NUMBER:data_len + 2 + INTERRUPT_VECTORS_NUMBER]:
        data.append(word)

    for word in word_list[data_len + 2 + INTERRUPT_VECTORS_NUMBER:]:
        opcode_bin = extract_bits(word, 7)
        opcode = binary_to_opcode[opcode_bin]

        instruction_type = opcode_to_instruction_type[opcode]
        instruction = instruction_type.from_binary(word)

        instructions.append(instruction)

    return instructions, data, interrupt_vectors, is_interrupts_enabled


def write_json(filename: str, code: List[Instruction], data_memory: List[int], interrupt_vectors: List[int],
               is_interrupts_enabled: bool):
    data_address = DATA_AREA_START_ADDR
    instruction_address = 0
    interrupt_vectors_buf = []
    data_buf = []
    instructions_buf = []

    for vector in interrupt_vectors:
        interrupt_vectors_buf.append(json.dumps({"vector": vector}))

    for word in enumerate(data_memory):
        data_buf.append(json.dumps({"address": data_address, "word": word}))
        data_address += 1

    for i, instr in enumerate(code):
        instructions_buf.append(json.dumps({"address": instruction_address, **instr.to_json()}))
        instruction_address += 1

    with open(filename, "w", encoding="utf-8") as file:
        file.write(
            f'''{{
    "is_interrupts_enabled": {str.lower(str(is_interrupts_enabled))},
    "interrupt_vectors": [
        {",\n\t\t".join(interrupt_vectors_buf)}
    ],
    "data": [
        {",\n\t\t".join(data_buf)}
    ],
    "instructions": [
        {",\n\t\t".join(instructions_buf)}
    ]
}}''')
