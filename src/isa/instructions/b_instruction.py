from typing import override

from src.isa.instructions.instruction import Instruction
from src.isa.opcode_ import Opcode, binary_to_opcode, opcode_to_binary
from src.isa.register import Register, binary_to_register, register_to_binary
from src.isa.util.binary import binary_to_signed_int, extract_bits, is_correct_bin_size_signed


class BInstruction(Instruction):
    """B-инструкции.

    Это инструкции для условных переходов. Например `beq`, `bgt`.

    Структура инструкции:

    ```
    ┌───────────────────────────────┬─────────┬─────────┬────────┬────────┐
    │           31...14             │ 13...11 │  10...8 │  7...5 │  4..0  │
    ├───────────────────────────────┼─────────┼─────────┼────────┼────────┤
    │              imm              │   rs2   │   rs1   │   imm  │ opcode │
    └───────────────────────────────┴─────────┴─────────┴────────┴────────┘
    ```
    """

    rs1 = None
    "код регистра первого операнда, 3 бита"

    rs2 = None
    "код регистра второго операнда, 3 бита"

    imm = None
    "величина смещения, 21 бит"

    def __init__(self, opcode: Opcode, rs1: Register, rs2: Register, imm: int):
        assert is_correct_bin_size_signed(imm, 21), "imm size in BInstruction must be 21 bits"

        super().__init__(opcode)
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = imm

    @override
    def to_binary(self) -> int:
        imm_lower = extract_bits(self.imm, 3)
        imm_upper = self.imm >> 3
        return (
            imm_upper << 14
            | register_to_binary[self.rs2] << 11
            | register_to_binary[self.rs1] << 8
            | imm_lower << 5
            | opcode_to_binary[self.opcode]
        )

    @staticmethod
    def from_binary(binary: int) -> "BInstruction":
        opcode_bin = extract_bits(binary, 5)
        opcode = binary_to_opcode[opcode_bin]

        imm_lower = extract_bits(binary >> 5, 3)
        imm_upper = extract_bits(binary >> 14, 18)
        imm_bin = (imm_upper << 3) | imm_lower
        imm = binary_to_signed_int(imm_bin, 21)

        rs1_bin = extract_bits(binary >> 8, 3)
        rs1 = binary_to_register[rs1_bin]

        rs2_bin = extract_bits(binary >> 11, 3)
        rs2 = binary_to_register[rs2_bin]

        return BInstruction(opcode, rs1, rs2, imm)

    @override
    def to_json(self) -> dict:
        return {
            "address": self.address,
            "opcode": str(self.opcode),
            "rs1": str(self.rs1),
            "rs2": str(self.rs2),
            "imm": self.imm,
        }

    def __str__(self) -> str:
        return f"{self.opcode!s} {self.rs1!s}, {self.rs2!s}, {self.imm!s}"
