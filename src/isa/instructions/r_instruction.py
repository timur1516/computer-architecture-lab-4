from src.isa.instructions.instruction import Instruction
from src.isa.opcode_ import Opcode, binary_to_opcode, opcode_to_binary
from src.isa.register import Register, binary_to_register, register_to_binary
from src.isa.util.binary import extract_bits


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
        return (
            register_to_binary[self.rs2] << 17
            | register_to_binary[self.rs1] << 12
            | register_to_binary[self.rd] << 7
            | opcode_to_binary[self.opcode]
        )

    @staticmethod
    def from_binary(binary: int) -> "RInstruction":
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
        return {"opcode": str(self.opcode), "rd": str(self.rd), "rs1": str(self.rs1), "rs2": str(self.rs2)}

    def __str__(self) -> str:
        return f"{self.opcode!s} {self.rd!s}, {self.rs1!s}, {self.rs2!s}"
