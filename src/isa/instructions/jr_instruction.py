from typing import override

from src.isa.instructions.instruction import Instruction
from src.isa.opcode_ import Opcode, binary_to_opcode, opcode_to_binary
from src.isa.register import Register, binary_to_register, register_to_binary
from src.isa.util.binary import binary_to_signed_int, extract_bits, is_correct_bin_size_signed


class JRInstruction(Instruction):
    """JR-инструкции.

    Это инструкции для выполнения безусловных переходов со смещением относительно регистра. Например `jr`.

    Структура инструкции:

    ```plaintext
    ┌─────────────────────────────────────────┬─────────┬────────┬────────┐
    │                 31...17                 │ 16...12 │ 11...7 │  6..0  │
    ├─────────────────────────────────────────┼─────────┼────────┼────────┤
    │                   imm                   │   rs1   │        │ opcode │
    └─────────────────────────────────────────┴─────────┴────────┴────────┘
    ```
    """

    rs1 = None
    "код регистра относительно которого происходит смещение, 5 бит"

    imm = None
    "величина смещения, 20 бит"

    def __init__(self, opcode: Opcode, imm: int, rs1: Register):
        assert is_correct_bin_size_signed(imm, 20), "imm size in JRInstruction must be 20 bits"

        super().__init__(opcode)
        self.rs1 = rs1
        self.imm = imm

    @override
    def to_binary(self) -> int:
        imm_lower = extract_bits(self.imm, 5)
        imm_upper = self.imm >> 5
        return imm_upper << 17 | register_to_binary[self.rs1] << 12 | imm_lower << 7 | opcode_to_binary[self.opcode]

    @staticmethod
    @override
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

    @override
    def to_json(self) -> dict:
        return {"address": self.address, "opcode": str(self.opcode), "rs1": str(self.rs1), "imm": self.imm}

    def __str__(self) -> str:
        return f"{self.opcode!s} {self.rs1!s} {self.imm!s}"
