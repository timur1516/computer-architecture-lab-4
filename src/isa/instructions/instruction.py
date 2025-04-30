from src.isa.opcode_ import Opcode, binary_to_opcode, opcode_to_binary
from src.isa.util.binary import extract_bits


class Instruction:
    opcode = None

    def __init__(self, opcode: Opcode):
        self.opcode = opcode

    def to_binary(self) -> int:
        return opcode_to_binary[self.opcode]

    @staticmethod
    def from_binary(binary: int) -> "Instruction":
        opcode_bin = extract_bits(binary, 7)
        opcode = binary_to_opcode[opcode_bin]

        return Instruction(opcode)

    def to_json(self) -> dict:
        return {"opcode": str(self.opcode)}

    def __str__(self) -> str:
        return str(self.opcode)
