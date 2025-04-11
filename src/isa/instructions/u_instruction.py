from src.isa.instructions.instruction import Instruction
from src.isa.opcode import Opcode, opcode_to_binary, binary_to_opcode
from src.isa.register import Register, register_to_binary, binary_to_register
from src.isa.util.binary import is_correct_bin_size_signed, extract_bits, binary_to_signed_int


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
