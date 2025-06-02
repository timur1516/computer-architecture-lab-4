from typing import override

from src.isa.instructions.instruction import Instruction
from src.isa.opcode_ import Opcode, binary_to_opcode, opcode_to_binary
from src.isa.register import Register, binary_to_register, register_to_binary
from src.isa.util.binary import extract_bits


class RInstruction(Instruction):
    """R-инструкции.

    Это инструкции для выполнения арифметических и логических операций над данными в регистрах. Например `add`, `sub`.

    Структура инструкции:

    ```plaintext
    ┌───────────────────────────────┬─────────┬─────────┬────────┬────────┐
    │           31...14             │ 13...11 │  10...8 │  7...5 │  4..0  │
    ├───────────────────────────────┼─────────┼─────────┼────────┼────────┤
    │                               │   rs2   │   rs1   │   rd   │ opcode │
    └───────────────────────────────┴─────────┴─────────┴────────┴────────┘
    ```
    """

    rd = None
    "код регистра назначения, 3 бита"

    rs1 = None
    "код регистра первого операнда, 3 бита"

    rs2 = None
    "код регистра второго операнда, 3 бита"

    def __init__(self, opcode: Opcode, rd: Register, rs1: Register, rs2: Register):
        super().__init__(opcode)
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2

    @override
    def to_binary(self) -> int:
        return (
            register_to_binary[self.rs2] << 11
            | register_to_binary[self.rs1] << 8
            | register_to_binary[self.rd] << 5
            | opcode_to_binary[self.opcode]
        )

    @staticmethod
    @override
    def from_binary(binary: int) -> "RInstruction":
        opcode_bin = extract_bits(binary, 5)
        opcode = binary_to_opcode[opcode_bin]

        rd_bin = extract_bits(binary >> 5, 3)
        rd = binary_to_register[rd_bin]

        rs1_bin = extract_bits(binary >> 8, 3)
        rs1 = binary_to_register[rs1_bin]

        rs2_bin = extract_bits(binary >> 11, 3)
        rs2 = binary_to_register[rs2_bin]

        return RInstruction(opcode, rd, rs1, rs2)

    @override
    def to_json(self) -> dict:
        return {
            "address": self.address,
            "opcode": str(self.opcode),
            "rd": str(self.rd),
            "rs1": str(self.rs1),
            "rs2": str(self.rs2),
        }

    def __str__(self) -> str:
        return f"{self.opcode!s} {self.rd!s}, {self.rs1!s}, {self.rs2!s}"
