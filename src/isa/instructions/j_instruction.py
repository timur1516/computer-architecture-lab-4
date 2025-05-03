from typing_extensions import override

from src.isa.instructions.instruction import Instruction
from src.isa.opcode_ import Opcode, binary_to_opcode, opcode_to_binary
from src.isa.util.binary import binary_to_signed_int, extract_bits, is_correct_bin_size_signed


class JInstruction(Instruction):
    """J-инструкции.

    Это инструкции для выполнения безусловных переходов со смещением относительно счётчика команд. Например `j`.

    Структура инструкции:

    ```plaintext
    ┌────────────────────────────────────────────────────────────┬────────┐
    │                             31...7                         │  6..0  │
    ├────────────────────────────────────────────────────────────┼────────┤
    │                              imm                           │ opcode │
    └────────────────────────────────────────────────────────────┴────────┘
    ```
    """

    imm = None
    "величина смещения, 25 бит"

    def __init__(self, opcode: Opcode, imm: int):
        assert is_correct_bin_size_signed(imm, 25), "imm size in JInstruction must be 25 bits"

        super().__init__(opcode)
        self.imm = imm

    @override
    def to_binary(self) -> int:
        return self.imm << 7 | opcode_to_binary[self.opcode]

    @staticmethod
    @override
    def from_binary(binary: int) -> "JInstruction":
        opcode_bin = extract_bits(binary, 7)
        opcode = binary_to_opcode[opcode_bin]

        imm = binary_to_signed_int(binary >> 7, 25)

        return JInstruction(opcode, imm)

    @override
    def to_json(self) -> dict:
        return {"opcode": str(self.opcode), "imm": self.imm}

    def __str__(self) -> str:
        return f"{self.opcode!s} {self.imm!s}"
