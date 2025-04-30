from src.isa.instructions.instruction import Instruction
from src.isa.opcode_ import Opcode, binary_to_opcode, opcode_to_binary
from src.isa.register import Register, binary_to_register, register_to_binary
from src.isa.util.binary import binary_to_signed_int, extract_bits, is_correct_bin_size_signed


class JRInstruction(Instruction):
    rs1 = None
    imm = None

    def __init__(self, opcode: Opcode, imm: int, rs1: Register):
        assert is_correct_bin_size_signed(imm, 20), "imm size in JInstruction with rs1 must be 20 bits"

        super().__init__(opcode)
        self.rs1 = rs1
        self.imm = imm

    def to_binary(self) -> int:
        imm_lower = extract_bits(self.imm, 5)
        imm_upper = self.imm >> 5
        return imm_upper << 17 | register_to_binary[self.rs1] << 12 | imm_lower << 7 | opcode_to_binary[self.opcode]

    @staticmethod
    def from_binary(binary: int) -> "JRInstruction":
        opcode_bin = extract_bits(binary, 7)
        opcode = binary_to_opcode[opcode_bin]

        imm_lower = extract_bits(binary >> 7, 5)
        imm_upper = extract_bits(binary >> 17, 15)
        imm_bin = (imm_upper << 5) | imm_lower
        imm = binary_to_signed_int(imm_bin, 20)

        rs1_bin = extract_bits(binary >> 12, 5)
        rs1 = binary_to_register[rs1_bin]

        return JRInstruction(opcode, imm, rs1)

    def to_json(self) -> dict:
        return {"opcode": str(self.opcode), "rs1": str(self.rs1), "imm": self.imm}

    def __str__(self) -> str:
        return f"{self.opcode!s} {self.rs1!s} {self.imm!s}"
