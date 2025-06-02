from typing_extensions import override

from src.isa.instructions.instruction import Instruction
from src.isa.opcode_ import Opcode, binary_to_opcode, opcode_to_binary
from src.isa.register import Register, binary_to_register, register_to_binary
from src.isa.util.binary import binary_to_signed_int, extract_bits, is_correct_bin_size_signed


class IInstruction(Instruction):
    """I-инструкции.

    Это инструкции, использующие непосредственные (константные) значения. Например `addi`, `lw`.

    Структура инструкции:

    ```plaintext
    ┌─────────────────────────────────────────┬─────────┬────────┬────────┐
    │                 31...11                 │  10...8 │  7...5 │  4..0  │
    ├─────────────────────────────────────────┼─────────┼────────┼────────┤
    │                   imm                   │   rs1   │   rd   │ opcode │
    └─────────────────────────────────────────┴─────────┴────────┴────────┘
    ```
    """

    rd = None
    "код регистра назначения, 3 бита"

    rs1 = None
    "код регистра источника, 3 бита"

    imm = None
    "непосредственное значение, 21 бит"

    def __init__(self, opcode: Opcode, rd: Register, rs1: Register, imm: int):
        assert is_correct_bin_size_signed(imm, 21), "imm size in IInstruction must be 21 bits"

        super().__init__(opcode)
        self.rd = rd
        self.rs1 = rs1
        self.imm = imm

    @override
    def to_binary(self) -> int:
        return (
            self.imm << 11
            | register_to_binary[self.rs1] << 8
            | register_to_binary[self.rd] << 5
            | opcode_to_binary[self.opcode]
        )

    @staticmethod
    @override
    def from_binary(binary: int) -> "IInstruction":
        opcode_bin = extract_bits(binary, 5)
        opcode = binary_to_opcode[opcode_bin]

        rd_bin = extract_bits(binary >> 5, 3)
        rd = binary_to_register[rd_bin]

        rs1_bin = extract_bits(binary >> 8, 3)
        rs1 = binary_to_register[rs1_bin]

        imm = binary_to_signed_int(binary >> 11, 21)

        return IInstruction(opcode, rd, rs1, imm)

    @override
    def to_json(self) -> dict:
        return {
            "address": self.address,
            "opcode": str(self.opcode),
            "rd": str(self.rd),
            "rs1": str(self.rs1),
            "imm": self.imm,
        }

    def __str__(self) -> str:
        return f"{self.opcode!s} {self.rd!s}, {self.rs1!s}, {self.imm!s}"
