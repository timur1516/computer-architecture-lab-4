from src.isa.instructions.instruction import Instruction
from src.isa.opcode import Opcode, opcode_to_binary, binary_to_opcode
from src.isa.util.binary import is_correct_bin_size_signed, extract_bits, binary_to_signed_int


class JInstruction(Instruction):
    imm = None

    def __init__(self, opcode: Opcode, imm: int):
        assert is_correct_bin_size_signed(imm, 25), 'imm size in JInstruction without rs1 must be 25 bits'

        super().__init__(opcode)
        self.imm = imm

    def to_binary(self) -> int:
        return (self.imm << 7 |
                opcode_to_binary[self.opcode])

    @staticmethod
    def from_binary(binary: int) -> 'JInstruction':
        opcode_bin = extract_bits(binary, 7)
        opcode = binary_to_opcode[opcode_bin]

        imm = binary_to_signed_int(binary >> 7, 25)

        return JInstruction(opcode, imm)


def to_json(self) -> dict:
    return {'opcode': str(self.opcode), 'imm': self.imm}


def __str__(self) -> str:
    return f'{str(self.opcode)} {str(self.imm)}'
