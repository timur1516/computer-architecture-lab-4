from typing import override

from src.isa.instructions.instruction import Instruction
from src.isa.opcode_ import Opcode, binary_to_opcode, opcode_to_binary
from src.isa.register import Register, binary_to_register, register_to_binary
from src.isa.util.binary import binary_to_signed_int, extract_bits, is_correct_bin_size_signed


class UInstruction(Instruction):
    """U-инструкции.

    Это инструкции для загрузки больших непосредственных значений в регистры. Например `lui`.

    Структура инструкции:

    ```plaintext
    ┌───────────────────────────────────────────────────┬────────┬────────┐
    │                       31...12                     │ 11...7 │  6..0  │
    ├───────────────────────────────────────────────────┼────────┼────────┤
    │                         imm                       │   rd   │ opcode │
    └───────────────────────────────────────────────────┴────────┴────────┘
    ```
    """

    rd = None
    "код регистра назначения, 5 бит"

    u_imm = None
    "расширенное непосредственное значение, 20 бит"

    def __init__(self, opcode: Opcode, rd: Register, u_imm: int):
        assert is_correct_bin_size_signed(u_imm, 20), "u_imm size in UInstruction must be 20 bits"

        super().__init__(opcode)
        self.rd = rd
        self.u_imm = u_imm

    @override
    def to_binary(self) -> int:
        return self.u_imm << 12 | register_to_binary[self.rd] << 7 | opcode_to_binary[self.opcode]

    @staticmethod
    @override
    def from_binary(binary: int) -> "UInstruction":
        opcode_bin = extract_bits(binary, 7)
        opcode = binary_to_opcode[opcode_bin]

        rd_bin = extract_bits(binary >> 7, 5)
        rd = binary_to_register[rd_bin]

        u_imm = binary_to_signed_int(binary >> 12, 20)

        return UInstruction(opcode, rd, u_imm)

    @override
    def to_json(self) -> dict:
        return {"address": self.address, "opcode": str(self.opcode), "rd": str(self.rd), "u_imm": self.u_imm}

    def __str__(self) -> str:
        return f"{self.opcode!s} {self.rd!s}, {self.u_imm!s}"
