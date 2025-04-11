from src.isa.instructions.instruction import Instruction
from src.isa.opcode import Opcode, opcode_to_binary, binary_to_opcode
from src.isa.register import Register, register_to_binary, binary_to_register
from src.isa.util.binary import is_correct_bin_size_signed, extract_bits, binary_to_signed_int


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
