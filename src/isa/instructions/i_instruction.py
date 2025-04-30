from src.isa.instructions.instruction import Instruction
from src.isa.opcode_ import Opcode, binary_to_opcode, opcode_to_binary
from src.isa.register import Register, binary_to_register, register_to_binary
from src.isa.util.binary import binary_to_signed_int, extract_bits, is_correct_bin_size_signed


class IInstruction(Instruction):
    rd = None
    rs1 = None
    imm = None

    def __init__(self, opcode: Opcode, rd: Register, rs1: Register, imm: int):
        assert is_correct_bin_size_signed(imm, 12), "imm size in IInstruction must be 12 bits"

        super().__init__(opcode)
        self.rd = rd
        self.rs1 = rs1
        self.imm = imm

    def to_binary(self) -> int:
        return (
            self.imm << 17
            | register_to_binary[self.rs1] << 12
            | register_to_binary[self.rd] << 7
            | opcode_to_binary[self.opcode]
        )

    @staticmethod
    def from_binary(binary: int) -> "IInstruction":
        opcode_bin = extract_bits(binary, 7)
        opcode = binary_to_opcode[opcode_bin]

        rd_bin = extract_bits(binary >> 7, 5)
        rd = binary_to_register[rd_bin]

        rs1_bin = extract_bits(binary >> 12, 5)
        rs1 = binary_to_register[rs1_bin]

        imm = binary_to_signed_int(binary >> 17, 12)

        return IInstruction(opcode, rd, rs1, imm)

    def to_json(self) -> dict:
        return {"opcode": str(self.opcode), "rd": str(self.rd), "rs1": str(self.rs1), "imm": self.imm}

    def __str__(self) -> str:
        return f"{self.opcode!s} {self.rd!s}, {self.rs1!s}, {self.imm!s}"
